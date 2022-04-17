# Creates the a Lambda function, serverless execution that can be invoked by other components

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  connect_name      = "${var.prefix}Connect"
  disconnect_name   = "${var.prefix}Disconnect"
  send_message_name = "${var.prefix}SendMessage"
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
      "dynamodb:GetItem",
      "dynamodb:DeleteItem",
      "dynamodb:PutItem",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    effect    = "Allow"
    resources = [var.dynamo_db_arn]
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

# Create the functions using the source code zips

data "archive_file" "zip" {
  # Zips all source code in the src folder
  type        = "zip"
  source_dir  = "${var.lambda_folder}/src"
  output_path = "${var.lambda_folder}/lambda.zip"
}

resource "aws_lambda_function" "connect" {
  filename         = "${var.lambda_folder}/lambda.zip"
  function_name    = local.connect_name
  role             = aws_iam_role.role.arn
  handler          = "index.connect"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.connect]
}

resource "aws_lambda_function" "disconnect" {
  filename         = "${var.lambda_folder}/lambda.zip"
  function_name    = local.disconnect_name
  role             = aws_iam_role.role.arn
  handler          = "index.disconnect"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.disconnect]
}

resource "aws_lambda_function" "send_message" {
  filename         = "${var.lambda_folder}/lambda.zip"
  function_name    = local.send_message_name
  role             = aws_iam_role.role.arn
  handler          = "index.send_message"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.send_message]
}

# Logging for all lambda invocations, print statements will appear here

resource "aws_cloudwatch_log_group" "connect" {
  name              = "/aws/lambda/${local.connect_name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_log_group" "disconnect" {
  name              = "/aws/lambda/${local.disconnect_name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_log_group" "send_message" {
  name              = "/aws/lambda/${local.send_message_name}"
  retention_in_days = 3
}
