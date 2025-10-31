# Enable required Google Cloud APIs
resource "google_project_service" "compute_api" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "oslogin_api" {
  service            = "oslogin.googleapis.com"
  disable_on_destroy = false
}

# Wait for APIs to be enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [
    google_project_service.compute_api,
    google_project_service.oslogin_api
  ]
  create_duration = "60s"
}
