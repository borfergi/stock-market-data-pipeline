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

/*
# Google Dataproc
resource "google_dataproc_cluster" "" {
  name = ""
  region = var.region
  
  cluster_config {
}
*/

# Google Cloud Storage - GCS
resource "google_storage_bucket" "raw_polygon_data_bucket" {
  name                        = var.gcs_bucket_name
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

# Google Composer
resource "google_composer_environment" "google_composer" {
  name   = var.composer_name
  region = var.region

  config {
    software_config {
      image_version = "composer-3-airflow-2.10.5-build.6"
      env_variables = {
        "BUCKET_NAME"     = var.gcs_bucket_name
        "POLYGON_API_KEY" = var.polygon_api_key
      }
    }
    node_config {
      service_account = var.service_account
    }
    ## workloads_config {} -> Defaulf values
  }
}

data "google_composer_environment" "google_composer" {
  name       = var.composer_name
  region     = var.region
  depends_on = [google_composer_environment.google_composer]
}

locals {
  composer_bucket_name = replace(replace(data.google_composer_environment.google_composer.config[0].dag_gcs_prefix, "gs://", ""), "/dags", "")
}

resource "google_storage_bucket_object" "upload_dag" {
  name       = "dags/stock_market_dag.py"
  bucket     = local.composer_bucket_name
  source     = "${path.module}/../dags/stock_market_dag.py"
  depends_on = [google_composer_environment.google_composer]
}


# BigQuery Dataset
resource "google_bigquery_dataset" "stock_market_dw" {
  dataset_id                 = var.dataset_id
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = true
}

# BigQuery Tables
resource "google_bigquery_table" "dim_company" {
  dataset_id          = var.dataset_id
  table_id            = "dim_company"
  schema              = file("./schemas/dim_company_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

resource "google_bigquery_table" "dim_date" {
  dataset_id          = var.dataset_id
  table_id            = "dim_date"
  schema              = file("./schemas/dim_date_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

# Google BigQuery Table
resource "google_bigquery_table" "dim_exchange" {
  dataset_id          = var.dataset_id
  table_id            = "dim_exchange"
  schema              = file("./schemas/dim_exchange_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}

resource "google_bigquery_table" "fact_stock_price" {
  dataset_id          = var.dataset_id
  table_id            = "fact_stock_price"
  schema              = file("./schemas/fact_stock_price_schema.json")
  deletion_protection = false
  depends_on          = [google_bigquery_dataset.stock_market_dw]
}
