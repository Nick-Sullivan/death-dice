terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.70.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "death_dice/production/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

locals {
  prefix = "DeathDice"
  tags = {
    Project = "Death Dice"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

# Create an API with a URL, to be populated later

module "api_gateway_shell" {
  source = "./../../modules/api_gateway_shell"
  name   = local.prefix
}

# Create a database to store game state

module "database" {
  source = "./../../modules/database"
  prefix = local.prefix
}

# Create the lambdas that will interact with the database

module "lambdas" {
  source        = "./../../modules/lambdas"
  prefix        = local.prefix
  lambda_folder = "${path.root}/../../../lambda"
  table_arns    = module.database.table_arns
  gateway_url   = module.api_gateway_shell.gateway_url
}

# Populate the API so it will trigger the lambdas

module "api_gateway_integration" {
  source        = "./../../modules/api_gateway_integration"
  lambdas       = module.lambdas.lambdas
  websocket_id  = module.api_gateway_shell.websocket_id
  websocket_arn = module.api_gateway_shell.websocket_arn
}

# Create a dashboard for observing correct behaviour

module "cloudwatch" {
  source = "./../../modules/cloudwatch"
  name   = local.prefix
}
