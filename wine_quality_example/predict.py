"""Predict wine quality with an MLflow‑logged model.

This revision silences the MLflow “extra inputs” warning by automatically
dropping any column named ``quality`` (the target) from the inference data.
"""

import argparse
import os
import sys
import warnings
from pathlib import Path
from typing import Any

import mlflow
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

warnings.filterwarnings("ignore")

load_dotenv("../.env", override=True)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY‑MM‑DD HH:mm:ss} | {level} | {message}",
    level="INFO",
)

np.seterr(divide='ignore')


# --------------------------------------------------------------------------- #
# Utility Functions
# --------------------------------------------------------------------------- #

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the target column if present to match the model signature.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input data.

    Returns
    -------
    pd.DataFrame
        DataFrame without the ``quality`` column.
    """
    if "quality" in df.columns:
        logger.debug("Dropping column 'quality' from inference data.")
        return df.drop(columns=["quality"])
    return df


def load_data(path: Path) -> pd.DataFrame:
    """Load data from CSV or JSON and drop the target column.

    Parameters
    ----------
    path : Path
        Path to a ``.csv`` or ``.json`` file.

    Returns
    -------
    pd.DataFrame
        Feature matrix ready for prediction.

    Raises
    ------
    ValueError
        If the file extension is unsupported.
    """
    logger.info("Loading data from {}", path)

    if path.suffix == ".csv":
        df = pd.read_csv(path, sep=";")
    elif path.suffix == ".json":
        df = pd.read_json(path, orient="records")
    else:
        raise ValueError("Unsupported file type (use .csv or .json).")

    return _clean(df)


# --------------------------------------------------------------------------- #
# Main Inference Function
# --------------------------------------------------------------------------- #

def predict(model_uri: str, features: pd.DataFrame) -> Any:
    """Generate predictions with the specified MLflow model.

    Parameters
    ----------
    model_uri : str
        MLflow model URI or local path.
    features : pd.DataFrame
        Input feature matrix.

    Returns
    -------
    Any
        Model predictions.
    """
    logger.info(f"Loading model: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)

    logger.info("Generating predictions...")
    return model.predict(features)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def parse_args() -> argparse.Namespace:
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(description="Run model inference.")
    parser.add_argument(
        "-i",
        "--input-file",
        required=True,
        type=Path,
        help="Path to input .csv or .json file.",
    )
    parser.add_argument(
        "-m",
        "--model-uri",
        default=os.getenv("MODEL_REPO_DIR"),
        help="MLflow model URI (defaults to $MODEL_REPO_DIR).",
    )
    return parser.parse_args()


def main() -> None:
    """Entry‑point for the script."""
    args = parse_args()

    if args.model_uri is None:
        logger.error(
            "Model URI not provided (use --model-uri or $MODEL_REPO_DIR).")
        sys.exit(1)

    input_df = load_data(args.input_file)
    predictions = predict(args.model_uri, input_df)

    logger.info("Predictions:\n{}", predictions)


if __name__ == "__main__":
    main()
