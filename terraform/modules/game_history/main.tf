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
  extract_name = "${var.prefix}-Extract"
  transform_name = "${var.prefix}-Transform"
}

# DynamoDB stream triggers an extraction lambda

resource "aws_lambda_event_source_mapping" "extract" {
  event_source_arn  = var.stream_arn
  function_name     = aws_lambda_function.extract.arn
  starting_position = "LATEST"
  batch_size = 1000
  maximum_batching_window_in_seconds = 300  # max 300
}

# Extract lambda uploads the data to SQS, to batch the data

data "archive_file" "extract" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/extract.py"
  output_path = "${var.lambda_folder}/zip/extract.zip"
}

resource "aws_lambda_function" "extract" {
  filename         = "${var.lambda_folder}/zip/extract.zip"
  function_name    = local.extract_name
  handler          = "extract.extract"
  role             = aws_iam_role.extract.arn
  runtime          = "python3.9"
  memory_size      = 128  # MB
  timeout          = 10
  reserved_concurrent_executions = 1
  source_code_hash = data.archive_file.extract.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.extract]
  environment {
    variables = {
      "QUEUE_URL" : aws_sqs_queue.extract.url,
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

data "aws_iam_policy_document" "upload_to_sqs" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]
    effect    = "Allow"
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

resource "aws_cloudwatch_log_group" "extract" {
  name              = "/aws/lambda/${local.extract_name}"
  retention_in_days = 90
}

resource "aws_sqs_queue" "extract" {
  name                      = local.extract_name
}

# A scheduled event starts a transformation lambda

resource "aws_cloudwatch_event_rule" "transform" {
  name        = local.transform_name
  description = "Transform periodically"
  schedule_expression = "cron(30 0 * * ? *)"  # 11:00am adelaide time, every day
}


resource "aws_cloudwatch_event_target" "transform" {   # comment to stop all transformations
  rule      = aws_cloudwatch_event_rule.transform.name
  target_id = "InvokeTransformLambda"
  arn       = aws_lambda_function.transform.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_lambda_permission" "transform" {
  statement_id  = "AllowExecutionFromEventBus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transform.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.transform.arn
}


# resource "aws_lambda_event_source_mapping" "transform" {  # No scheduling, just straight invoke
#   event_source_arn  = aws_sqs_queue.extract.arn
#   function_name     = aws_lambda_function.transform.arn
#   batch_size = 1000
#   maximum_batching_window_in_seconds = 60  # max 300
# }

# Transformation Lambda converts the data and uploads to S3

data "archive_file" "transform" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/transform.py"
  output_path = "${var.lambda_folder}/zip/transform.zip"
}

resource "aws_lambda_function" "transform" {
  filename         = "${var.lambda_folder}/zip/transform.zip"
  function_name    = local.transform_name
  handler          = "transform.transform"
  role             = aws_iam_role.transform.arn
  runtime          = "python3.9"
  memory_size      = 512  # MB
  timeout          = 10
  reserved_concurrent_executions = 1
  source_code_hash = data.archive_file.transform.output_base64sha256
  layers = ["arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python39:2"]
  depends_on       = [aws_cloudwatch_log_group.transform]
  environment {
    variables = {
      "PROJECT" : var.prefix,
      "BUCKET_NAME" : var.s3_name,
      "QUEUE_URL" : aws_sqs_queue.extract.url,
    }
  }
}

# data "archive_file" "transform" {
#   type        = "zip"
#   source_file = "${var.lambda_folder}/handler/transform.js"
#   output_path = "${var.lambda_folder}/zip/transform.zip"
# }

# resource "aws_lambda_function" "transform" {
#   filename         = "${var.lambda_folder}/zip/transform.zip"
#   function_name    = local.transform_name
#   handler          = "transform.transform"
#   role             = aws_iam_role.transform.arn
#   runtime          = "nodejs12.x"
#   # runtime          = "nodejs18.x"
#   memory_size      = 128  # MB
#   timeout          = 10
#   reserved_concurrent_executions = 1
#   source_code_hash = data.archive_file.transform.output_base64sha256
#   # layers = ["arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python39:2"]
#   depends_on       = [aws_cloudwatch_log_group.transform]
#   environment {
#     variables = {
#       "PROJECT" : var.prefix,
#       "BUCKET_NAME" : var.s3_name,
#     }
#   }
# }

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

data "aws_iam_policy_document" "read_sqs" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    effect    = "Allow"
    resources = [
      aws_sqs_queue.extract.arn,
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
  name                = "${var.prefix}-LamdbaTransformRole"
  description         = "Allows Lambda to read from SQS and upload to S3"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadSqs"
    policy = data.aws_iam_policy_document.read_sqs.json
  }
  inline_policy {
    name   = "S3Upload"
    policy = data.aws_iam_policy_document.upload_to_s3.json
  }
}

resource "aws_cloudwatch_log_group" "transform" {
  name              = "/aws/lambda/${local.transform_name}"
  retention_in_days = 90
}

