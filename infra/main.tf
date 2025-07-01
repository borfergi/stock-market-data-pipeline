terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}


# Google Cloud Storage - GCS
resource "google_storage_bucket" "datalake_stock_market_bucket" {
  name                        = var.bucket_name
  location                    = var.region
  storage_class               = "STANDARD"
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Upload dim_date.csv file to recently created GCS bucket
resource "google_storage_bucket_object" "dim_date_csv" {
  name         = "dates/dates.csv"
  bucket       = var.bucket_name
  source       = "../data/dates.csv"
  content_type = "text/csv"
  depends_on   = [google_storage_bucket.datalake_stock_market_bucket]
}
# Upload dataproc script transform_stock_data_pipeline.py to recently created GCS bucket
resource "google_storage_bucket_object" "upload_dataproc_script" {
  name         = "dataproc_jobs/transform_stock_data.py"
  bucket       = var.bucket_name
  source       = "../dataproc_jobs/transform_stock_data_pipeline.py"
  content_type = "text/x-python"
  depends_on   = [google_storage_bucket.datalake_stock_market_bucket]
}

# Give dataproc batch creation permissions to your service account
resource "google_project_iam_member" "composer_dataproc_permissions" {
  project = var.project_id
  role    = "roles/dataproc.admin"
  member  = "serviceAccount:${var.service_account}"
}

# Google Composer - Airflow
resource "google_composer_environment" "google_composer" {
  name   = var.composer_name
  region = var.region

  config {
    software_config {
      image_version = "composer-3-airflow-2.10.5-build.6" # Composer and Airflow versions
      env_variables = {
        "SERVICE_ACCOUNT" = var.service_account
        "REGION"          = var.region
        "BUCKET_NAME"     = var.bucket_name
        "POLYGON_API_KEY" = var.polygon_api_key
        "DATASET_ID"      = var.dataset_id
      }
    }
    node_config {
      service_account = var.service_account
    }
    ## workloads_config {} -> Defaulf values
  }
}

# Give storage admin permissions to the Composer
resource "google_project_iam_member" "composer_storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${var.service_account}"
}

# Give logging permissions to the Composer
resource "google_project_iam_member" "composer_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${var.service_account}"
}

# Give Bigquery edit permissions to the Composer for later steps
resource "google_project_iam_member" "composer_bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${var.service_account}"
}


# Necessary to read dag_gcs_prefix later after the creation of the composer environment
data "google_composer_environment" "google_composer" {
  name       = var.composer_name
  region     = var.region
  depends_on = [google_composer_environment.google_composer]
}

# Define local variable to generate the Composer bucket name
locals {
  composer_bucket_name = replace(replace(data.google_composer_environment.google_composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")
}

# Upload dag to Google Composer
resource "google_storage_bucket_object" "upload_dag" {
  name       = "dags/stock_market_dag.py"
  bucket     = local.composer_bucket_name
  source     = "../dags/stock_market_dag.py"
  depends_on = [google_composer_environment.google_composer]
}


# BigQuery Dataset
resource "google_bigquery_dataset" "stock_market_dw" {
  dataset_id                 = var.dataset_id
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = true
}

# BigQuery Table dim_company
resource "google_bigquery_table" "dim_company" {
  dataset_id          = var.dataset_id
  table_id            = "dim_company"
  schema              = file("./schemas/dim_company_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

# BigQuery Table dim_date
resource "google_bigquery_table" "dim_date" {
  dataset_id          = var.dataset_id
  table_id            = "dim_date"
  schema              = file("./schemas/dim_date_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

# BigQuery Table dim_exchange
resource "google_bigquery_table" "dim_exchange" {
  dataset_id          = var.dataset_id
  table_id            = "dim_exchange"
  schema              = file("./schemas/dim_exchange_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

# BigQuery Table fact_stock_price
resource "google_bigquery_table" "fact_stock_price" {
  dataset_id          = var.dataset_id
  table_id            = "fact_stock_price"
  schema              = file("./schemas/fact_stock_price_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

