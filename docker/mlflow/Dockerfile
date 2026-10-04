FROM ghcr.io/mlflow/mlflow:v3.16.1
RUN pip install --no-cache-dir psycopg2-binary==2.9.13
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
