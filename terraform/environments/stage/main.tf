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
