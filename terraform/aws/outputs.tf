# AWS-specific outputs

output "eb_cname" {
  description = "Elastic Beanstalk CNAME"
  value       = aws_elastic_beanstalk_environment.callableapis_env.cname
}

output "eb_url" {
  description = "Elastic Beanstalk URL"
  value       = aws_elastic_beanstalk_environment.callableapis_env.endpoint_url
}

output "s3_website_endpoint" {
  description = "S3 website endpoint"
  value       = aws_s3_bucket_website_configuration.callableapis_website.website_endpoint
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.callableapis_website.bucket
}
