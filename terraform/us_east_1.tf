# US-EAST-1 Region Configuration
# Generated on 2025-01-05 16:57:00 UTC
# 
# This file contains resources specific to the us-east-1 region.
# All resources in this file use the aws.us_east_1 provider.

# Import blocks for existing resources
import {
  to = aws_instance.instance_i_0b42968767491c3c9
  id = "i-0b42968767491c3c9"
}

import {
  to = aws_vpc.vpc_vpc_4fc5fa35
  id = "vpc-4fc5fa35"
}

import {
  to = aws_subnet.subnet_subnet_b99877e6
  id = "subnet-b99877e6"
}

import {
  to = aws_subnet.subnet_subnet_b324d5d8
  id = "subnet-b324d5d8"
}

import {
  to = aws_subnet.subnet_subnet_23d4fb59
  id = "subnet-23d4fb59"
}

import {
  to = aws_security_group.security_group_sg_048390327b030fce1
  id = "sg-048390327b030fce1"
}

import {
  to = aws_security_group.security_group_sg_039e8bd8f8efdd536
  id = "sg-039e8bd8f8efdd536"
}

import {
  to = aws_route_table.route_table_rtb_a50c9ace
  id = "rtb-a50c9ace"
}

import {
  to = aws_internet_gateway.internet_gateway_igw_0c4a3b2d1e5f6789
  id = "igw-0c4a3b2d1e5f6789"
}

import {
  to = aws_eip.eip_eipalloc_0a1b2c3d4e5f6789
  id = "eipalloc-0a1b2c3d4e5f6789"
}

import {
  to = aws_ebs_volume.ebs_volume_vol_07a3e258331be1a74
  id = "vol-07a3e258331be1a74"
}

import {
  to = aws_route53_zone.route53_zone_zj57n2o5r20oe
  id = "ZJ57N2O5R20OE"
}

import {
  to = aws_route53_record.route53_record_zj57n2o5r20oe_callableapis_com__a
  id = "ZJ57N2O5R20OE_callableapis.com._A"
}

import {
  to = aws_route53_record.route53_record_zj57n2o5r20oe_www_callableapis_com__a
  id = "ZJ57N2O5R20OE_www.callableapis.com._A"
}

import {
  to = aws_route53_record.route53_record_zj57n2o5r20oe_api_callableapis_com__a
  id = "ZJ57N2O5R20OE_api.callableapis.com._A"
}

# Resource definitions
resource "aws_instance" "instance_i_0b42968767491c3c9" {
  provider = aws.us_east_1

  ami           = "ami-0855b98561d3195d1"
  instance_type = "t2.micro"
  subnet_id     = "subnet-b99877e6"

  vpc_security_group_ids = ["sg-048390327b030fce1"]

  tags = {
    Name                                = "CallableapisServiceEnv-env"
    "aws:cloudformation:stack-name"     = "awseb-e-9yatj6gavp-stack"
    "elasticbeanstalk:environment-name" = "CallableapisServiceEnv-env"
    "aws:cloudformation:logical-id"     = "AWSEBAutoScalingGroup"
  }
}

resource "aws_vpc" "vpc_vpc_4fc5fa35" {
  provider = aws.us_east_1

  cidr_block           = "172.31.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_b99877e6" {
  provider = aws.us_east_1

  vpc_id            = aws_vpc.vpc_vpc_4fc5fa35.id
  cidr_block        = "172.31.32.0/20"
  availability_zone = "us-east-1a"

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_b324d5d8" {
  provider = aws.us_east_1

  vpc_id            = aws_vpc.vpc_vpc_4fc5fa35.id
  cidr_block        = "172.31.0.0/20"
  availability_zone = "us-east-1b"

  tags = {
    Name = "default"
  }
}

resource "aws_subnet" "subnet_subnet_23d4fb59" {
  provider = aws.us_east_1

  vpc_id            = aws_vpc.vpc_vpc_4fc5fa35.id
  cidr_block        = "172.31.16.0/20"
  availability_zone = "us-east-1c"

  tags = {
    Name = "default"
  }
}

resource "aws_security_group" "security_group_sg_048390327b030fce1" {
  provider = aws.us_east_1

  name        = "awseb-e-9yatj6gavp-stack-AWSEBSecurityGroup-1Q8VGHGIBQ30A"
  description = "Security group for Elastic Beanstalk environment"
  vpc_id      = aws_vpc.vpc_vpc_4fc5fa35.id

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
    Name = "awseb-e-9yatj6gavp-stack-AWSEBSecurityGroup-1Q8VGHGIBQ30A"
  }
}

resource "aws_security_group" "security_group_sg_039e8bd8f8efdd536" {
  provider = aws.us_east_1

  name        = "default"
  description = "default VPC security group"
  vpc_id      = aws_vpc.vpc_vpc_4fc5fa35.id

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

resource "aws_route_table" "route_table_rtb_a50c9ace" {
  provider = aws.us_east_1

  vpc_id = aws_vpc.vpc_vpc_4fc5fa35.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway_igw_0c4a3b2d1e5f6789.id
  }

  tags = {
    Name = "default"
  }
}

resource "aws_internet_gateway" "internet_gateway_igw_0c4a3b2d1e5f6789" {
  provider = aws.us_east_1

  vpc_id = aws_vpc.vpc_vpc_4fc5fa35.id

  tags = {
    Name = "default"
  }
}

resource "aws_eip" "eip_eipalloc_0a1b2c3d4e5f6789" {
  provider = aws.us_east_1

  instance = aws_instance.instance_i_0b42968767491c3c9.id
  domain   = "vpc"

  tags = {
    Name                            = "CallableapisServiceEnv-env"
    "aws:cloudformation:logical-id" = "AWSEBEIP"
  }
}

resource "aws_ebs_volume" "ebs_volume_vol_07a3e258331be1a74" {
  provider = aws.us_east_1

  availability_zone = "us-east-1a"
  size              = 8
  type              = "gp2"

  tags = {
    Name = "vol-07a3e258331be1a74"
  }
}

resource "aws_route53_zone" "route53_zone_zj57n2o5r20oe" {
  provider = aws.us_east_1

  name = "callableapis.com"

  tags = {
    Name = "callableapis.com"
  }
}

resource "aws_route53_record" "route53_record_zj57n2o5r20oe_callableapis_com__a" {
  provider = aws.us_east_1

  zone_id = aws_route53_zone.route53_zone_zj57n2o5r20oe.zone_id
  name    = "callableapis.com."
  type    = "A"
  ttl     = 300

  records = ["35.170.87.155"]
}

resource "aws_route53_record" "route53_record_zj57n2o5r20oe_www_callableapis_com__a" {
  provider = aws.us_east_1

  zone_id = aws_route53_zone.route53_zone_zj57n2o5r20oe.zone_id
  name    = "www.callableapis.com."
  type    = "A"
  ttl     = 300

  records = ["35.170.87.155"]
}

resource "aws_route53_record" "route53_record_zj57n2o5r20oe_api_callableapis_com__a" {
  provider = aws.us_east_1

  zone_id = aws_route53_zone.route53_zone_zj57n2o5r20oe.zone_id
  name    = "api.callableapis.com."
  type    = "A"
  ttl     = 300

  records = ["18.191.248.15"]
}
