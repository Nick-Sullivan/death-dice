# Creates the database

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_dynamodb_table" "players" {
  # note - doesn't have autoscaling
  name           = "${var.prefix}Players"
  hash_key       = "Id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
  global_secondary_index {
    name            = "GameIndex"
    hash_key        = "GameId"
    write_capacity  = 5
    read_capacity   = 5
    projection_type = "ALL"  # allows all other columns to be accessed using this index - but uses more data
  }

  attribute {
    name = "Id"
    type = "S"
  }

  attribute {
    name = "GameId"
    type = "S"
  }
}

resource "aws_dynamodb_table" "games" {
  name           = "${var.prefix}Games"
  hash_key       = "Id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "Id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "rolls" {
  name           = "${var.prefix}Rolls"
  hash_key       = "Id"
  # sort_key       = "PlayerId"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
  global_secondary_index {
    name            = "GameIndex"
    hash_key        = "GameId"
    write_capacity  = 5
    read_capacity   = 5
    projection_type = "ALL"  # allows all other columns to be accessed using this index - but uses more data
  }

  attribute {
    name = "Id"
    type = "S"
  }

  attribute {
    name = "GameId"
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

data "aws_iam_policy_document" "rolls" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.rolls.arn]
  }
}
