variable "project_id" {
  default = ""
  type    = string
}

variable "service_account" {
  type    = string
  default = ""
}

variable "polygon_api_key" {
  default = ""
  type    = string
}

variable "region" {
  default = "us-central1"
  type    = string
}

variable "zone" {
  default = "us-central1-a"
  type    = string
}



variable "gcs_bucket_name" {
  default = "raw-polygon-data-bucket"
  type    = string
}

variable "composer_name" {
  default = "stock-market-composer"
  type    = string
}

variable "dataset_id" {
  default = "stock_market_dw"
  type    = string
}
