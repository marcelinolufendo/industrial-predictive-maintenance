import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.schemas import PredictionOutput, SensorInput
from decision_engine.engine import decide
from ml.predict import load_models, predict

load_dotenv()

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
    anomaly, failure, rul = load_models(tracking_uri)
    models["anomaly"] = anomaly
    models["failure"] = failure
    models["rul"] = rul
    print("Models loaded.")
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


@app.get("/machines/{machine_id}/health")
def machine_health(machine_id: str):
    return {"machine_id": machine_id, "message": "Use POST /predict with sensor data"}
