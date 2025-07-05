terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


locals {
  lambda_name = "${var.prefix}-StartQuery"
}


# When the game history has finished uploading to S3, invokes a lambda for processing

resource "aws_cloudwatch_event_target" "start_query" {
  rule      = var.transform_finished_rule_name
  target_id = "InvokeStartQueryLambda"
  arn       = aws_lambda_function.start_query.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_lambda_permission" "start_query" {
  statement_id  = "AllowExecutionFromEventBus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_query.function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.transform_finished_rule_arn
}


# The lambda starts an Athena query

data "archive_file" "start_query" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/start_query.py"
  output_path = "${var.lambda_folder}/zip/start_query.zip"
}

resource "aws_lambda_function" "start_query" {
  filename         = data.archive_file.start_query.output_path
  function_name    = local.lambda_name
  handler          = "start_query.start_query"
  role             = aws_iam_role.start_query.arn
  runtime          = "python3.12"
  timeout          = 10
  source_code_hash = data.archive_file.start_query.output_base64sha256
  layers           = ["arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-boto3:20"] # newer boto3
  depends_on       = [aws_cloudwatch_log_group.start_query]
  environment {
    variables = {
      "QUERY_ID" : aws_athena_named_query.all_stats_per_account.id,
    }
  }
}


# Lambda permissions

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "query_athena" {
  statement {
    actions = [
      "athena:CancelQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:GetWorkGroup",
      "athena:GetNamedQuery",
      "athena:ListNamedQueries",
      "athena:StartQueryExecution",
      "athena:StopQueryExecution",
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
      "glue:CreatePartition",
      "glue:GetPartition",
      "glue:GetTable",
    ]
    effect = "Allow"
    resources = [
      aws_athena_workgroup.athena.arn,
      var.s3_arn,
      "${var.s3_arn}/*",
      "arn:aws:glue:ap-southeast-2:${var.aws_account_id}:catalog",
      "arn:aws:glue:ap-southeast-2:${var.aws_account_id}:database/${aws_athena_database.athena.id}",
      aws_glue_catalog_table.connection.arn,
      aws_glue_catalog_table.game.arn,
    ]
  }
}

resource "aws_iam_role" "start_query" {
  name                = "${var.prefix}-QueryAthena"
  description         = "Allows Lambda to start queries in Athena"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "QueryAthena"
    policy = data.aws_iam_policy_document.query_athena.json
  }
}


# Lambda logging

resource "aws_cloudwatch_log_group" "start_query" {
  name              = "/aws/lambda/${local.lambda_name}"
  retention_in_days = 90
}
