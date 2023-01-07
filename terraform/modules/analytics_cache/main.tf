terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  lambda_name = "${var.prefix}-CacheResult"
}

# When a query has been processed, fire a rule

resource "aws_cloudwatch_event_rule" "query_finished" {
  name        = "${var.prefix}-AthenaQuerySucceeded"
  description = "A query in Athena has succeeded"

  event_pattern = <<-EOF
    {
      "source": ["aws.athena"],
      "detail-type": ["Athena Query State Change"],
      "detail": {
        "workgroupName": ["${var.athena_workgroup_name}"],
        "currentState": ["SUCCEEDED"]
      }
    }
  EOF
}

resource "aws_cloudwatch_event_target" "query_finished" {
  rule      = aws_cloudwatch_event_rule.query_finished.name
  target_id = "SendToCloudWatch"
  arn       = aws_cloudwatch_log_group.query_finished.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
  # dead_letter_config {
  # arn = 
  # }
}

resource "aws_cloudwatch_log_group" "query_finished" {
  name              = "/aws/events/${aws_cloudwatch_event_rule.query_finished.name}"
  retention_in_days = 90
}


# The rule invokes a lambda to cache the result

resource "aws_cloudwatch_event_target" "cache" {
  rule      = aws_cloudwatch_event_rule.query_finished.name
  target_id = "InvokeCacheLambda"
  arn       = aws_lambda_function.cache.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
  # dead_letter_config {
  # arn = 
  # }
}

resource "aws_lambda_permission" "cache" {
  statement_id  = "AllowExecutionFromEventBus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cache.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.query_finished.arn
}


# The lambda reads the result and saves it to a cache

data "archive_file" "cache" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/cache_result.py"
  output_path = "${var.lambda_folder}/zip/cache_result.zip"
}

resource "aws_lambda_function" "cache" {
  filename         = data.archive_file.cache.output_path
  function_name    = local.lambda_name
  handler          = "cache_result.cache_result"
  role             = aws_iam_role.cache_result.arn
  runtime          = "python3.9"
  timeout          = 10
  source_code_hash = data.archive_file.cache.output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.cache]
  environment {
    variables = {
      "RESULT_CACHE_TABLE_NAME" : aws_dynamodb_table.cache.name,
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

data "aws_iam_policy_document" "get_query_result" {
  statement {
    actions = [
      "athena:GetQueryResults",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListMultipartUploadParts",
    ]
    effect = "Allow"
    resources = [
      var.athena_workgroup_arn,
      var.athena_s3_output_arn,
      "${var.athena_s3_output_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "write_cache" {
  statement {
    actions = [
      "dynamodb:ConditionCheckItem",
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    effect    = "Allow"
    resources = [aws_dynamodb_table.cache.arn]
  }
}

resource "aws_iam_role" "cache_result" {
  name                = "${var.prefix}-CacheAthenaResult"
  description         = "Allows Lambda to cache Athena results in DynamoDB"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "GetQueryResult"
    policy = data.aws_iam_policy_document.get_query_result.json
  }
  inline_policy {
    name   = "WriteResultsCache"
    policy = data.aws_iam_policy_document.write_cache.json
  }
}


# Lambda monitoring

resource "aws_cloudwatch_log_group" "cache" {
  name              = "/aws/lambda/${local.lambda_name}"
  retention_in_days = 90
}


# The cache holds the query results

resource "aws_dynamodb_table" "cache" {
  name         = var.prefix
  hash_key     = "account_id"
  range_key    = "date_id"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "account_id"
    type = "S"
  }
  attribute {
    name = "date_id"
    type = "S"
  }
}
