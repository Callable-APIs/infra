# AWS free-tier EC2 instance in default VPC

data "aws_vpc" "default" {

  default = true
}

data "aws_subnets" "default" {

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux" {

  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "general_purpose_sg" {

  name        = "callableapis-general-purpose-sg"
  description = "Security group for general-purpose EC2 node"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "callableapis-general-purpose-sg"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_key_pair" "callableapis_key" {

  key_name   = "callableapis-rotated"
  public_key = file("${path.root}/../ansible/artifacts/ssh/callableapis_rotated_public_key")

  tags = {
    Name        = "callableapis-rotated"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "general_purpose" {

  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro" # x86_64 for container compatibility, always free tier
  subnet_id     = data.aws_subnets.default.ids[0]
  
  # Force replacement to ensure x86_64 architecture
  lifecycle {
    create_before_destroy = true
  }

  vpc_security_group_ids      = [aws_security_group.general_purpose_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.callableapis_key.key_name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name        = "callableapis-general-purpose"
    Environment = "production"
    ManagedBy   = "terraform"
    Role        = "general-purpose"
  }
}


