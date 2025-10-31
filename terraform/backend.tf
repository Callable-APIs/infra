terraform {
  backend "s3" {
    bucket         = "callableapis-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "callableapis-terraform-locks"
    encrypt        = true
  }
}


