variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Project region"
  default     = "us-central1"
  type        = string
}

variable "zone" {
  description = "Project zone"
  default     = "us-central1-a"
  type        = string
}

variable "dataset_id" {
  default = "fin_market_dw"
  type    = string
}
