# Creates the Lambda functions, serverless execution that can be invoked by other components

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  lambdas = {
    "Connect" = {
      name    = "${var.prefix}Connect"
      handler = "index.connect"
      route   = "$connect"
    },
    "Disconnect" = {
      name    = "${var.prefix}Disconnect"
      handler = "index.disconnect"
      route   = "$disconnect"
    },
    "CreateGame" = {
      name    = "${var.prefix}CreateGame"
      handler = "index.create_game"
      route   = "createGame"
    },
    "JoinGame" = {
      name    = "${var.prefix}JoinGame"
      handler = "index.join_game"
      route   = "joinGame"
    },
    "SendMessage" = {
      name    = "${var.prefix}SendMessage"
      handler = "index.send_message"
      route   = "sendMessage"
    },
    "SetNickname" = {
      name    = "${var.prefix}SetNickname"
      handler = "index.set_nickname"
      route   = "setNickname"
    }
  }
}

# Logging for all lambda invocations, print statements will appear here

resource "aws_cloudwatch_log_group" "all" {
  for_each          = local.lambdas
  name              = "/aws/lambda/${each.value.name}"
  retention_in_days = 3
}

# Create the functions using the source code zips

data "archive_file" "zip" {
  # Zips all source code in the src folder
  type        = "zip"
  source_dir  = "${var.lambda_folder}/src"
  output_path = "${var.lambda_folder}/lambda.zip"
}

resource "aws_lambda_function" "all" {
  for_each         = local.lambdas
  filename         = "${var.lambda_folder}/lambda.zip"
  function_name    = each.value.name
  handler          = each.value.handler
  role             = aws_iam_role.role.arn
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
}

# Permissions

data "aws_iam_policy_document" "assume_role" {
  # Allow Lambda to assume a role so it can execute
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "access_dynamodb" {
  # Allow Lambda to interact with the dynamo database
  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    effect    = "Allow"
    resources = var.table_arns
  }
}

data "aws_iam_policy_document" "api_connections" {
  # Allow Lambda to send messages to API gateway connections
  # TODO - restrict resources
  statement {
    actions = [
      "execute-api:ManageConnections",
    ]
    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role" "role" {
  # Permissions for the Lambda
  name                = "${var.prefix}LamdbaRole"
  description         = "Allows Lambda to write to Cloudwatch"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "DynamoWriteAccess"
    policy = data.aws_iam_policy_document.access_dynamodb.json
  }
  inline_policy {
    name   = "ApiGatewayConnections"
    policy = data.aws_iam_policy_document.api_connections.json
  }
}