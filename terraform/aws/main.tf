# AWS Infrastructure Module
# This module contains all AWS-specific resources

# Data source for latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {

  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-arm64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Use the specific AMI that's currently running
data "aws_ami" "current_instance" {

  filter {
    name   = "image-id"
    values = ["ami-001cfb1564f24ce79"]
  }
}

# VPC for us-west-2
resource "aws_vpc" "main" {

  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "callableapis-vpc"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {

  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "callableapis-igw"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Route Table
resource "aws_route_table" "public" {

  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "callableapis-public-rt"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public_1" {

  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {

  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Public Subnets
resource "aws_subnet" "public_1" {

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "callableapis-public-1"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public_2" {

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.31.2.0/24"
  availability_zone       = "us-west-2b"
  map_public_ip_on_launch = true

  tags = {
    Name        = "callableapis-public-2"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security Group for Elastic Beanstalk
resource "aws_security_group" "eb_security_group" {

  name        = "callableapis-eb-sg"
  description = "Security group for CallableAPIs Elastic Beanstalk"
  vpc_id      = aws_vpc.main.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH (restrict to your IP)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO: Restrict to your IP
  }

  # Container Services (port 8080)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "callableapis-eb-sg"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security Group for API Instance
resource "aws_security_group" "api_security_group" {

  name        = "callableapis-api-sg"
  description = "Security group for CallableAPIs API instance"
  vpc_id      = aws_vpc.main.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH (restrict to your IP)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO: Restrict to your IP
  }

  # Container Services (port 8080)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "callableapis-api-sg"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Key Pair (you'll need to create this manually or import existing)
resource "aws_key_pair" "callableapis_key" {

  key_name   = "callableapis-key"
  public_key = file("id_rsa.pub")

  tags = {
    Name        = "callableapis-key"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Elastic Beanstalk Application
resource "aws_elastic_beanstalk_application" "callableapis" {

  name        = "callableapis"
  description = "CallableAPIs application"

  appversion_lifecycle {
    service_role          = aws_iam_role.eb_service_role.arn
    max_count             = 128
    delete_source_from_s3 = true
  }

  tags = {
    Name        = "callableapis"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Elastic Beanstalk Environment
resource "aws_elastic_beanstalk_environment" "callableapis_env" {

  name                = "callableapis-java-env"
  application         = aws_elastic_beanstalk_application.callableapis.name
  solution_stack_name = "64bit Amazon Linux 2023 v5.7.5 running Tomcat 11 Corretto 21"

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = aws_vpc.main.id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = "${aws_subnet.public_1.id},${aws_subnet.public_2.id}"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = "true"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = "t4g.micro"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = aws_security_group.eb_security_group.id
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.eb_instance_profile.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "SingleInstance"
  }


  tags = {
    Name        = "callableapis-env"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Standalone API Instance removed - using Elastic Beanstalk instead

# IAM Role for Elastic Beanstalk Service
resource "aws_iam_role" "eb_service_role" {

  name = "callableapis-eb-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticbeanstalk.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "callableapis-eb-service-role"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach AWS managed policy for Elastic Beanstalk service role
resource "aws_iam_role_policy_attachment" "eb_service_role_policy" {

  role       = aws_iam_role.eb_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
}

# IAM Role for EC2 instances
resource "aws_iam_role" "eb_instance_role" {

  name = "callableapis-eb-instance-role"

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
    Name        = "callableapis-eb-instance-role"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach AWS managed policy for EC2 instances
resource "aws_iam_role_policy_attachment" "eb_instance_role_policy" {

  role       = aws_iam_role.eb_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "eb_instance_profile" {

  name = "callableapis-eb-instance-profile"
  role = aws_iam_role.eb_instance_role.name

  tags = {
    Name        = "callableapis-eb-instance-profile"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Attach CodeDeploy EC2 policy to EB instance role
resource "aws_iam_role_policy_attachment" "eb_codedeploy_policy" {

  role       = aws_iam_role.eb_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforAWSCodeDeploy"
}

# API service is now handled by Elastic Beanstalk environment

# DNS Records are now managed by Cloudflare
# See cloudflare.tf for DNS configuration
