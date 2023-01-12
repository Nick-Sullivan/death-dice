# Creates the Kinesis streaming from DynamoDB to S3

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# Stream DynamoDB changes to Kinesis data stream

resource "aws_kinesis_stream" "kinesis" {
  name        = var.prefix
  shard_count = 1
  # stream_mode_details {
  #   stream_mode = "ON_DEMAND"
  # }
}

resource "aws_dynamodb_kinesis_streaming_destination" "kinesis" {
  stream_arn = aws_kinesis_stream.kinesis.arn
  table_name = var.table_name
}

# Lambda to transform the data stream

resource "aws_cloudwatch_log_group" "transform" {
  name              = "/aws/lambda/${var.prefix}-Extract"
  retention_in_days = 90
}

data "archive_file" "transform" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/extract.py"
  output_path = "${var.lambda_folder}/zip/extract.zip"
}

resource "aws_lambda_function" "transform" {
  filename         = "${var.lambda_folder}/zip/extract.zip"
  function_name    = "${var.prefix}-Extract"
  handler          = "extract.extract"
  role             = aws_iam_role.lambda_role.arn
  runtime          = "python3.9"
  timeout          = 10
  source_code_hash = data.archive_file.transform.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.transform]
  # environment {
  #   variables = {
  #     # "PROJECT" : var.prefix,
  #     # "GATEWAY_URL" : var.gateway_url,
  #   }
  # }
}

data "aws_iam_policy_document" "lambda_assume_role" {
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

resource "aws_iam_role" "lambda_role" {
  # Permissions for the Lambda
  name                = "${var.prefix}LamdbaTransformRole"
  description         = "Allows Lambda to write to Cloudwatch"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
}

# S3 bucket to store the output

resource "aws_s3_bucket" "kinesis" {
  bucket = "${var.prefix_lower}-database-history"
}

resource "aws_s3_bucket_acl" "kinesis" {
  bucket = aws_s3_bucket.kinesis.id
  acl    = "private"
}

# Connect Kinesis data stream into Kinesis delivery stream, and into S3

data "aws_iam_policy_document" "kinesis_assume_role" {
  # Allow Kinesis delivery stream to assume a role so it can execute
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "kinesis_list_stream" {
  # Allow Kinesis delivery stream to read from the data stream
  statement {
    actions = [
      "kinesis:DescribeStream",
      "kinesis:GetShardIterator",
      "kinesis:GetRecords",
      "kinesis:ListShards",
    ]
    effect    = "Allow"
    resources = [aws_kinesis_stream.kinesis.arn]
  }
}

data "aws_iam_policy_document" "kinesis_upload_to_s3" {
  # Allow Kinesis delivery to upload to S3 bucket
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    effect = "Allow"
    resources = [
      aws_s3_bucket.kinesis.arn,
      "${aws_s3_bucket.kinesis.arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "kinesis_invoke_lambda" {
  # Allow Kinesis to invoke the transformation lambda
  statement {
    actions = [
      "lambda:InvokeFunction",
      "lambda:GetFunctionConfiguration",
    ]
    effect = "Allow"
    resources = [
      aws_lambda_function.transform.arn,
    ]
  }
}

resource "aws_iam_role" "kinesis_role" {
  # Permissions for the Kinesis delivery stream
  name               = "${var.prefix}FirehoseRole"
  description        = "Allows Firehose to invoke transform lambdas and write to S3"
  assume_role_policy = data.aws_iam_policy_document.kinesis_assume_role.json
  inline_policy {
    name   = "ListKinesisDataStream"
    policy = data.aws_iam_policy_document.kinesis_list_stream.json
  }
  inline_policy {
    name   = "InvokeLambda"
    policy = data.aws_iam_policy_document.kinesis_invoke_lambda.json
  }
  inline_policy {
    name   = "UploadToS3"
    policy = data.aws_iam_policy_document.kinesis_upload_to_s3.json
  }
}

resource "aws_kinesis_firehose_delivery_stream" "s3_stream" {
  # TODO - add cloudwatch, and backup
  name        = var.prefix
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.kinesis.arn
    role_arn           = aws_iam_role.kinesis_role.arn
  }


  extended_s3_configuration {
    role_arn            = aws_iam_role.kinesis_role.arn
    bucket_arn          = aws_s3_bucket.kinesis.arn
    buffer_size         = 64 # MB (minimum 64)
    buffer_interval     = 60 # seconds
    prefix              = "data/table=!{partitionKeyFromLambda:table}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    error_output_prefix = "errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/!{firehose:error-output-type}/"

    # s3_backup_mode = "Enabled"
    # s3_backup_configuration = {
    # }

    # cloudwatch_logging_options {
    #   enabled         = true
    #   log_group_name  = "/aws/kinesisfirehose/${local.stream_name}"
    #   log_stream_name = "S3Delivery"
    # }

    dynamic_partitioning_configuration {
      enabled = true
    }

    # Many of these options can only be applied if the stream is destroyed and created
    processing_configuration {
      enabled = "true"
      processors {
        type = "Lambda"
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = aws_lambda_function.transform.arn
        }
        parameters {
          parameter_name  = "BufferSizeInMBs"
          parameter_value = 1
        }
        parameters {
          parameter_name  = "BufferIntervalInSeconds"
          parameter_value = 60
        }
      }

      processors {
        type = "AppendDelimiterToRecord"
      }
    }
  }

  # Terraform thinks the parameters has always changed
  # https://github.com/hashicorp/terraform-provider-aws/issues/4392
  lifecycle {
    ignore_changes = [
      extended_s3_configuration[0].processing_configuration[0].processors[0].parameters,
    ]
  }
}
