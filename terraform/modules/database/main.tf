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

# Permissions
# note - if you make a change to this, you will need to destroy & reapply

data "aws_iam_policy_document" "death_dice" {
  statement {
    actions   = [
      "dynamodb:PutItem",
    ]
    effect    = "Allow"
    resources = [aws_dynamodb_table.death_dice.arn]
  }
}
