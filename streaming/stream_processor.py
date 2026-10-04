"""
Spark Structured Streaming Pipeline
  Kafka (sensor-readings) → Bronze (raw) → Silver (features) → Gold (predictions)
"""
import os
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import (
    DoubleType, IntegerType, LongType, StringType, StructField, StructType,
)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
MLFLOW_URI      = os.getenv("MLFLOW_TRACKING_URI",    "http://mlflow:5000")
TOPIC           = os.getenv("KAFKA_TOPIC",             "sensor-readings")
DELTA_BASE      = os.getenv("DELTA_BASE",              "/opt/spark/delta")
CHECKPOINT_BASE = os.getenv("CHECKPOINT_BASE",         "/opt/spark/checkpoints")

SENSORS = ["s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"]
WINDOW  = 10

MSG_SCHEMA = StructType([
    StructField("machine_id", StringType()),
    StructField("cycle",      IntegerType()),
    StructField("op1",        DoubleType()),
    StructField("op2",        DoubleType()),
    StructField("op3",        DoubleType()),
    *[StructField(s, DoubleType()) for s in SENSORS],
    StructField("timestamp",  LongType()),
])


def _slope(x: np.ndarray) -> float:
    if len(x) < 2:
        return 0.0
    t = np.arange(len(x), dtype=float)
    return float(np.polyfit(t, x, 1)[0])


def add_rolling_features(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf = pdf.sort_values(["machine_id", "cycle"]).copy()
    for s in SENSORS:
        grp = pdf.groupby("machine_id")[s]
        roll = grp.rolling(WINDOW, min_periods=1)
        pdf[f"{s}_mean"]  = roll.mean().reset_index(level=0, drop=True)
        pdf[f"{s}_std"]   = roll.std().fillna(0).reset_index(level=0, drop=True)
        pdf[f"{s}_slope"] = (
            grp.rolling(WINDOW, min_periods=2)
            .apply(_slope, raw=True)
            .fillna(0)
            .reset_index(level=0, drop=True)
        )
    return pdf


def _decide(anomaly_score: float, failure_prob: float, rul: float) -> str:
    if anomaly_score >= 0.80 or failure_prob >= 0.70 or rul <= 20:
        return "CRITICAL"
    if anomaly_score >= 0.60 or failure_prob >= 0.40 or rul <= 50:
        return "WARNING"
    return "NORMAL"


_models: dict = {}


def _load_models():
    if _models:
        return
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
    mlflow.set_tracking_uri(MLFLOW_URI)
    _models["anomaly"]  = mlflow.sklearn.load_model("models:/anomaly-detector/latest")
    _models["failure"]  = mlflow.xgboost.load_model("models:/failure-predictor/latest")
    _models["rul"]      = mlflow.xgboost.load_model("models:/rul-predictor/latest")
    print("Models loaded in streaming job.")


def process_batch(batch_df, batch_id: int):
    if batch_df.isEmpty():
        return

    spark = SparkSession.getActiveSession()

    # ── Bronze ──────────────────────────────────────────────────────────────
    (batch_df.withColumn("ingested_at", current_timestamp())
     .write.format("delta").mode("append")
     .save(f"{DELTA_BASE}/bronze"))

    # ── Silver (feature engineering) ────────────────────────────────────────
    pdf = batch_df.toPandas()
    pdf = add_rolling_features(pdf)
    pdf["processed_at"] = pd.Timestamp.utcnow()

    (spark.createDataFrame(pdf)
     .write.format("delta").mode("append")
     .save(f"{DELTA_BASE}/silver"))

    # ── Gold (inference) ────────────────────────────────────────────────────
    try:
        _load_models()
        feature_cols = [f"{s}_{stat}" for s in SENSORS for stat in ("mean", "std", "slope")]
        X = pdf[feature_cols].fillna(0).values

        scores = _models["anomaly"].decision_function(X)
        lo, hi = scores.min(), scores.max()
        norm   = (scores - lo) / (hi - lo + 1e-9)

        pdf["anomaly_score"]        = norm
        pdf["failure_probability"]  = _models["failure"].predict_proba(X)[:, 1]
        pdf["rul"]                  = _models["rul"].predict(X)
        pdf["status"]               = pdf.apply(
            lambda r: _decide(r.anomaly_score, r.failure_probability, r.rul), axis=1
        )
        pdf["predicted_at"] = pd.Timestamp.utcnow()

        gold_cols = ["machine_id", "cycle", "timestamp",
                     "anomaly_score", "failure_probability", "rul", "status", "predicted_at"]
        (spark.createDataFrame(pdf[gold_cols])
         .write.format("delta").mode("append")
         .save(f"{DELTA_BASE}/gold"))

        print(f"[batch {batch_id}] {len(pdf)} rows → Gold ✓")
    except Exception as exc:
        print(f"[batch {batch_id}] inference skipped — {exc}")


def main():
    spark = (SparkSession.builder
             .appName("PredictiveMaintenance")
             .config("spark.sql.extensions",
                     "io.delta.sql.DeltaSparkSessionExtension")
             .config("spark.sql.catalog.spark_catalog",
                     "org.apache.spark.sql.delta.catalog.DeltaCatalog")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")

    raw = (spark.readStream
           .format("kafka")
           .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
           .option("subscribe", TOPIC)
           .option("startingOffsets", "latest")
           .load())

    parsed = (raw
              .select(from_json(col("value").cast("string"), MSG_SCHEMA).alias("d"))
              .select("d.*"))

    query = (parsed.writeStream
             .foreachBatch(process_batch)
             .option("checkpointLocation", f"{CHECKPOINT_BASE}/stream")
             .trigger(processingTime="10 seconds")
             .start())

    print(f"Streaming from Kafka topic '{TOPIC}' …")
    query.awaitTermination()


if __name__ == "__main__":
    main()
