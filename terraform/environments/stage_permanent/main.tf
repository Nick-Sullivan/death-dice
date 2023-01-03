terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.48.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "death_dice/stage_permanent/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

locals {
  prefix_lower = "death-dice-stage"
  tags = {
    Project = "Death Dice Stage Permanent"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

resource "aws_s3_bucket" "history" {
  bucket = "${local.prefix_lower}-database-history"
}

resource "aws_s3_bucket_acl" "history" {
  bucket = aws_s3_bucket.history.id
  acl    = "private"
}
