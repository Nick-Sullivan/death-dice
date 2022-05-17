terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.70.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "death_dice/website_contents/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

locals {
  prefix  = "DeathDice"
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

# Create a database to store game state

module "database" {
  source = "./../modules/database"
  prefix = local.prefix
}

# Create the lambdas that will interact with the database

module "lambdas" {
  source        = "./../modules/lambdas"
  prefix        = local.prefix
  lambda_folder = "${path.root}/../../lambda"
  table_arns    = module.database.table_arns
}

# Create an API for the website to talk to, that will trigger the lambdas

module "api_gateway" {
  source  = "./../modules/api_gateway"
  name    = local.prefix
  lambdas = module.lambdas.lambdas
}
