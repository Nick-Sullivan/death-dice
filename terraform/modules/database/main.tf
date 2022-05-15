# Creates the database

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  read_capacity = 10
  write_capacity = 10
}

resource "aws_dynamodb_table" "players" {
  # note - doesn't have autoscaling
  name           = "${var.prefix}Players"
  hash_key       = "id"
  billing_mode   = "PROVISIONED"
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity

  # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
  # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-indexes-general.html
  global_secondary_index {
    name            = "game_index"
    hash_key        = "game_id"
    read_capacity   = local.read_capacity
    write_capacity  = local.write_capacity
    projection_type = "ALL"
  }

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "game_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "games" {
  name           = "${var.prefix}Games"
  hash_key       = "id"
  billing_mode   = "PROVISIONED"
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity

  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "turns" {
  name     = "${var.prefix}Turns"
  hash_key = "id"
  billing_mode   = "PROVISIONED"
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity

  global_secondary_index {
    name            = "game_index"
    hash_key        = "game_id"
    read_capacity   = local.read_capacity
    write_capacity  = local.write_capacity
    projection_type = "ALL"
  }

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "game_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "rolls" {
  name     = "${var.prefix}Rolls"
  hash_key = "id"
  billing_mode   = "PROVISIONED"
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity

  global_secondary_index {
    name            = "game_index"
    hash_key        = "game_id"
    read_capacity   = local.read_capacity
    write_capacity  = local.write_capacity
    projection_type = "ALL"
  }

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "game_id"
    type = "S"
  }
}

# Permissions
# note - if you make a change to this, you will need to destroy & reapply

data "aws_iam_policy_document" "players" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.players.arn]
  }
}

data "aws_iam_policy_document" "games" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.games.arn]
  }
}

data "aws_iam_policy_document" "turns" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.turns.arn]
  }
}

data "aws_iam_policy_document" "rolls" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.rolls.arn]
  }
}
