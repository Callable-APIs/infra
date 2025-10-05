# Main Terraform configuration
# Generated on 2025-10-05 08:20:55 UTC
# 
# This file contains the main infrastructure configuration
# generated from your current AWS deployment.
# 
# IMPORTANT: This configuration uses import blocks to import existing resources.
# Run 'terraform plan' to verify the configuration matches your current infrastructure.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Import blocks for existing resources
import {
  to = aws_instance.callableapisserviceenv-env
  id = "i-0b42968767491c3c9"
}
import {
  to = aws_vpc.vpc-4fc5fa35
  id = "vpc-4fc5fa35"
}
import {
  to = aws_subnet.subnet-17cd2436
  id = "subnet-17cd2436"
}
import {
  to = aws_subnet.subnet-891c2ab7
  id = "subnet-891c2ab7"
}
import {
  to = aws_subnet.subnet-bfb705f2
  id = "subnet-bfb705f2"
}
import {
  to = aws_subnet.subnet-ff648799
  id = "subnet-ff648799"
}
import {
  to = aws_subnet.subnet-b99877e6
  id = "subnet-b99877e6"
}
import {
  to = aws_subnet.subnet-5cf45052
  id = "subnet-5cf45052"
}
import {
  to = aws_security_group.sg-820ba7af
  id = "sg-820ba7af"
}
import {
  to = aws_security_group.callableapisserviceenv-env_1
  id = "sg-048390327b030fce1"
}
import {
  to = aws_route_table.rtb-0e4bf170
  id = "rtb-0e4bf170"
}
import {
  to = aws_internet_gateway.igw-eab6d491
  id = "igw-eab6d491"
}
import {
  to = aws_eip.callableapisserviceenv-env_2
  id = "eipalloc-00bc12209dd2ce49b"
}
import {
  to = aws_ebs_volume.vol-07a3e258331be1a74
  id = "vol-07a3e258331be1a74"
}
import {
  to = aws_route53_zone.zj57n2o5r20oe
  id = "ZJ57N2O5R20OE"
}
import {
  to = aws_route53_record.zj57n2o5r20oe_callableapis_com__a
  id = "ZJ57N2O5R20OE_callableapis.com._A"
}
import {
  to = aws_route53_record.zj57n2o5r20oe_api_callableapis_com__a
  id = "ZJ57N2O5R20OE_api.callableapis.com._A"
}
import {
  to = aws_route53_record.zj57n2o5r20oe_www_callableapis_com__a
  id = "ZJ57N2O5R20OE_www.callableapis.com._A"
}
import {
  to = aws_s3_bucket.callableapis_com
  id = "callableapis.com"
}
import {
  to = aws_s3_bucket.codepipeline-us-east-2-207476045341
  id = "codepipeline-us-east-2-207476045341"
}
import {
  to = aws_s3_bucket.elasticbeanstalk-us-east-1-312005263551
  id = "elasticbeanstalk-us-east-1-312005263551"
}
import {
  to = aws_s3_bucket.elasticbeanstalk-us-east-2-312005263551
  id = "elasticbeanstalk-us-east-2-312005263551"
}
import {
  to = aws_s3_bucket.www_callableapis_com
  id = "www.callableapis.com"
}
import {
  to = aws_iam_role.aws-elasticbeanstalk-ec2-role
  id = "aws-elasticbeanstalk-ec2-role"
}
import {
  to = aws_iam_role.aws-elasticbeanstalk-service-role
  id = "aws-elasticbeanstalk-service-role"
}
import {
  to = aws_iam_role.awscodedeployroleforecs
  id = "AWSCodeDeployRoleForECS"
}
import {
  to = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-codepipeline
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"
}
import {
  to = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-service
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"
}
import {
  to = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-website
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"
}
import {
  to = aws_iam_role.awsserviceroleforautoscaling
  id = "AWSServiceRoleForAutoScaling"
}
import {
  to = aws_iam_role.awsserviceroleforsupport
  id = "AWSServiceRoleForSupport"
}
import {
  to = aws_iam_role.awsservicerolefortrustedadvisor
  id = "AWSServiceRoleForTrustedAdvisor"
}
import {
  to = aws_iam_role.callableapis-codedeploy-ec2-permissions
  id = "callableapis-codedeploy-ec2-permissions"
}
import {
  to = aws_iam_role.callableapis-service-codedeploy-role
  id = "callableapis-service-codedeploy-role"
}
import {
  to = aws_iam_role.codebuild-callableapis-service-build-service-role
  id = "codebuild-callableapis-service-build-service-role"
}
import {
  to = aws_iam_role.codedeploy-ec2-profile-role
  id = "codedeploy-ec2-profile-role"
}
import {
  to = aws_iam_role.cwe-role-us-east-2-callableapis-codepipeline
  id = "cwe-role-us-east-2-callableapis-codepipeline"
}
import {
  to = aws_iam_policy.lightsail
  id = "Lightsail"
}
import {
  to = aws_iam_policy.awscodepipelineservicerole-us-east-2-callableapis-website_1
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"
}
import {
  to = aws_iam_policy.codebuildbasepolicy-callableapis-service-codebuild-us-east-2
  id = "CodeBuildBasePolicy-callableapis-service-codebuild-us-east-2"
}
import {
  to = aws_iam_policy.start-pipeline-execution-us-east-2-callableapis-codepipeline
  id = "start-pipeline-execution-us-east-2-callableapis-codepipeline"
}
import {
  to = aws_iam_policy.codebuildcloudwatchlogspolicy-callableapis-service-build-us-east-2
  id = "CodeBuildCloudWatchLogsPolicy-callableapis-service-build-us-east-2"
}
import {
  to = aws_iam_policy.codedeploy-ec2-policy
  id = "codedeploy-ec2-policy"
}
import {
  to = aws_iam_policy.awscodepipelineservicerole-us-east-2-callableapis-service_1
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"
}
import {
  to = aws_iam_policy.codebuildbasepolicy-callableapis-service-build-us-east-2
  id = "CodeBuildBasePolicy-callableapis-service-build-us-east-2"
}
import {
  to = aws_iam_policy.callableapis-codedeploy-ec2-permissions_1
  id = "callableapis-codedeploy-ec2-permissions"
}
import {
  to = aws_iam_policy.awscodepipelineservicerole-us-east-2-callableapis-codepipeline_1
  id = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"
}

# Resource configurations

resource "aws_instance" "callableapisserviceenv-env_3" {
  ami           = "ami-0855b98561d3195d1"
  instance_type = "t2.micro"
  subnet_id     = "subnet-b99877e6"

  vpc_security_group_ids = ["sg-048390327b030fce1"]

  # Add key_name if available
  # key_name = "your-key-pair"

  # Add user_data if available
  # user_data = base64encode(file("user_data.sh"))

  tags = {
    Name                                = "i-0b42968767491c3c9"
    "aws:cloudformation:stack-name"     = "awseb-e-9yatj6gavp-stack"
    "elasticbeanstalk:environment-name" = "CallableapisServiceEnv-env"
    "aws:cloudformation:logical-id"     = "AWSEBAutoScalingGroup"
    Name                                = "CallableapisServiceEnv-env"
    "aws:cloudformation:stack-id"       = "arn:aws:cloudformation:us-east-1:312005263551:stack/awseb-e-9yatj6gavp-stack/7d159030-6547-11ea-b327-0ee5b554e1bc"
    "aws:autoscaling:groupName"         = "awseb-e-9yatj6gavp-stack-AWSEBAutoScalingGroup-16CDJLU3C4I7"
    "elasticbeanstalk:environment-id"   = "e-9yatj6gavp"
  }
}


resource "aws_vpc" "vpc-4fc5fa35_1" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpc-4fc5fa35"

  }
}


resource "aws_subnet" "subnet-17cd2436_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.80.0/20"
  availability_zone = "us-east-1a"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-17cd2436"

  }
}


resource "aws_subnet" "subnet-891c2ab7_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.48.0/20"
  availability_zone = "us-east-1e"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-891c2ab7"

  }
}


resource "aws_subnet" "subnet-bfb705f2_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.16.0/20"
  availability_zone = "us-east-1b"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-bfb705f2"

  }
}


resource "aws_subnet" "subnet-ff648799_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.0.0/20"
  availability_zone = "us-east-1d"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-ff648799"

  }
}


resource "aws_subnet" "subnet-b99877e6_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.32.0/20"
  availability_zone = "us-east-1c"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-b99877e6"

  }
}


resource "aws_subnet" "subnet-5cf45052_1" {
  vpc_id            = "vpc-4fc5fa35"
  cidr_block        = "172.31.64.0/20"
  availability_zone = "us-east-1f"

  map_public_ip_on_launch = true

  tags = {
    Name = "subnet-5cf45052"

  }
}


resource "aws_security_group" "sg-820ba7af_1" {
  name        = "default"
  description = "default VPC security group"
  vpc_id      = "vpc-4fc5fa35"



  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = ""
  }

  tags = {
    Name = "default"

  }
}


resource "aws_security_group" "callableapisserviceenv-env_4" {
  name        = "awseb-e-9yatj6gavp-stack-AWSEBSecurityGroup-1Q8VGHGIBQ30A"
  description = "SecurityGroup for ElasticBeanstalk environment."
  vpc_id      = "vpc-4fc5fa35"


  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = ""
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = ""
  }

  tags = {
    Name                                = "awseb-e-9yatj6gavp-stack-AWSEBSecurityGroup-1Q8VGHGIBQ30A"
    "aws:cloudformation:stack-name"     = "awseb-e-9yatj6gavp-stack"
    Name                                = "CallableapisServiceEnv-env"
    "aws:cloudformation:logical-id"     = "AWSEBSecurityGroup"
    "elasticbeanstalk:environment-id"   = "e-9yatj6gavp"
    "aws:cloudformation:stack-id"       = "arn:aws:cloudformation:us-east-1:312005263551:stack/awseb-e-9yatj6gavp-stack/7d159030-6547-11ea-b327-0ee5b554e1bc"
    "elasticbeanstalk:environment-name" = "CallableapisServiceEnv-env"
  }
}


resource "aws_route_table" "rtb-0e4bf170_1" {
  vpc_id = "vpc-4fc5fa35"

  tags = {
    Name = "rtb-0e4bf170"

  }
}


resource "aws_internet_gateway" "igw-eab6d491_1" {
  vpc_id = ""

  tags = {
    Name = "igw-eab6d491"

  }
}


resource "aws_eip" "callableapisserviceenv-env_5" {
  domain = "vpc"

  tags = {
    Name                                = "35.170.87.155"
    "aws:cloudformation:logical-id"     = "AWSEBEIP"
    Name                                = "CallableapisServiceEnv-env"
    "aws:cloudformation:stack-id"       = "arn:aws:cloudformation:us-east-1:312005263551:stack/awseb-e-9yatj6gavp-stack/7d159030-6547-11ea-b327-0ee5b554e1bc"
    "elasticbeanstalk:environment-id"   = "e-9yatj6gavp"
    "aws:cloudformation:stack-name"     = "awseb-e-9yatj6gavp-stack"
    "elasticbeanstalk:environment-name" = "CallableapisServiceEnv-env"
  }
}


resource "aws_ebs_volume" "vol-07a3e258331be1a74_1" {
  availability_zone = "us-east-1c"
  size              = 8
  type              = "gp2"
  encrypted         = false

  tags = {
    Name = "vol-07a3e258331be1a74"

  }
}


resource "aws_route53_zone" "zj57n2o5r20oe_1" {
  name = "callableapis.com."

  tags = {
    Name = "callableapis.com."
  }
}


resource "aws_route53_record" "zj57n2o5r20oe_callableapis_com__a_1" {
  zone_id = "ZJ57N2O5R20OE"
  name    = "callableapis.com."
  type    = "A"

  alias {
    name                   = "s3-website.us-east-2.amazonaws.com."
    zone_id                = "Z2O1EMRO9K5GLX"
    evaluate_target_health = false
  }
}


resource "aws_route53_record" "zj57n2o5r20oe_api_callableapis_com__a_1" {
  zone_id = "ZJ57N2O5R20OE"
  name    = "api.callableapis.com."
  type    = "A"
  ttl     = 300

  records = ["18.191.248.15"]
}


resource "aws_route53_record" "zj57n2o5r20oe_www_callableapis_com__a_1" {
  zone_id = "ZJ57N2O5R20OE"
  name    = "www.callableapis.com."
  type    = "A"

  alias {
    name                   = "s3-website.us-east-2.amazonaws.com."
    zone_id                = "Z2O1EMRO9K5GLX"
    evaluate_target_health = false
  }
}


resource "aws_s3_bucket" "callableapis_com_1" {
  bucket = "callableapis.com"

  tags = {
    Name = "callableapis.com"
  }
}

resource "aws_s3_bucket_versioning" "callableapis_com_1" {
  bucket = aws_s3_bucket.callableapis_com_1.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "callableapis_com_1" {
  bucket = aws_s3_bucket.callableapis_com_1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_s3_bucket" "codepipeline-us-east-2-207476045341_1" {
  bucket = "codepipeline-us-east-2-207476045341"

  tags = {
    Name = "codepipeline-us-east-2-207476045341"
  }
}

resource "aws_s3_bucket_versioning" "codepipeline-us-east-2-207476045341_1" {
  bucket = aws_s3_bucket.codepipeline-us-east-2-207476045341_1.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "codepipeline-us-east-2-207476045341_1" {
  bucket = aws_s3_bucket.codepipeline-us-east-2-207476045341_1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_s3_bucket" "elasticbeanstalk-us-east-1-312005263551_1" {
  bucket = "elasticbeanstalk-us-east-1-312005263551"

  tags = {
    Name = "elasticbeanstalk-us-east-1-312005263551"
  }
}

resource "aws_s3_bucket_versioning" "elasticbeanstalk-us-east-1-312005263551_1" {
  bucket = aws_s3_bucket.elasticbeanstalk-us-east-1-312005263551_1.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "elasticbeanstalk-us-east-1-312005263551_1" {
  bucket = aws_s3_bucket.elasticbeanstalk-us-east-1-312005263551_1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_s3_bucket" "elasticbeanstalk-us-east-2-312005263551_1" {
  bucket = "elasticbeanstalk-us-east-2-312005263551"

  tags = {
    Name = "elasticbeanstalk-us-east-2-312005263551"
  }
}

resource "aws_s3_bucket_versioning" "elasticbeanstalk-us-east-2-312005263551_1" {
  bucket = aws_s3_bucket.elasticbeanstalk-us-east-2-312005263551_1.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "elasticbeanstalk-us-east-2-312005263551_1" {
  bucket = aws_s3_bucket.elasticbeanstalk-us-east-2-312005263551_1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_s3_bucket" "www_callableapis_com_1" {
  bucket = "www.callableapis.com"

  tags = {
    Name = "www.callableapis.com"
  }
}

resource "aws_s3_bucket_versioning" "www_callableapis_com_1" {
  bucket = aws_s3_bucket.www_callableapis_com_1.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "www_callableapis_com_1" {
  bucket = aws_s3_bucket.www_callableapis_com_1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_iam_role" "aws-elasticbeanstalk-ec2-role_1" {
  name = "aws-elasticbeanstalk-ec2-role"

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
    Name = "aws-elasticbeanstalk-ec2-role"

  }
}

resource "aws_iam_instance_profile" "aws-elasticbeanstalk-ec2-role_1" {
  name = "aws-elasticbeanstalk-ec2-role-profile"
  role = aws_iam_role.aws-elasticbeanstalk-ec2-role_1.name
}


resource "aws_iam_role" "aws-elasticbeanstalk-service-role_1" {
  name = "aws-elasticbeanstalk-service-role"

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
    Name = "aws-elasticbeanstalk-service-role"

  }
}

resource "aws_iam_instance_profile" "aws-elasticbeanstalk-service-role_1" {
  name = "aws-elasticbeanstalk-service-role-profile"
  role = aws_iam_role.aws-elasticbeanstalk-service-role_1.name
}


resource "aws_iam_role" "awscodedeployroleforecs_1" {
  name = "AWSCodeDeployRoleForECS"

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
    Name = "AWSCodeDeployRoleForECS"

  }
}

resource "aws_iam_instance_profile" "awscodedeployroleforecs_1" {
  name = "AWSCodeDeployRoleForECS-profile"
  role = aws_iam_role.awscodedeployroleforecs_1.name
}


resource "aws_iam_role" "awscodepipelineservicerole-us-east-2-callableapis-codepipeline_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"

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
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"

  }
}

resource "aws_iam_instance_profile" "awscodepipelineservicerole-us-east-2-callableapis-codepipeline_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline-profile"
  role = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-codepipeline_2.name
}


resource "aws_iam_role" "awscodepipelineservicerole-us-east-2-callableapis-service_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"

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
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"

  }
}

resource "aws_iam_instance_profile" "awscodepipelineservicerole-us-east-2-callableapis-service_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-service-profile"
  role = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-service_2.name
}


resource "aws_iam_role" "awscodepipelineservicerole-us-east-2-callableapis-website_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"

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
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"

  }
}

resource "aws_iam_instance_profile" "awscodepipelineservicerole-us-east-2-callableapis-website_2" {
  name = "AWSCodePipelineServiceRole-us-east-2-callableapis-website-profile"
  role = aws_iam_role.awscodepipelineservicerole-us-east-2-callableapis-website_2.name
}


resource "aws_iam_role" "awsserviceroleforautoscaling_1" {
  name = "AWSServiceRoleForAutoScaling"

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
    Name = "AWSServiceRoleForAutoScaling"

  }
}

resource "aws_iam_instance_profile" "awsserviceroleforautoscaling_1" {
  name = "AWSServiceRoleForAutoScaling-profile"
  role = aws_iam_role.awsserviceroleforautoscaling_1.name
}


resource "aws_iam_role" "awsserviceroleforsupport_1" {
  name = "AWSServiceRoleForSupport"

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
    Name = "AWSServiceRoleForSupport"

  }
}

resource "aws_iam_instance_profile" "awsserviceroleforsupport_1" {
  name = "AWSServiceRoleForSupport-profile"
  role = aws_iam_role.awsserviceroleforsupport_1.name
}


resource "aws_iam_role" "awsservicerolefortrustedadvisor_1" {
  name = "AWSServiceRoleForTrustedAdvisor"

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
    Name = "AWSServiceRoleForTrustedAdvisor"

  }
}

resource "aws_iam_instance_profile" "awsservicerolefortrustedadvisor_1" {
  name = "AWSServiceRoleForTrustedAdvisor-profile"
  role = aws_iam_role.awsservicerolefortrustedadvisor_1.name
}


resource "aws_iam_role" "callableapis-codedeploy-ec2-permissions_2" {
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
    Name = "callableapis-codedeploy-ec2-permissions"

  }
}

resource "aws_iam_instance_profile" "callableapis-codedeploy-ec2-permissions_2" {
  name = "callableapis-codedeploy-ec2-permissions-profile"
  role = aws_iam_role.callableapis-codedeploy-ec2-permissions_2.name
}


resource "aws_iam_role" "callableapis-service-codedeploy-role_1" {
  name = "callableapis-service-codedeploy-role"

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
    Name = "callableapis-service-codedeploy-role"

  }
}

resource "aws_iam_instance_profile" "callableapis-service-codedeploy-role_1" {
  name = "callableapis-service-codedeploy-role-profile"
  role = aws_iam_role.callableapis-service-codedeploy-role_1.name
}


resource "aws_iam_role" "codebuild-callableapis-service-build-service-role_1" {
  name = "codebuild-callableapis-service-build-service-role"

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
    Name = "codebuild-callableapis-service-build-service-role"

  }
}

resource "aws_iam_instance_profile" "codebuild-callableapis-service-build-service-role_1" {
  name = "codebuild-callableapis-service-build-service-role-profile"
  role = aws_iam_role.codebuild-callableapis-service-build-service-role_1.name
}


resource "aws_iam_role" "codedeploy-ec2-profile-role_1" {
  name = "codedeploy-ec2-profile-role"

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
    Name = "codedeploy-ec2-profile-role"

  }
}

resource "aws_iam_instance_profile" "codedeploy-ec2-profile-role_1" {
  name = "codedeploy-ec2-profile-role-profile"
  role = aws_iam_role.codedeploy-ec2-profile-role_1.name
}


resource "aws_iam_role" "cwe-role-us-east-2-callableapis-codepipeline_1" {
  name = "cwe-role-us-east-2-callableapis-codepipeline"

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
    Name = "cwe-role-us-east-2-callableapis-codepipeline"

  }
}

resource "aws_iam_instance_profile" "cwe-role-us-east-2-callableapis-codepipeline_1" {
  name = "cwe-role-us-east-2-callableapis-codepipeline-profile"
  role = aws_iam_role.cwe-role-us-east-2-callableapis-codepipeline_1.name
}


resource "aws_iam_policy" "lightsail_1" {
  name        = "Lightsail"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "Lightsail"

  }
}


resource "aws_iam_policy" "awscodepipelineservicerole-us-east-2-callableapis-website_3" {
  name        = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-website"

  }
}


resource "aws_iam_policy" "codebuildbasepolicy-callableapis-service-codebuild-us-east-2_1" {
  name        = "CodeBuildBasePolicy-callableapis-service-codebuild-us-east-2"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "CodeBuildBasePolicy-callableapis-service-codebuild-us-east-2"

  }
}


resource "aws_iam_policy" "start-pipeline-execution-us-east-2-callableapis-codepipeline_1" {
  name        = "start-pipeline-execution-us-east-2-callableapis-codepipeline"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "start-pipeline-execution-us-east-2-callableapis-codepipeline"

  }
}


resource "aws_iam_policy" "codebuildcloudwatchlogspolicy-callableapis-service-build-us-east-2_1" {
  name        = "CodeBuildCloudWatchLogsPolicy-callableapis-service-build-us-east-2"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "CodeBuildCloudWatchLogsPolicy-callableapis-service-build-us-east-2"

  }
}


resource "aws_iam_policy" "codedeploy-ec2-policy_1" {
  name        = "codedeploy-ec2-policy"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "codedeploy-ec2-policy"

  }
}


resource "aws_iam_policy" "awscodepipelineservicerole-us-east-2-callableapis-service_3" {
  name        = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-service"

  }
}


resource "aws_iam_policy" "codebuildbasepolicy-callableapis-service-build-us-east-2_1" {
  name        = "CodeBuildBasePolicy-callableapis-service-build-us-east-2"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "CodeBuildBasePolicy-callableapis-service-build-us-east-2"

  }
}


resource "aws_iam_policy" "callableapis-codedeploy-ec2-permissions_3" {
  name        = "callableapis-codedeploy-ec2-permissions"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "callableapis-codedeploy-ec2-permissions"

  }
}


resource "aws_iam_policy" "awscodepipelineservicerole-us-east-2-callableapis-codepipeline_3" {
  name        = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"
  description = ""

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "AWSCodePipelineServiceRole-us-east-2-callableapis-codepipeline"

  }
}

