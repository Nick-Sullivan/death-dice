# Creates the a Lambda function, serverless execution that can be invoked by other components

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

data "archive_file" "zip" {
  # Zips all source code in the src folder
  type        = "zip"
  source_dir  = "${var.lambda_folder}/src"
  output_path = "${var.lambda_folder}/lambda.zip"
}

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

data "aws_iam_policy_document" "inline_policy" {
  # Allow Lambda to interact with the dynamo database
  statement {
    actions   = [
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

resource "aws_iam_role" "role" {
  # Permissions for the Lambda
  name                = "${var.name}LamdbaRole"
  description         = "Allows Lambda to write to Cloudwatch"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "DynamoDBWriteAccess"
    policy = data.aws_iam_policy_document.inline_policy.json
  }
}



resource "aws_lambda_function" "function" {
  # Create the function using the source code in the zip
  filename         = "${var.lambda_folder}/lambda.zip"
  function_name    = var.name
  role             = aws_iam_role.role.arn
  handler          = "index.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.zip.output_base64sha256
  depends_on = [
    aws_cloudwatch_log_group.function
  ]
}

resource "aws_cloudwatch_log_group" "function" {
  # Logging for all lambda invocations
  name              = "/aws/lambda/${var.name}"
  retention_in_days = 30
}
