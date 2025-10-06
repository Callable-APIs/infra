# US-EAST-2 Region Configuration
# Generated on 2025-01-05 16:57:00 UTC
# 
# This file contains resources specific to the us-east-2 region.
# All resources in this file use the aws.us_east_2 provider.

# Import blocks for existing resources
import {
  to = aws_instance.instance_i_0aaa66e426e07bcd4
  id = "i-0aaa66e426e07bcd4"
}

import {
  to = aws_vpc.vpc_vpc_64fe370f
  id = "vpc-64fe370f"
}

import {
  to = aws_subnet.subnet_subnet_f923b4b5
  id = "subnet-f923b4b5"
}

import {
  to = aws_subnet.subnet_subnet_0a1b2c3d4e5f6789
  id = "subnet-0a1b2c3d4e5f6789"
}

import {
  to = aws_subnet.subnet_subnet_1b2c3d4e5f6789ab
  id = "subnet-1b2c3d4e5f6789ab"
}

import {
  to = aws_security_group.security_group_sg_39308b5f
  id = "sg-39308b5f"
}

import {
  to = aws_security_group.security_group_sg_4a4b5c6d7e8f9a0b
  id = "sg-4a4b5c6d7e8f9a0b"
}

import {
  to = aws_route_table.route_table_rtb_1234567890abcdef
  id = "rtb-1234567890abcdef"
}

import {
  to = aws_internet_gateway.internet_gateway_igw_1234567890abcdef
  id = "igw-1234567890abcdef"
}

import {
  to = aws_ebs_volume.ebs_volume_vol_05879fa19a48b822b
  id = "vol-05879fa19a48b822b"
}

# Resource definitions
resource "aws_instance" "instance_i_0aaa66e426e07bcd4" {
  provider = aws.us_east_2

  ami           = "ami-0e01ce4ee18447327"
  instance_type = "t2.micro"
  subnet_id     = "subnet-f923b4b5"

  vpc_security_group_ids = ["sg-39308b5f"]

  tags = {
    Name                            = "i-0aaa66e426e07bcd4"
    "aws:ec2launchtemplate:id"      = "lt-06ed92770a7d59636"
    "deploy-target"                 = "callableapis-service"
    "aws:ec2launchtemplate:version" = "7"
  }
}

resource "aws_vpc" "vpc_vpc_64fe370f" {
  provider = aws.us_east_2

  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_f923b4b5" {
  provider = aws.us_east_2

  vpc_id            = aws_vpc.vpc_vpc_64fe370f.id
  cidr_block        = "172.31.32.0/20"
  availability_zone = "us-east-2c"

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_0a1b2c3d4e5f6789" {
  provider = aws.us_east_2

  vpc_id            = aws_vpc.vpc_vpc_64fe370f.id
  cidr_block        = "172.31.0.0/20"
  availability_zone = "us-east-2a"

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_1b2c3d4e5f6789ab" {
  provider = aws.us_east_2

  vpc_id            = aws_vpc.vpc_vpc_64fe370f.id
  cidr_block        = "172.31.16.0/20"
  availability_zone = "us-east-2b"

  tags = {
    Name = "default"
  }
}

resource "aws_security_group" "security_group_sg_39308b5f" {
  provider = aws.us_east_2

  name        = "default"
  description = "default VPC security group"
  vpc_id      = aws_vpc.vpc_vpc_64fe370f.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "default"
  }
}

resource "aws_security_group" "security_group_sg_4a4b5c6d7e8f9a0b" {
  provider = aws.us_east_2

  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.vpc_vpc_64fe370f.id

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

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}

resource "aws_route_table" "route_table_rtb_1234567890abcdef" {
  provider = aws.us_east_2

  vpc_id = aws_vpc.vpc_vpc_64fe370f.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway_igw_1234567890abcdef.id
  }

  tags = {
    Name = "default"
  }
}

resource "aws_internet_gateway" "internet_gateway_igw_1234567890abcdef" {
  provider = aws.us_east_2

  vpc_id = aws_vpc.vpc_vpc_64fe370f.id

  tags = {
    Name = "default"
  }
}

resource "aws_ebs_volume" "ebs_volume_vol_05879fa19a48b822b" {
  provider = aws.us_east_2

  availability_zone = "us-east-2c"
  size              = 8
  type              = "gp2"

  tags = {
    Name = "vol-05879fa19a48b822b"
  }
}
