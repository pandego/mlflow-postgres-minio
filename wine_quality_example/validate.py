import os

import mlflow
from dotenv import load_dotenv

load_dotenv("../.env", override=True)

# Load the logged model
model_uri = os.getenv('MODEL_REPO_DIR')

# The model is logged with an input example
pyfunc_model = mlflow.pyfunc.load_model(model_uri)
input_data = pyfunc_model.input_example

# Verify the model with the provided input data using the logged dependencies.
# For more details, refer to:
# https://mlflow.org/docs/latest/models.html#validate-models-before-deployment
mlflow.models.predict(
    model_uri=model_uri,
    input_data=input_data,
    env_manager="uv",
)
