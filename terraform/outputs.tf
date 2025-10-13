# Output definitions
# Generated on 2025-10-06 04:34:42 UTC

output "eb_cname" {
  description = "Elastic Beanstalk environment CNAME"
  value       = aws_elastic_beanstalk_environment.callableapis_env.cname
}

output "eb_url" {
  description = "Elastic Beanstalk environment URL"
  value       = aws_elastic_beanstalk_environment.callableapis_env.endpoint_url
}


