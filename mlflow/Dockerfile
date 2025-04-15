FROM python:3.11-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install mlflow[extras] psycopg2-binary boto3 cryptography pymysql

EXPOSE ${MLFLOW_PORT_SERVICE}
