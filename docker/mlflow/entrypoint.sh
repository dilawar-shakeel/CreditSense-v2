#!/bin/sh
# Build the backend URI with the password URL-encoded, so special characters
# such as @ : / # in POSTGRES_PASSWORD cannot break the connection string.
set -e
PW=$(python -c "import os, urllib.parse as u; print(u.quote(os.environ['POSTGRES_PASSWORD'], safe=''))")
exec mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri "postgresql://${POSTGRES_USER}:${PW}@postgres:5432/${MLFLOW_DB:-mlflow}" \
  --artifacts-destination /mlflow/artifacts \
  --serve-artifacts
