# CodePipeline Infrastructure for us-west-2
# Generated for migrating from us-east-2


# IAM Role for CodePipeline
resource "aws_iam_role" "codepipeline_role" {
  provider = aws.us_west_2

  name = "callableapis-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codepipeline.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "callableapis-codepipeline-role"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# IAM Role for CodeBuild
resource "aws_iam_role" "codebuild_role" {
  provider = aws.us_west_2

  name = "callableapis-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "callableapis-codebuild-role"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# IAM Role for CodeDeploy
resource "aws_iam_role" "codedeploy_role" {
  provider = aws.us_west_2

  name = "callableapis-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "callableapis-codedeploy-role"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach policies to CodePipeline role
resource "aws_iam_role_policy" "codepipeline_policy" {
  provider = aws.us_west_2

  name = "callableapis-codepipeline-policy"
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetBucketVersioning",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::callableapis-deployments-us-west-2",
          "arn:aws:s3:::callableapis-deployments-us-west-2/*",
          "arn:aws:s3:::callableapis.com",
          "arn:aws:s3:::callableapis.com/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ]
        Resource = aws_codebuild_project.callableapis_service.arn
      },
      {
        Effect = "Allow"
        Action = [
          "codedeploy:CreateDeployment",
          "codedeploy:GetApplication",
          "codedeploy:GetApplicationRevision",
          "codedeploy:GetDeployment",
          "codedeploy:GetDeploymentConfig",
          "codedeploy:RegisterApplicationRevision"
        ]
        Resource = [
          aws_codedeploy_app.callableapis_service.arn,
          "arn:aws:codedeploy:us-west-2:${data.aws_caller_identity.current.account_id}:deploymentconfig:CodeDeployDefault.OneAtATime",
          "arn:aws:codedeploy:us-west-2:${data.aws_caller_identity.current.account_id}:deploymentconfig:CodeDeployDefault.HalfAtATime",
          "arn:aws:codedeploy:us-west-2:${data.aws_caller_identity.current.account_id}:deploymentconfig:CodeDeployDefault.AllAtOnce"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "elasticbeanstalk:*",
          "ec2:*",
          "ecs:*",
          "autoscaling:*",
          "elasticloadbalancing:*",
          "s3:*",
          "sns:*",
          "cloudformation:*",
          "rds:*",
          "sqs:*",
          "ecr:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policies to CodeBuild role
resource "aws_iam_role_policy" "codebuild_policy" {
  provider = aws.us_west_2

  name = "callableapis-codebuild-policy"
  role = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:us-west-2:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::callableapis-deployments-us-west-2/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:CreateReport",
          "codebuild:UpdateReport",
          "codebuild:BatchPutTestCases",
          "codebuild:BatchPutCodeCoverages"
        ]
        Resource = "arn:aws:codebuild:us-west-2:${data.aws_caller_identity.current.account_id}:report/callableapis-service-codebuild-*"
      }
    ]
  })
}

# Attach policies to CodeDeploy role
resource "aws_iam_role_policy_attachment" "codedeploy_service_role" {
  provider = aws.us_west_2

  role       = aws_iam_role.codedeploy_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
}

# IAM Role for CodeDeploy EC2 instances
resource "aws_iam_role" "codedeploy_ec2_role" {
  provider = aws.us_west_2

  name = "callableapis-codedeploy-ec2-permissions"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "callableapis-codedeploy-ec2-permissions"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# IAM Policy for CodeDeploy EC2 instances
resource "aws_iam_role_policy" "codedeploy_ec2_policy" {
  provider = aws.us_west_2

  name = "codedeploy-ec2-policy"
  role = aws_iam_role.codedeploy_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::callableapis-deployments-us-west-2",
          "arn:aws:s3:::callableapis-deployments-us-west-2/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:us-west-2:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# IAM Instance Profile for CodeDeploy EC2 (managed outside Terraform to avoid conflicts)

# CodeBuild project
resource "aws_codebuild_project" "callableapis_service" {
  provider = aws.us_west_2

  name         = "callableapis-service-codebuild"
  description  = "Build project for CallableAPIs service"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = "us-west-2"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec.yml"
  }

  tags = {
    Name        = "callableapis-service-codebuild"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# CodeDeploy application
resource "aws_codedeploy_app" "callableapis_service" {
  provider = aws.us_west_2

  compute_platform = "Server"
  name             = "callableapis-service-application"

  tags = {
    Name        = "callableapis-service-application"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# CodeDeploy deployment group
resource "aws_codedeploy_deployment_group" "callableapis_service" {
  provider = aws.us_west_2

  app_name              = aws_codedeploy_app.callableapis_service.name
  deployment_group_name = "callableapis-service-deploymentgroup"
  service_role_arn      = aws_iam_role.codedeploy_role.arn

  ec2_tag_filter {
    key   = "elasticbeanstalk:environment-name"
    type  = "KEY_AND_VALUE"
    value = "callableapis-java-env"
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  tags = {
    Name        = "callableapis-service-deploymentgroup"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# CodePipeline
resource "aws_codepipeline" "callableapis" {
  provider = aws.us_west_2

  name     = "callableapis-codepipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = "callableapis-deployments-us-west-2"
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "callableapis-website-source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["website-source"]

      configuration = {
        Owner                = "Callable-APIs"
        Repo                 = "website"
        Branch               = "main"
        OAuthToken           = var.github_token
        PollForSourceChanges = "true"
      }
    }

    action {
      name             = "callableapis-service-source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["service-source"]

      configuration = {
        Owner                = "Callable-APIs"
        Repo                 = "services"
        Branch               = "main"
        OAuthToken           = var.github_token
        PollForSourceChanges = "true"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "callableapis-service-build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["service-source"]
      output_artifacts = ["service-build"]

      configuration = {
        ProjectName = aws_codebuild_project.callableapis_service.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "callableapis-website-deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "S3"
      version         = "1"
      input_artifacts = ["website-source"]

      configuration = {
        BucketName = "callableapis-usw2.com"
        Extract    = "true"
      }
    }

    action {
      name            = "callableapis-service-deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "ElasticBeanstalk"
      version         = "1"
      input_artifacts = ["service-build"]

      configuration = {
        ApplicationName = "callableapis"
        EnvironmentName = "callableapis-java-env"
      }
    }
  }

  tags = {
    Name        = "callableapis-codepipeline"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# S3 bucket for website deployment
resource "aws_s3_bucket" "website" {
  provider = aws.us_west_2

  bucket = "callableapis-usw2.com"

  tags = {
    Name        = "callableapis-website-usw2"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# S3 bucket versioning for website
resource "aws_s3_bucket_versioning" "website" {
  provider = aws.us_west_2

  bucket = aws_s3_bucket.website.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket website configuration
resource "aws_s3_bucket_website_configuration" "website" {
  provider = aws.us_west_2

  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "website" {
  provider = aws.us_west_2

  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 bucket policy for public read access
resource "aws_s3_bucket_policy" "website" {
  provider = aws.us_west_2

  bucket = aws_s3_bucket.website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.website.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.website]
}

# Data source for current account ID
data "aws_caller_identity" "current" {
  provider = aws.us_west_2
}

# Variable for GitHub token
variable "github_token" {
  description = "GitHub OAuth token for CodePipeline"
  type        = string
  sensitive   = true
}
