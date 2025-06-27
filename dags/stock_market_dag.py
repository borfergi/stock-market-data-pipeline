import requests
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator


from google.cloud import storage


# Parameters
PROJECT_ID = os.environ.get("PROJECT_ID")
SERVICE_ACCOUNT = os.environ.get("SERVICE_ACCOUNT")
REGION = os.environ.get("REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
PYTHON_FILE_URI = f"gs://{BUCKET_NAME}/scripts/transform_stock_data_pipeline.py"
API_KEY = os.environ.get("POLYGON_API_KEY")
SYMBOL = "AAPL"


# Python functions
def polygon_to_gcs(ds):
    # Obtain previous day
    ds_date = datetime.strptime(ds, "%Y-%m-%d")
    previous_day = (ds_date - timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"https://api.polygon.io/v2/aggs/ticker/{SYMBOL}/range/1/day/{previous_day}/{previous_day}?apiKey={API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.text

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"raw/polygon/polygon_{previous_day}.json")
    blob.upload_from_string(data, content_type="application/json")


# DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="stock_market_dag",
    description='Daily data pipeline to generate dims and facts for stock market analysis',
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    fetch_and_upload_raw = PythonOperator(
        task_id="fetch_and_upload",
        python_callable=polygon_to_gcs,
    )

    # Wait for the files to be uploaded into raw/ERP in the GCS bucket
    wait_for_erp_companies_file = GCSObjectExistenceSensor(
        task_id="wait_for_erp_companies_file",
        bucket=BUCKET_NAME,
        object="raw/ERP/erp_companies.csv",
        timeout=600,  # 10 minutes
        poke_interval=30,
    )

    # Prepare Dataproc serverless and execute the transformation job
    run_dataproc_job = DataprocCreateBatchOperator(
        task_id="run_transform_stock_data_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        batch_id="dataproc-batch-{{ ds_nodash }}",
        batch={
            "pyspark_batch": {
                "main_python_file_uri": PYTHON_FILE_URI,
                "args": [
                    "--bucket", BUCKET_NAME
                ]
            },
            "environment_config": {
                "execution_config": {
                    "service_account": SERVICE_ACCOUNT,
                }
            }
        }
    )

[fetch_and_upload_raw, wait_for_erp_companies_file] >> run_dataproc_job
