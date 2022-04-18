# Creates the a Lambda function, serverless execution that can be invoked by other components

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_dynamodb_table" "lobbies" {
  # note - doesn't have autoscaling
  name           = "UncomfortableQuestionsLobbies"
  hash_key       = "ConnectionId"
  # range_key      = "LobbyId"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  # To efficiently search for lobbies, we need to set it as a key.
  global_secondary_index {
    name = "LobbyIndex"
    hash_key = "LobbyId"
    write_capacity = 5
    read_capacity = 5
    projection_type = "KEYS_ONLY"
    # non_key_attributes = ["description"]
  }

  # ttl {
  #   attribute_name = "TimeToLive"
  #   enabled = true
  # }
  attribute {
    name = "ConnectionId"
    type = "S"
  }

  attribute {
    name = "LobbyId"
    type = "S"
  }

}

data "aws_iam_policy_document" "inline_policy" {
  statement {
    actions   = ["dynamodb:PutItem"]
    effect    = "Allow"
    resources = [aws_dynamodb_table.lobbies.arn]
  }
}
