# Extracts data from DynamoDB to S3

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  s3_arn = "arn:aws:s3:::${var.s3_name}"
}

# DynamoDB stream triggers an extraction lambda

resource "aws_lambda_event_source_mapping" "extract" {
  event_source_arn  = var.stream_arn
  function_name     = aws_lambda_function.transform.arn
  starting_position = "LATEST"
  batch_size = 1000
  maximum_batching_window_in_seconds = 60
}

# Transformation Lambda converts the data and uploads to S3

data "archive_file" "transform" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/transform.py"
  output_path = "${var.lambda_folder}/zip/transform.zip"
}

resource "aws_lambda_function" "transform" {
  filename         = "${var.lambda_folder}/zip/transform.zip"
  function_name    = "${var.prefix}-Transform"
  handler          = "transform.transform"
  role             = aws_iam_role.transform.arn
  runtime          = "python3.9"
  memory_size      = 258  # MB
  timeout          = 10
  reserved_concurrent_executions = 1
  source_code_hash = data.archive_file.transform.output_base64sha256
  layers = ["arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python39:2"]
  depends_on       = [aws_cloudwatch_log_group.transform]
  environment {
    variables = {
      "PROJECT" : var.prefix,
      "BUCKET_NAME" : var.s3_name,
    }
  }
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "read_dynamodb" {
  statement {
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]
    effect    = "Allow"
    resources = [
      var.stream_arn,
    ]
  }
}

data "aws_iam_policy_document" "upload_to_s3" {
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    effect    = "Allow"
    resources = [
      local.s3_arn,
      "${local.s3_arn}/*",
    ]
  }
}

resource "aws_iam_role" "transform" {
  name                = "${var.prefix}LamdbaTransformRole"
  description         = "Allows Lambda to read from SQS and upload to S3"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadStream"
    policy = data.aws_iam_policy_document.read_dynamodb.json
  }
  inline_policy {
    name   = "S3Upload"
    policy = data.aws_iam_policy_document.upload_to_s3.json
  }
}

resource "aws_cloudwatch_log_group" "transform" {
  name              = "/aws/lambda/${var.prefix}-Transform"
  retention_in_days = 90
}

