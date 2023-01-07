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
  terraform_output  = "stage"
  prefix            = "DeathDiceStage"
  prefix_lower      = "death-dice-stage"
  auth_callback_url = "http://localhost:5500/website/"
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

// S3 bucket to store game history forever

resource "aws_s3_bucket" "history" {
  bucket = "${local.prefix_lower}-database-history"
}

resource "aws_s3_bucket_acl" "history" {
  bucket = aws_s3_bucket.history.id
  acl    = "private"
}

resource "aws_s3_bucket_metric" "history" {
  bucket = aws_s3_bucket.history.bucket
  name   = "EntireBucket"
}

// Cognito to store user signups

resource "aws_cognito_user_pool" "users" {
  name                     = local.prefix
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
  password_policy {
    minimum_length                   = 6
    require_lowercase                = false
    require_numbers                  = false
    require_symbols                  = false
    require_uppercase                = false
    temporary_password_validity_days = 7
  }
  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true
    string_attribute_constraints {
      min_length = 5
      max_length = 2048
    }
  }
  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }
}

resource "aws_cognito_user_pool_domain" "users" {
  domain       = lower(local.prefix)
  user_pool_id = aws_cognito_user_pool.users.id
}

resource "aws_cognito_user_pool_client" "users" {
  name                                 = local.prefix
  user_pool_id                         = aws_cognito_user_pool.users.id
  callback_urls                        = [local.auth_callback_url]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid"]
  supported_identity_providers         = ["COGNITO"]
}
