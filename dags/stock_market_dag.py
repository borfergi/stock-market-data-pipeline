from datetime import datetime, timedelta
import os
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

from google.cloud import storage


# Parameters
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
SERVICE_ACCOUNT = os.environ.get("SERVICE_ACCOUNT")
REGION = os.environ.get("REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
PYTHON_FILE_URI = f"gs://{BUCKET_NAME}/scripts/transform_stock_data_pipeline.py"
DATASET_ID = os.environ.get("DATASET_ID")

API_KEY = os.environ.get("POLYGON_API_KEY")

if not all([PROJECT_ID, SERVICE_ACCOUNT, REGION, BUCKET_NAME, API_KEY]):
    raise ValueError("Missing one or more required environment variables.")

SYMBOLS = ["META", "AAPL", "AMZN", "NFLX", "GOOGL"]


# Python functions
def polygon_to_gcs(ds, **kwargs):
    # Obtain previous day
    previous_day = (datetime.strptime(ds, "%Y-%m-%d") -
                    timedelta(days=1)).strftime("%Y-%m-%d")

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    for symbol in SYMBOLS:
        try:
            url = (
                f"https://api.polygon.io/v1/open-close/{symbol}/{previous_day}?adjusted=true&apiKey={API_KEY}"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.text

            blob = bucket.blob(
                f"raw/polygon/polygon_{symbol}_{previous_day}.json")
            blob.upload_from_string(data, content_type="application/json")
        except Exception as e:
            print(f"Error processing symbol {symbol}: {e}")


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
                    "--bucket", BUCKET_NAME,
                    "--previous_day", "{{ macros.ds_add(ds, -1) }}"
                ]
            },
            "environment_config": {
                "execution_config": {
                    "service_account": SERVICE_ACCOUNT,
                }
            }
        }
    )

    # Add stock price data to BigQuery with append
    load_fact_stock_price = GCSToBigQueryOperator(
        task_id="load_fact_stock_price",
        bucket=BUCKET_NAME,
        source_objects=["processed/fact_stock_price.parquet"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.fact_stock_price",
        source_format="PARQUET",
        write_disposition="WRITE_APPEND",
        location=REGION,
    )
   # Load company data to BigQuery with truncate
    load_dim_company = GCSToBigQueryOperator(
        task_id="load_dim_company",
        bucket=BUCKET_NAME,
        source_objects=["processed/dim_company.parquet"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.dim_company",
        source_format="PARQUET",
        write_disposition="WRITE_TRUNCATE",
        location=REGION,
    )
   # Load exchange data to BigQuery with truncate
    load_dim_exchange = GCSToBigQueryOperator(
        task_id="load_dim_exchange",
        bucket=BUCKET_NAME,
        source_objects=["processed/dim_exchange.parquet"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.dim_exchange",
        source_format="PARQUET",
        write_disposition="WRITE_TRUNCATE",
        location=REGION,
    )
   # Load dates data to BigQuery with truncate
    load_dim_date = GCSToBigQueryOperator(
        task_id="load_dim_date",
        bucket=BUCKET_NAME,
        source_objects=["dates/dates.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.dim_date",
        source_format="CSV",
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=1,  # Do not include the header
        location=REGION,
    )

[fetch_and_upload_raw, wait_for_erp_companies_file] >> run_dataproc_job >> [
    load_fact_stock_price, load_dim_company, load_dim_exchange, load_dim_date]
