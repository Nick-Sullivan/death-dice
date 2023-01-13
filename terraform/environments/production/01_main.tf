terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.48.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "death_dice/production/terraform.tfstate"
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

  prefix            = "DeathDice"
  prefix_lower      = "death-dice"
  prefix_underscore = "death_dice"

  prefix_analytics            = "${local.prefix}Analytics"
  prefix_analytics_underscore = "${local.prefix_underscore}_analytics"

  permanent_output = jsondecode(file("permanent_values.json"))

  tags = {
    Project = "Death Dice"
  }
}
