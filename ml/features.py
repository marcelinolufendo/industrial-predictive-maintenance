import pandas as pd
import numpy as np
from ml.loader import SENSORS

WINDOW = 10


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["machine_id", "cycle"])

    for sensor in SENSORS:
        grp = df.groupby("machine_id")[sensor]
        df[f"{sensor}_mean"] = grp.transform(lambda x: x.rolling(WINDOW, min_periods=1).mean())
        df[f"{sensor}_std"] = grp.transform(lambda x: x.rolling(WINDOW, min_periods=1).std().fillna(0))
        df[f"{sensor}_slope"] = grp.transform(lambda x: x.diff().rolling(WINDOW, min_periods=1).mean().fillna(0))

    return df


def get_feature_columns() -> list:
    features = []
    for sensor in SENSORS:
        features += [f"{sensor}_mean", f"{sensor}_std", f"{sensor}_slope"]
    features += ["cycle", "op1", "op2", "op3"]
    return features


def prepare_features(df: pd.DataFrame) -> tuple:
    df = add_rolling_features(df)
    feature_cols = get_feature_columns()
    X = df[feature_cols].fillna(0)
    y_failure = df["failure"]
    y_rul = df["rul"]
    return X, y_failure, y_rul, feature_cols
