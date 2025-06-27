import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp

# Iniciate Spark Session
spark = SparkSession.builder \
    .appName('transform-stock-market-data-pipeline') \
    .getOrCreate()


# Parameters
# Parse bucket_name arg
parser_args = argparse.ArgumentParser().add_argument(
    "--bucket", required=True).parse_args()

BUCKET_NAME = parser_args.bucket

# Take the lastest polygon file as input
INPUT_API_FILE = f"gs://{BUCKET_NAME}/raw/polygon/.json"
INPUT_ERP_FILE = f"gs://{BUCKET_NAME}/raw/ERP/erp_companies.csv"
OUTPUT_FACT_STOCK_PRICE = f"gs://{BUCKET_NAME}/processed/fact_stock_price.parquet"
OUTPUT_DIM_COMPANY = f"gs://{BUCKET_NAME}/processed/dim_company.parquet"
OUTPUT_DIM_EXCHANGE = f"gs://{BUCKET_NAME}/processed/dim_exchange.parquet"


# Read CSV files from GCS raw area
df_api = spark.read.option("header", True).option(
    "inferSchema", True).json(INPUT_API_FILE)
df_erp = spark.read.option("header", True).option(
    "inferSchema", True).csv(INPUT_ERP_FILE)


# Limpiar columnas


# Transformation Phase

# Join Trip Data and Fare Data

# data validation and data accuracy

df_stock_price

# Drop duplicates


df_company

df_exchange


# Save parquet files into GCS processed area
df_stock_price.write.mode("overwrite").parquet(OUTPUT_FACT_STOCK_PRICE)
df_company.write.mode("overwrite").parquet(OUTPUT_DIM_COMPANY)
df_exchange.write.mode("overwrite").parquet(OUTPUT_DIM_EXCHANGE)


# Finish Spark Session
spark.stop()
