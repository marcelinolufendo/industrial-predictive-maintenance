import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.schemas import PredictionOutput, SensorInput, StreamingPrediction
from decision_engine.engine import decide
from ml.predict import load_models, predict

load_dotenv()

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
    try:
        anomaly, failure, rul = load_models(tracking_uri)
        models["anomaly"] = anomaly
        models["failure"] = failure
        models["rul"] = rul
        print("Models loaded.")
    except Exception as e:
        print(f"Warning: models not loaded — {e}")
    yield
    models.clear()


app = FastAPI(title="Predictive Maintenance API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": len(models) == 3}


@app.post("/predict", response_model=PredictionOutput)
def predict_endpoint(payload: SensorInput):
    if not models:
        raise HTTPException(status_code=503, detail="Models not loaded")

    features = payload.model_dump()
    machine_id = features.pop("machine_id")

    result = predict(features, models["anomaly"], models["failure"], models["rul"])
    decision = decide(result["anomaly_score"], result["failure_probability"], result["rul"])

    return PredictionOutput(
        machine_id=machine_id,
        anomaly_score=result["anomaly_score"],
        failure_probability=result["failure_probability"],
        rul=result["rul"],
        status=decision.status,
        reasons=decision.reasons,
    )


@app.get("/machines/{machine_id}/latest", response_model=StreamingPrediction)
def latest_prediction(machine_id: str):
    delta_base = os.getenv("DELTA_BASE", "/opt/spark/delta")
    gold_path = f"{delta_base}/gold"
    try:
        from deltalake import DeltaTable
        dt = DeltaTable(gold_path)
        df = dt.to_pandas()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Gold table not available: {e}")

    machine_df = df[df["machine_id"] == machine_id]
    if machine_df.empty:
        raise HTTPException(status_code=404, detail=f"No predictions found for {machine_id}")

    row = machine_df.sort_values("predicted_at").iloc[-1]
    return StreamingPrediction(
        machine_id=str(row["machine_id"]),
        cycle=int(row["cycle"]),
        anomaly_score=float(row["anomaly_score"]),
        failure_probability=float(row["failure_probability"]),
        rul=float(row["rul"]),
        status=str(row["status"]),
        predicted_at=str(row["predicted_at"]),
    )
