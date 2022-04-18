# Creates the database

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_dynamodb_table" "connections" {
  # note - doesn't have autoscaling
  name           = "${var.prefix}Connections"
  hash_key       = "Id"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  global_secondary_index {
    name            = "GameIndex"
    hash_key        = "GameId"
    write_capacity  = 5
    read_capacity   = 5
    projection_type = "KEYS_ONLY"
    # non_key_attributes = ["description"]
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

# Permissions

data "aws_iam_policy_document" "connections" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.connections.arn]
  }
}

data "aws_iam_policy_document" "games" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.games.arn]
  }
}
