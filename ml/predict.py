import mlflow.sklearn
import numpy as np
import pandas as pd
from ml.features import get_feature_columns


def load_models(tracking_uri: str = "./mlruns"):
    mlflow.set_tracking_uri(tracking_uri)
    anomaly_model = mlflow.sklearn.load_model("models:/anomaly-detector/latest")
    failure_model = mlflow.sklearn.load_model("models:/failure-predictor/latest")
    rul_model = mlflow.sklearn.load_model("models:/rul-predictor/latest")
    return anomaly_model, failure_model, rul_model


def predict(features: dict, anomaly_model, failure_model, rul_model) -> dict:
    feature_cols = get_feature_columns()
    row = pd.DataFrame([features])[feature_cols].fillna(0)

    anomaly_score = -anomaly_model.score_samples(row)[0]
    anomaly_score = float(np.clip((anomaly_score - 0.3) / 0.4, 0, 1))

    failure_probability = float(failure_model.predict_proba(row)[0][1])
    rul = max(0, int(rul_model.predict(row)[0]))

    return {
        "anomaly_score": round(anomaly_score, 4),
        "failure_probability": round(failure_probability, 4),
        "rul": rul,
    }


import mlflow
