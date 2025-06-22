provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

# Google Cloud Storage - GCS
resource "google_storage_bucket" "raw_fin_market_bucket" {
  name          = "raw_fin_market_bucket"
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 10
    }
    action {
      type = "Delete"
    }
  }
}

/*
# Google Dataproc
resource "google_dataproc_cluster" "" {
  name = ""
  region = var.region
  
  cluster_config {
}

# Google BigQuery Dataset
resource "google_bigquery_dataset" "fin_market_dw" {
  dataset_id = var.dataset_id
  project = var.project
  location  = var.region
  description = ""
  delete_contents_on_destroy = true
}

# Google BigQuery Table
resource "google_bigquery_table" "dim_" {
  dataset_id = google_bigquery_dataset.fin_market_dw.dataset_id
  table_id   = "dim_"
  schema     = file("./schemas/dim_customer.json")
}

# Google BigQuery Table
resource "google_bigquery_table" "fact_" {
  dataset_id = google_bigquery_dataset.fin_market_dw.dataset_id
  table_id   = "fact_"
  schema     = file("./schemas/dim_customer.json")
}


# Google Composer
resource "google_composer_environment" "composer_env" {
  name   = var.composer_env_name
  project = var.project
  region = var.region
*/
