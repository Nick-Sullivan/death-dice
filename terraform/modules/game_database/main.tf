# Creates the database

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_dynamodb_table" "death_dice" {
  name             = var.prefix
  hash_key         = "id"
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "websocket" {
  name             = "${var.prefix}Websocket"
  hash_key         = "connection_id"
  billing_mode     = "PAY_PER_REQUEST"
  attribute {
    name = "connection_id"
    type = "S"
  }
}
