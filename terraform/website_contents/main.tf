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
  prefix = "UncomfortableQuestions"
  tags = {
    Project = "Hidden Opinions"
  }
  lambdas = {
    "Connect" = {
      name  = module.lambdas.connect_function_name
      handler = "index.connect"
      route = "$connect"
      uri   = module.lambdas.connect_uri
    },
    "Disconnect" = {
      name  = module.lambdas.disconnect_function_name
      handler = "index.disconnect"
      route = "$disconnect"
      uri   = module.lambdas.disconnect_uri
    },
    "JoinGame" = {
      name  = module.lambdas.join_game_function_name
      handler = "index.join_game"
      route = "joinGame"
      uri   = module.lambdas.join_game_uri
    },
    "SendMessage" = {
      name  = module.lambdas.send_message_function_name
      handler = "index.send_message"
      route = "sendMessage"
      uri   = module.lambdas.send_message_uri
    }
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
  lambdas = local.lambdas
}
