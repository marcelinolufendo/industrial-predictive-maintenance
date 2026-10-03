import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path

from ml.loader import load_cmapss, add_rul, COLUMNS, SENSORS
from ml.features import add_rolling_features, get_feature_columns

API_URL = "http://localhost:8000/predict"


def simulate(data_dir: str = "data/raw", subset: str = "FD001", speed: float = 0.5, machine_filter: int = None):
    path = Path(data_dir) / f"train_{subset}.txt"
    df = pd.read_csv(str(path), sep=r"\s+", header=None, names=COLUMNS)
    df = add_rul(df)
    df = add_rolling_features(df)

    if machine_filter:
        df = df[df["machine_id"] == machine_filter]

    feature_cols = get_feature_columns()
    print(f"Simulating {df['machine_id'].nunique()} machines | {len(df)} events\n")

    for _, row in df.iterrows():
        payload = {"machine_id": f"M{int(row['machine_id']):03d}"}
        payload.update({col: float(row[col]) if col in row.index else 0.0 for col in feature_cols})
        payload["cycle"] = float(row["cycle"])
        payload["op1"] = float(row["op1"])
        payload["op2"] = float(row["op2"])
        payload["op3"] = float(row["op3"])

        try:
            resp = requests.post(API_URL, json=payload, timeout=5)
            result = resp.json()
            status = result.get("status", "?")
            fp = result.get("failure_probability", 0)
            rul = result.get("rul", "?")
            print(
                f"Machine {result['machine_id']} | Cycle {int(row['cycle']):4d} | "
                f"Status: {status:8s} | Failure Prob: {fp:.2%} | RUL: {rul}"
            )
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(speed)


if __name__ == "__main__":
    simulate(speed=0.2, machine_filter=1)
