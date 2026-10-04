#!/bin/bash
set -e

MLFLOW_URL="${MLFLOW_TRACKING_URI:-http://mlflow:5000}"

echo "Waiting for MLflow at $MLFLOW_URL..."
until curl -sf "$MLFLOW_URL/health" > /dev/null 2>&1; do
    sleep 3
done
echo "MLflow ready."

python - <<'EOF'
import os, sys
import mlflow

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(tracking_uri)
client = mlflow.tracking.MlflowClient()

try:
    client.get_registered_model("failure-predictor")
    print("Models already in MLflow. Skipping training.")
except Exception:
    print("No models found. Starting training (this takes ~2 minutes)...")
    import subprocess
    result = subprocess.run([sys.executable, "ml/train.py"], check=True)
    print("Training complete.")
EOF

echo "Starting API..."
exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
