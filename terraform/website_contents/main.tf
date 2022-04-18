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
    Project = "Hidden Opinions"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

# Create a database to store lobbies

resource "aws_dynamodb_table" "lobbies" {
  # note - doesn't have autoscaling
  name           = "UncomfortableQuestionsLobbies"
  hash_key       = "ConnectionId"
  # range_key      = "LobbyId"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # To efficiently search for lobbies, we need to set it as a key.
  global_secondary_index {
    name = "LobbyIndex"
    hash_key = "LobbyId"
    write_capacity = 5
    read_capacity = 5
    projection_type = "KEYS_ONLY"
    # non_key_attributes = ["description"]
  }

  # ttl {
  #   attribute_name = "TimeToLive"
  #   enabled = true
  # }
  attribute {
    name = "ConnectionId"
    type = "S"
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
    resources = [aws_dynamodb_table.lobbies.arn]
  }
}

# Create the lambdas that will interact with the database

module "website_lambda" {
  source        = "./../modules/website_lambda"
  prefix        = "UncomfortableQuestions"
  lambda_folder = "${path.root}/../../lambda"
  dynamo_db_arn = aws_dynamodb_table.lobbies.arn
}

# Create an API for the website to talk to, that will trigger the lambdas (version 2)

module "website_api_gateway" {
  source                     = "./../modules/website_api_gateway"
  name                       = "UncomfortableQuestions"
  connect_uri                = module.website_lambda.connect_uri
  connect_function_name      = module.website_lambda.connect_function_name
  disconnect_uri             = module.website_lambda.disconnect_uri
  disconnect_function_name   = module.website_lambda.disconnect_function_name
  join_lobby_uri             = module.website_lambda.join_lobby_uri
  join_lobby_function_name   = module.website_lambda.join_lobby_function_name
  send_message_uri           = module.website_lambda.send_message_uri
  send_message_function_name = module.website_lambda.send_message_function_name
}
