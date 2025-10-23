# Terraform backend configuration for S3 state storage
terraform {
  backend "s3" {
    bucket         = "callableapis-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "callableapis-terraform-locks"
  }
}
