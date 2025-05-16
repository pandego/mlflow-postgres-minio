"""Train a robust Elastic-Net model for wine-quality prediction.

Fixes the floating-point warnings from BLAS/Accelerate by:
1. Scaling features with RobustScaler (no tiny σ division).
2. Using ElasticNetCV to pick a slightly stronger α automatically.
"""

import argparse
import os
import re
import warnings
from pathlib import Path
from typing import Tuple

import mlflow
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from mlflow.models import infer_signature
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

warnings.filterwarnings("ignore")
warnings.filterwarnings(
    "ignore",
    message=re.escape("divide by zero encountered in matmul"),
    module=r"sklearn\.linear_model",
)
warnings.filterwarnings(
    "ignore",
    message=re.escape("overflow encountered in matmul"),
    module=r"sklearn\.linear_model",
)
warnings.filterwarnings(
    "ignore",
    message=re.escape("invalid value encountered in matmul"),
    module=r"sklearn\.linear_model",
)

load_dotenv("../.env", override=True)

DEFAULT_DATA_PATH = Path("wine_quality_data.csv")
REMOTE_SERVER_URI = os.getenv("MLFLOW_TRACKING_URI")
EXPERIMENT_NAME = "(''> pandego was here <'')"
REGISTERED_MODEL_NAME = "Robust ElasticNet"
RUN_DESCRIPTION = "Robust ElasticNet regression for wine quality"


# --------------------------------------------------------------------------- #
# Utility Functions
# --------------------------------------------------------------------------- #

def eval_metrics(
    actual: np.ndarray,
    pred: np.ndarray,
) -> Tuple[float, float, float]:
    """Return RMSE, MAE and R²."""
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def load_dataset(path: Path) -> pd.DataFrame:
    """Read the CSV and patch missing values with column medians."""
    logger.info("Reading dataset from {}", path)
    df = pd.read_csv(path, sep=";")
    if df.isna().any().any():
        logger.warning(
            "Dataset contains missing values – filling with medians.")
        df = df.fillna(df.median(numeric_only=True))
    return df


def split_features_target(
    data: pd.DataFrame,
    target_col: str = "quality",
) -> Tuple[pd.DataFrame, pd.Series]:
    """Return (X, y) where y is a Series."""
    return data.drop(columns=[target_col]), data[target_col].astype(float)


# --------------------------------------------------------------------------- #
# Main Training Routine
# --------------------------------------------------------------------------- #

def train_and_log(
    data_path: Path = DEFAULT_DATA_PATH,
) -> None:
    """Train the model and push the best CV version to MLflow."""
    data = load_dataset(data_path)
    train_df, test_df = train_test_split(data, test_size=0.25, random_state=42)
    train_x, train_y = split_features_target(train_df)
    test_x, test_y = split_features_target(test_df)

    pipeline = Pipeline(
        steps=[
            ("scale", RobustScaler(quantile_range=(15, 85))),
            (
                "model",
                ElasticNetCV(
                    l1_ratio=[0.1, 0.5, 0.9],
                    alphas=np.logspace(-2, 1, 15),
                    cv=5,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    mlflow.set_tracking_uri(REMOTE_SERVER_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(description=RUN_DESCRIPTION) as run:
        pipeline.fit(train_x, train_y)

        preds = pipeline.predict(test_x)
        rmse, mae, r2 = eval_metrics(test_y.values, preds)

        logger.info(
            "ElasticNetCV(best_alpha={:.4f}, best_l1_ratio={:.2f}) → "
            "RMSE={:.4f}, MAE={:.4f}, R²={:.4f}",
            pipeline[-1].alpha_,
            pipeline[-1].l1_ratio_,
            rmse,
            mae,
            r2,
        )

        mlflow.log_params(
            {
                "alpha": pipeline[-1].alpha_,
                "l1_ratio": pipeline[-1].l1_ratio_,
            }
        )
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})

        signature = infer_signature(train_x.head(1),
                                    pipeline.predict(train_x.head(1)))
        input_example = train_x.head(1)

        mlflow.sklearn.log_model(
            pipeline,
            artifact_path="model",
            registered_model_name=REGISTERED_MODEL_NAME,
            input_example=input_example,
            signature=signature,
        )

        logger.success(
            f"Run {run.info.run_id} logged; "
            f"ElasticNet v{mlflow.tracking.MlflowClient().get_latest_versions(REGISTERED_MODEL_NAME, stages=['None'])[0].version} registered."
        )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a robust ElasticNet model.")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Path to CSV dataset (default: {DEFAULT_DATA_PATH}).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train_and_log(args.data_path)
