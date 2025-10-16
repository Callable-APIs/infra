# IAM Users Configuration
# Generated on 2025-01-27 17:00:00 UTC
# 
# This file contains IAM users that exist in AWS and should be managed by Terraform.

# infra-deployer user
resource "aws_iam_user" "infra_deployer" {
  provider = aws.us_west_2

  name = "infra-deployer"

  tags = {
    Name        = "infra-deployer"
    Purpose     = "Infrastructure deployment"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# infra-reporter user
resource "aws_iam_user" "infra_reporter" {
  provider = aws.us_west_2

  name = "infra-reporter"

  tags = {
    Name        = "infra-reporter"
    Purpose     = "Cost reporting and analysis"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach AWS managed policy to infra-reporter
resource "aws_iam_user_policy_attachment" "infra_reporter_cost_policy" {
  provider = aws.us_west_2

  user       = aws_iam_user.infra_reporter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCostAndUsageReportAutomationPolicy"
}

# Inline policy for Cost Explorer access
resource "aws_iam_user_policy" "infra_reporter_cost_explorer" {
  provider = aws.us_west_2

  name = "AllowCostExplorerServiceAccess"
  user = aws_iam_user.infra_reporter.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "VisualEditor0"
        Effect   = "Allow"
        Action   = "ce:*"
        Resource = "*"
      }
    ]
  })
}

# Inline policy for infrastructure discovery
resource "aws_iam_user_policy" "infra_reporter_discovery" {
  provider = aws.us_west_2

  name = "InfrastructureDisccovery"
  user = aws_iam_user.infra_reporter.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "route53:List*",
          "route53:Get*",
          "s3:ListAllMyBuckets",
          "s3:GetBucket*",
          "iam:ListRoles",
          "iam:ListPolicies",
          "iam:ListRolePolicies",
          "iam:GetRole",
          "iam:GetPolicy"
        ]
        Resource = "*"
      }
    ]
  })
}

# Access keys for infra-deployer (managed outside Terraform to avoid conflicts)

# Access key for infra-reporter (1 active key)
resource "aws_iam_access_key" "infra_reporter_key" {
  provider = aws.us_west_2

  user = aws_iam_user.infra_reporter.name
}
