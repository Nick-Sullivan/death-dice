terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  extract_name      = "${var.prefix}-Extract"
  extract_fail_name = "${var.prefix}-ExtractDeadLetterQueue"
}


# DynamoDB stream triggers an extraction lambda

resource "aws_lambda_event_source_mapping" "extract" {
  event_source_arn                   = var.stream_arn
  function_name                      = aws_lambda_function.extract.function_name
  starting_position                  = "LATEST"
  batch_size                         = 1000
  maximum_batching_window_in_seconds = 300 # max 300
}


# Extract lambda uploads the data to SQS, to batch the data

data "archive_file" "extract" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/extract.py"
  output_path = "${var.lambda_folder}/zip/extract.zip"
}

resource "aws_lambda_function" "extract" {
  filename                       = "${var.lambda_folder}/zip/extract.zip"
  function_name                  = local.extract_name
  handler                        = "extract.extract"
  role                           = aws_iam_role.extract.arn
  runtime                        = "python3.9"
  memory_size                    = 128 # MB
  timeout                        = 10
  reserved_concurrent_executions = 1
  source_code_hash               = data.archive_file.extract.output_base64sha256
  depends_on                     = [aws_cloudwatch_log_group.extract]
  environment {
    variables = {
      "QUEUE_URL" : aws_sqs_queue.extract.url,
    }
  }
}


# Lambda permissions

data "aws_iam_policy_document" "read_dynamodb" {
  statement {
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]
    effect = "Allow"
    resources = [
      var.stream_arn,
    ]
  }
}

data "aws_iam_policy_document" "upload_to_sqs" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]
    effect = "Allow"
    resources = [
      aws_sqs_queue.extract.arn,
    ]
  }
}

resource "aws_iam_role" "extract" {
  name                = "${var.prefix}-LamdbaExtractRole"
  description         = "Allows Lambda to read from DynamoDB and upload to SQS"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadStream"
    policy = data.aws_iam_policy_document.read_dynamodb.json
  }
  inline_policy {
    name   = "SqsUpload"
    policy = data.aws_iam_policy_document.upload_to_sqs.json
  }
}


# Cloudwatch logs

resource "aws_cloudwatch_log_group" "extract" {
  name              = "/aws/lambda/${local.extract_name}"
  retention_in_days = 90
}


# SQS queue holds all the data until we want to transform. If transformation fails, messages will go to the dead letter queue.

resource "aws_sqs_queue" "extract" {
  name                      = local.extract_name
  message_retention_seconds = 14 * 24 * 60 * 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.extract_dead_letter.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "extract_dead_letter" {
  name                      = local.extract_fail_name
  message_retention_seconds = 14 * 24 * 60 * 60
}

resource "aws_sqs_queue_redrive_allow_policy" "extract" {
  queue_url = aws_sqs_queue.extract_dead_letter.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.extract.arn]
  })
}