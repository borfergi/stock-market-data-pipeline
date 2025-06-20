provider "google" {
  project = ""
  region  = "us-central1"
}

resource "google_storage_bucket" "fin_market_polygon_bucket" {
  name          = ""
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30
    }
  }

}
