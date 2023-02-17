terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.48.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "death_dice/stage/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

locals {
  admin_email    = "nick.dave.sullivan@gmail.com"
  aws_account_id = "314077822992"

  prefix            = "DeathDiceStage"
  prefix_lower      = "death-dice-stage"
  prefix_underscore = "death_dice_stage"

  prefix_analytics            = "${local.prefix}Analytics"
  prefix_analytics_underscore = "${local.prefix_underscore}_analytics"

  permanent_output = jsondecode(file("permanent_values.json"))

  tags = {
    Project = "Death Dice Stage"
  }
}


# Users interact with an API URL

module "game" {
  source                   = "./../../modules/game"
  prefix                   = local.prefix
  prefix_lower             = local.prefix_lower
  aws_account_id           = local.aws_account_id
  s3_database_history_name = local.permanent_output.s3_database_history_name
}

# When the game history is uploaded to S3, start SQL queries

module "analytics" {
  source                       = "./../../modules/analytics"
  aws_account_id               = local.aws_account_id
  prefix                       = local.prefix_analytics
  prefix_underscore            = local.prefix_analytics_underscore
  s3_database_history_arn      = module.game.s3_database_history_arn
  s3_database_history_name     = local.permanent_output.s3_database_history_name
  transform_finished_rule_arn  = module.game.transform_finished_rule_arn
  transform_finished_rule_name = module.game.transform_finished_rule_name
  cognito_user_pool_arn        = local.permanent_output.cognito_user_pool_arn
}

# Monitor using a cloudwatch dashboard 
module "game_monitoring" {
  source         = "./../../modules/game_monitoring"
  name           = local.prefix
  name_lower     = local.prefix_lower
  name_analytics = local.prefix_analytics
  project        = local.tags.Project
}

module "notifications" {
  source                 = "./../../modules/notifications"
  prefix                 = local.prefix
  admin_email            = local.admin_email
  game_created_rule_name = module.game.game_created_rule_name
}
