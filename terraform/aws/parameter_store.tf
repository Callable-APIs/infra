# Parameter Store for OAuth and other secrets
# Generated for CallableAPIs infrastructure

# GitHub OAuth Client ID
resource "aws_ssm_parameter" "github_client_id" {
  provider = aws.us_west_2

  name  = "/callableapis/github/client-id"
  type  = "String"
  value = "Ov23li0LGPKsZnyGEHsd"

  description = "GitHub OAuth Client ID for CallableAPIs authentication"

  tags = {
    Name        = "callableapis-github-client-id"
    Environment = "production"
    ManagedBy   = "terraform"
    Service     = "oauth"
  }
}

# GitHub OAuth Client Secret (placeholder - will be updated via UI)
resource "aws_ssm_parameter" "github_client_secret" {
  provider = aws.us_west_2

  name  = "/callableapis/github/client-secret"
  type  = "SecureString"
  value = "PLACEHOLDER_UPDATE_VIA_UI"

  description = "GitHub OAuth Client Secret for CallableAPIs authentication"

  tags = {
    Name        = "callableapis-github-client-secret"
    Environment = "production"
    ManagedBy   = "terraform"
    Service     = "oauth"
  }
}

# GitHub OAuth Redirect URI
resource "aws_ssm_parameter" "github_redirect_uri" {
  provider = aws.us_west_2

  name  = "/callableapis/github/redirect-uri"
  type  = "String"
  value = "https://api.callableapis.com/api/auth/callback"

  description = "GitHub OAuth Redirect URI for CallableAPIs"

  tags = {
    Name        = "callableapis-github-redirect-uri"
    Environment = "production"
    ManagedBy   = "terraform"
    Service     = "oauth"
  }
}

# GitHub OAuth Scope
resource "aws_ssm_parameter" "github_oauth_scope" {
  provider = aws.us_west_2

  name  = "/callableapis/github/oauth-scope"
  type  = "String"
  value = "user:email,read:user"

  description = "GitHub OAuth scope for CallableAPIs"

  tags = {
    Name        = "callableapis-github-oauth-scope"
    Environment = "production"
    ManagedBy   = "terraform"
    Service     = "oauth"
  }
}

# IAM Policy for Elastic Beanstalk to access Parameter Store
resource "aws_iam_policy" "parameter_store_access" {
  provider = aws.us_west_2

  name        = "callableapis-parameter-store-access"
  description = "Policy for CallableAPIs to access Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:us-west-2:${data.aws_caller_identity.current.account_id}:parameter/callableapis/github/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "callableapis-parameter-store-access"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach Parameter Store policy to Elastic Beanstalk instance role
resource "aws_iam_role_policy_attachment" "eb_parameter_store_access" {
  provider = aws.us_west_2

  role       = aws_iam_role.eb_instance_role.name
  policy_arn = aws_iam_policy.parameter_store_access.arn
}
