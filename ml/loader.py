import pandas as pd
import numpy as np
from pathlib import Path

COLUMNS = [
    "machine_id", "cycle",
    "op1", "op2", "op3",
    "s1", "s2", "s3", "s4", "s5", "s6", "s7",
    "s8", "s9", "s10", "s11", "s12", "s13", "s14",
    "s15", "s16", "s17", "s18", "s19", "s20", "s21",
]

SENSORS = ["s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"]


def load_cmapss(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS)
    return df


def add_rul(df: pd.DataFrame) -> pd.DataFrame:
    max_cycle = df.groupby("machine_id")["cycle"].max().reset_index()
    max_cycle.columns = ["machine_id", "max_cycle"]
    df = df.merge(max_cycle, on="machine_id")
    df["rul"] = df["max_cycle"] - df["cycle"]
    df["failure"] = (df["rul"] <= 30).astype(int)
    df.drop(columns=["max_cycle"], inplace=True)
    return df


def load_dataset(data_dir: str = "data/raw", subset: str = "FD001") -> pd.DataFrame:
    path = Path(data_dir) / f"train_{subset}.txt"
    df = load_cmapss(str(path))
    df = add_rul(df)
    return df
