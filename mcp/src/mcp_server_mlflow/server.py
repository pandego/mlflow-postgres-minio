import json
import os
from typing import List

import httpx
from mcp.server.fastmcp import FastMCP

MLFLOW_URL = os.getenv("MLFLOW_URL", "http://localhost:1234/invocations")

mcp = FastMCP(
    name="Wine Quality Server",
    stateless_http=True,
    host="0.0.0.0",
    port=8000,
    # json_response=True
)


@mcp.tool(
    name="predict_wine_quality",
    description="Predict wine quality using MLflow API"
)
async def predict_wine_quality(
    inputs: List[List[float]],
    columns: List[str]
) -> List[float]:
    """
    Predict wine quality for one or more samples using MLflow

    Args:
        inputs: List of feature rows (each row is a list of floats)
        columns: List of feature names (column names)

    Returns:
        List of predicted quality scores

    """
    payload = {
        "dataframe_split": {
            "data": inputs,
            "columns": columns
        }
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url=MLFLOW_URL,
            json=payload
        )
        return resp.json()["predictions"]


@mcp.resource(
    uri="wine://example",
    name="wine_quality_example",
    description="Example wine quality inputs and outputs",
    mime_type="application/json"
)
def get_input_example() -> str:
    """
    Return example inputs for wine quality prediction (columns and data)
    """
    example = {
        "columns": [
            "fixed acidity",
            "volatile acidity",
            "citric acid",
            "residual sugar",
            "chlorides",
            "free sulfur dioxide",
            "total sulfur dioxide",
            "density",
            "pH",
            "sulphates",
            "alcohol"
        ],
        "data": [
            [7.4, 0.7, 0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4],
            [7.8, 0.88, 0, 2.6, 0.098, 25, 67, 0.9968, 3.2, 0.68, 9.8]
        ]
    }
    return json.dumps(example, indent=2)


@mcp.prompt(
    name="format_predictions",
    description="Format wine quality predictions for chatbot"
)
def format_predictions(predictions: List[float]) -> str:
    """
    Format wine quality predictions for chatbot.

    Args:
        predictions: List of predicted quality scores

    Returns:
        Formatted text

    """
    formatted = "\n".join(
        f"- Sample {i + 1}: **{score:.2f}/10**"
        for i, score in enumerate(predictions)
    )
    return f"## 🍷 Predicted Wine Quality Scores\n\n{formatted}"
