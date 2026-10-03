import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score,
)
from xgboost import XGBClassifier, XGBRegressor

from ml.loader import load_dataset
from ml.features import prepare_features


def train(data_dir: str = "data/raw", subset: str = "FD001"):
    print(f"Loading dataset {subset}...")
    df = load_dataset(data_dir, subset)
    X, y_failure, y_rul, feature_cols = prepare_features(df)

    X_train, X_test, yf_train, yf_test, yr_train, yr_test = train_test_split(
        X, y_failure, y_rul, test_size=0.2, random_state=42
    )

    mlflow.set_experiment("predictive-maintenance")

    # --- Anomaly Detection ---
    print("Training Isolation Forest...")
    with mlflow.start_run(run_name="isolation-forest"):
        iso = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)
        iso.fit(X_train)
        mlflow.log_param("contamination", 0.1)
        mlflow.sklearn.log_model(
            iso, "isolation-forest",
            registered_model_name="anomaly-detector",
            skops_trusted_types=["sklearn.tree._tree.Tree", "sklearn.ensemble._iforest.IsolationForest"],
        )
        print("  Isolation Forest logged.")

    # --- Failure Prediction ---
    print("Training XGBoost Classifier...")
    with mlflow.start_run(run_name="xgboost-failure"):
        scale_pos = int((yf_train == 0).sum() / (yf_train == 1).sum())
        clf = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric="auc",
        )
        clf.fit(X_train, yf_train, eval_set=[(X_test, yf_test)], verbose=False)

        preds = clf.predict(X_test)
        proba = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(yf_test, proba)

        mlflow.log_param("n_estimators", 200)
        mlflow.log_param("max_depth", 6)
        mlflow.log_metric("roc_auc", round(auc, 4))
        mlflow.xgboost.log_model(
            clf, "xgboost-failure",
            registered_model_name="failure-predictor",
        )

        print(f"  ROC-AUC: {auc:.4f}")
        print(classification_report(yf_test, preds))

    # --- RUL Prediction ---
    print("Training XGBoost Regressor (RUL)...")
    with mlflow.start_run(run_name="xgboost-rul"):
        reg = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42)
        reg.fit(X_train, yr_train, eval_set=[(X_test, yr_test)], verbose=False)

        rul_preds = reg.predict(X_test)
        mae = mean_absolute_error(yr_test, rul_preds)
        rmse = np.sqrt(mean_squared_error(yr_test, rul_preds))
        r2 = r2_score(yr_test, rul_preds)

        mlflow.log_metric("mae", round(mae, 2))
        mlflow.log_metric("rmse", round(rmse, 2))
        mlflow.log_metric("r2", round(r2, 4))
        mlflow.xgboost.log_model(
            reg, "xgboost-rul",
            registered_model_name="rul-predictor",
        )

        print(f"  MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.4f}")

    print("\nTraining complete.")


if __name__ == "__main__":
    train()
