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

module "database" {
  source        = "./../modules/database"
}

# Create the lambdas that will interact with the database

module "lambdas" {
  source        = "./../modules/lambdas"
  prefix        = "UncomfortableQuestions"
  lambda_folder = "${path.root}/../../lambda"
  dynamo_db_arn = module.database.database_arn
}

# Create an API for the website to talk to, that will trigger the lambdas (version 2)

module "api_gateway" {
  source                     = "./../modules/api_gateway"
  name                       = "UncomfortableQuestions"
  connect_uri                = module.lambdas.connect_uri
  connect_function_name      = module.lambdas.connect_function_name
  disconnect_uri             = module.lambdas.disconnect_uri
  disconnect_function_name   = module.lambdas.disconnect_function_name
  join_lobby_uri             = module.lambdas.join_lobby_uri
  join_lobby_function_name   = module.lambdas.join_lobby_function_name
  send_message_uri           = module.lambdas.send_message_uri
  send_message_function_name = module.lambdas.send_message_function_name
}
