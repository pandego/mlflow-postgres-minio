"""
Tests for the MCP MLflow server functions.
"""

import json
from typing import List

import pytest
from respx import MockRouter

# Assuming server.py is in a package mcp_server_mlflow that's in PYTHONPATH
# If not, adjust the import path accordingly.
from mcp_server_mlflow.server import (
    MLFLOW_URL,  # Import MLFLOW_URL for mocking
    format_predictions,
    get_input_example,
    predict_wine_quality,
)


def test_get_input_example():
    """Test the get_input_example function."""
    # Arrange
    data = None

    # Act
    result = get_input_example()

    # Assert
    assert isinstance(result, str), "Output should be a string"
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        pytest.fail("Output should be valid JSON")

    assert "columns" in data, "JSON should have a 'columns' key"
    assert "data" in data, "JSON should have a 'data' key"
    assert isinstance(data["columns"], list), "'columns' should be a list"
    assert isinstance(data["data"], list), "'data' should be a list"
    assert len(data["data"]) > 0, "Example data should not be empty"
    assert len(data["data"][0]) == len(data["columns"]), \
        "Number of items in a data row should match number of columns"


def test_format_predictions_empty():
    """Test format_predictions with an empty list."""
    # Arrange
    predictions: List[float] = []

    # Act
    formatted_text = format_predictions(predictions)

    # Assert
    expected_text = "## 🍷 Predicted Wine Quality Scores\n\n"
    assert formatted_text == expected_text


def test_format_predictions_single():
    """Test format_predictions with a single prediction."""
    # Arrange
    predictions: List[float] = [7.85]

    # Act
    formatted_text = format_predictions(predictions)

    # Assert
    expected_text = "## 🍷 Predicted Wine Quality Scores\n\n- Sample 1: **7.85/10**"
    assert formatted_text == expected_text


def test_format_predictions_multiple():
    """Test format_predictions with multiple predictions."""
    # Arrange
    predictions: List[float] = [7.85, 5.2, 9.999]

    # Act
    formatted_text = format_predictions(predictions)

    # Assert
    expected_text = (
        "## 🍷 Predicted Wine Quality Scores\n\n"
        "- Sample 1: **7.85/10**\n"
        "- Sample 2: **5.20/10**\n"
        "- Sample 3: **10.00/10**"
    )
    assert formatted_text == expected_text


@pytest.mark.asyncio
async def test_predict_wine_quality_success(respx_mock: MockRouter):
    """Test predict_wine_quality successfully calls MLflow and returns predictions."""
    # Arrange
    input_data = [[7.4, 0.7, 0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4]]
    columns = [
        "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
        "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density",
        "pH", "sulphates", "alcohol"
    ]
    expected_predictions = [6.5]

    # Mock the httpx call to MLflow
    respx_mock.post(MLFLOW_URL).respond(
        status_code=200,
        json={"predictions": expected_predictions}
    )

    # Act
    actual_predictions = await predict_wine_quality(inputs=input_data, columns=columns)

    # Assert
    assert actual_predictions == expected_predictions
    assert len(respx_mock.calls) == 1
    called_request = respx_mock.calls[0].request
    assert called_request.url == MLFLOW_URL
    request_payload = json.loads(called_request.content)
    assert request_payload["dataframe_split"]["data"] == input_data
    assert request_payload["dataframe_split"]["columns"] == columns


@pytest.mark.asyncio
async def test_predict_wine_quality_mlflow_error(respx_mock: MockRouter):
    """Test predict_wine_quality when MLflow returns an error."""
    # Arrange
    input_data = [[7.4, 0.7, 0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4]]
    columns = [
        "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
        "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density",
        "pH", "sulphates", "alcohol"
    ]

    # Mock the httpx call to MLflow to return an error
    respx_mock.post(MLFLOW_URL).respond(status_code=500, json={"error": "MLflow internal error"})

    # Act & Assert
    # The function predict_wine_quality currently directly returns resp.json()["predictions"].
    # If MLflow returns an error (e.g., 500) and the JSON doesn't have a "predictions" key,
    # this will raise a KeyError. If the JSON is malformed, it will raise a JSONDecodeError.
    # We test for KeyError here, assuming the 500 error response JSON doesn't contain 'predictions'.
    # If the server.py function were to handle errors more gracefully (e.g., raise custom exceptions),
    # this test would change to expect that custom exception.
    with pytest.raises(KeyError): # Or potentially httpx.HTTPStatusError if resp.raise_for_status() was used
        await predict_wine_quality(inputs=input_data, columns=columns)

    assert len(respx_mock.calls) == 1
