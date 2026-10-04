#!/bin/sh
# Runs once on first start: a separate database for MLflow's backend store.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -c "CREATE DATABASE ${MLFLOW_DB:-mlflow}"
