variable "project_id" {
  default = "inspiring-rite-239607"
  type    = string
}

variable "service_account" {
  type    = string
  default = "myproject-user-account@inspiring-rite-239607.iam.gserviceaccount.com"
}

variable "polygon_api_key" {
  default = "zLjgXXDNkacKu3XH7JlMNZO3UeicBmFH"
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
