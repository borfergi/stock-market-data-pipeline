import argparse
from pyspark.sql.functions import col, from_unixtime, to_date

from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp

# Iniciate Spark Session
spark = SparkSession.builder \
    .appName('transform-stock-market-data-pipeline') \
    .getOrCreate()


# Parameters
# Parse arguments
parser_args = argparse.ArgumentParser()
parser_args.add_argument("--bucket", required=True)
parser_args.add_argument("--date", required=True)
args = parser_args.parse_args()

BUCKET_NAME = args.bucket
PREVIOUS_DAY = args.previous_day

# Take the lastest polygon file as input
INPUT_API_PATH = f"gs://{BUCKET_NAME}/raw/polygon/*_{PREVIOUS_DAY}.json"
INPUT_ERP_PATH = f"gs://{BUCKET_NAME}/raw/ERP/erp_companies.csv"
OUTPUT_FACT_STOCK_PRICE = f"gs://{BUCKET_NAME}/processed/fact_stock_price.parquet"
OUTPUT_DIM_COMPANY = f"gs://{BUCKET_NAME}/processed/dim_company.parquet"
OUTPUT_DIM_EXCHANGE = f"gs://{BUCKET_NAME}/processed/dim_exchange.parquet"


# Read raw data
# Read symbol JSON files from GCS raw area
df_api = spark.read.option("header", True).option(
    "inferSchema", True).json(INPUT_API_PATH)

# Read ERP CSV files from GCS raw area
df_erp = spark.read.option("header", True).option(
    "inferSchema", True).csv(INPUT_ERP_PATH)

# Transformation phase
# Flatten JSON
df_stock_price = df_api.selectExpr(
    "ticker as Ticker",
    "results[0].o as Open",
    "results[0].h as High",
    "results[0].l as Low",
    "results[0].c as Close",
    "results[0].v as Volume",
    "results[0].vw as VWAP",
    "results[0].n as Transactions",
    "results[0].x as ExchangeCode",
    "results[0].t as timestamp"
)

# Convert timestamp UNIX to date format
df_stock_price = df_stock_price.withColumn("DateKey", to_date(
    from_unixtime(col("timestamp") / 1000)))

# Sort schema columns and ensure data types
df_stock_price = df_stock_price.select(
    col("DateKey").cast("date"),
    col("Ticker").cast("string"),
    col("Open").cast("float"),
    col("High").cast("float"),
    col("Low").cast("float"),
    col("Close").cast("float"),
    col("Volume").cast("int"),
    col("VWAP").cast("float"),
    col("Transactions").cast("int"),
    col("ExchangeCode").cast("string")
)

df_company = df_erp.select(
    col("company_symbol").alias("Ticker").cast("string"),
    col("company_name").alias("Name").cast("string"),
    col("sector").alias("Sector").cast("string"),
    col("industry").alias("Industry").cast("string")
)

df_exchange = df_erp.select(
    col("mic").alias("ExchangeCode").cast("string"),
    col("exchange_name").alias("ExchangeName").cast("string"),
    col("currency").alias("Currency").cast("string")
)

# Drop duplicates based on key columns
df_stock_price = df_stock_price.dropDuplicates(["DateKey", "Ticker"])
df_company = df_company.dropDuplicates(["Ticker"])
df_exchange = df_exchange.dropDuplicates(["ExchangeCode"])


# Validate REQUIRED values
df_stock_price = df_stock_price.filter(
    col("DateKey").isNotNull() & col("Ticker").isNotNull())
df_company = df_company.filter(col("Ticker").isNotNull())
df_exchange = df_exchange.filter(col("ExchangeCode").isNotNull())


# Save parquet files into GCS processed area
df_stock_price.write.mode("overwrite").parquet(OUTPUT_FACT_STOCK_PRICE)
df_company.write.mode("overwrite").parquet(OUTPUT_DIM_COMPANY)
df_exchange.write.mode("overwrite").parquet(OUTPUT_DIM_EXCHANGE)


# Finish Spark Session
spark.stop()
