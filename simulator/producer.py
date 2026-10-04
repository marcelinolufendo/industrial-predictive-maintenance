import json
import os
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from ml.loader import load_cmapss, add_rul, COLUMNS, SENSORS

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "sensor-readings")


def make_producer(retries: int = 10, delay: int = 5) -> KafkaProducer:
    for attempt in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
            )
        except NoBrokersAvailable:
            print(f"Kafka not ready, retrying in {delay}s... ({attempt + 1}/{retries})")
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to Kafka at {KAFKA_BOOTSTRAP}")


def simulate(data_dir: str = "data/raw", subset: str = "FD001", speed: float = 0.5, machine_filter: int = None):
    path = Path(data_dir) / f"train_{subset}.txt"
    df = pd.read_csv(str(path), sep=r"\s+", header=None, names=COLUMNS)
    df = add_rul(df)

    if machine_filter:
        df = df[df["machine_id"] == machine_filter]

    producer = make_producer()
    print(f"Connected to Kafka at {KAFKA_BOOTSTRAP}")
    print(f"Publishing to topic: {TOPIC}")
    print(f"Simulating {df['machine_id'].nunique()} machines | {len(df)} events\n")

    for _, row in df.iterrows():
        machine_id = f"M{int(row['machine_id']):03d}"
        message = {
            "machine_id": machine_id,
            "cycle": int(row["cycle"]),
            "op1": float(row["op1"]),
            "op2": float(row["op2"]),
            "op3": float(row["op3"]),
            **{s: float(row[s]) for s in SENSORS},
            "timestamp": int(time.time() * 1000),
        }

        producer.send(TOPIC, key=machine_id, value=message)
        print(f"Machine {machine_id} | Cycle {int(row['cycle']):4d} → published")
        time.sleep(speed)

    producer.flush()
    print("\nSimulation complete.")


if __name__ == "__main__":
    simulate(speed=0.2, machine_filter=1)
