import requests
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from google.cloud import storage

# Parameters
API_KEY = Variable.get("polygon_api_key")
BUCKET_NAME = Variable.get("bucket_name")
SYMBOL = "AAPL"


# Python functions
def polygon_to_gcs(ds):
    ds_date = datetime.strptime(ds, "%Y-%m-%d")
    previous_day = (ds_date - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{SYMBOL}/range/1/day/{previous_day}/{previous_day}?apiKey={API_KEY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.text

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"raw_polygon/polygon_{previous_day}.json")
    blob.upload_from_string(data, content_type="application/json")


# DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="polygon_api_to_gcs",
    description='Daily data pipeline to generate dims and facts for stock market analysis',
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    polygon_to_gcs = PythonOperator(
        task_id="fetch_and_upload",
        python_callable=polygon_to_gcs,
    )
