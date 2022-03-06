terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.70.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "uncomfortable_questions_website/website_contents/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

locals {
  url     = var.domain
  url_www = "www.${local.url}"
  tags = {
    Project = "Uncomfortable Questions"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "us-east-1"
  default_tags {
    tags = local.tags
  }
}

# Create a public S3 bucket to host the files.

module "s3_bucket" {
  source        = "./../modules/website_s3_bucket"
  name          = local.url
  source_folder = "${path.root}/../../src"
}

# Create the lambda that will interact with the database

module "website_lambda" {
  source = "./../modules/website_lambda"
  name = "UncomfortableQuestions"
  lambda_folder = "${path.root}/../../lambda"
  dynamo_db_arn = aws_dynamodb_table.basic-dynamodb-table.arn
}

# Create an API for the website to talk to, that will trigger the lambdas (version 2)

module "website_api_gateway" {
  source = "./../modules/website_api_gateway"
  name = "UncomfortableQuestions"
  integration_uri = module.website_lambda.uri
  lambda_function_name = module.website_lambda.function_name
}

# Create a database to store lobbies

resource "aws_dynamodb_table" "basic-dynamodb-table" {
  # note - doesn't have autoscaling
  name           = "UncomfortableQuestionsLobbies"
  hash_key       = "LobbyId"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  ttl {
    attribute_name = "TimeToLive"
    enabled = true
  }

  attribute {
    name = "LobbyId"
    type = "S"
  }
}


data "aws_iam_policy_document" "inline_policy" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.basic-dynamodb-table.arn]
  }
}

