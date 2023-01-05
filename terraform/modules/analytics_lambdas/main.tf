terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  lambdas = {
    "StartQuery" = {
      name     = "${var.prefix}-StartQuery"
      filename = "start_query"
      handler  = "start_query.start_query"
      route    = "$start_query"
      role = aws_iam_role.start_query.arn
      variables = {
        "QUERY_ID": var.athena_query_id,
      }
    },
    "CacheResult" = {
      name     = "${var.prefix}-CacheResult"
      filename = "cache_result"
      handler  = "cache_result.cache_result"
      route    = "$cache_result"
      role = aws_iam_role.cache_result.arn
      variables = {
        "RESULT_CACHE_TABLE_NAME": var.dynamodb_table_name,
      }
    },
    "GetStatistics" = {
      name     = "${var.prefix}-GetStatistics"
      filename = "get_statistics"
      handler  = "get_statistics.get_statistics"
      route    = "$get_statistics"
      role = aws_iam_role.get_statistics.arn
      variables = {
        "RESULT_CACHE_TABLE_NAME": var.dynamodb_table_name,
      }
    },
  }
}

# Logging for all lambda invocations, print statements will appear here

resource "aws_cloudwatch_log_group" "all" {
  for_each          = local.lambdas
  name              = "/aws/lambda/${each.value.name}"
  retention_in_days = 90
}

# Create the functions using the source code zips

data "archive_file" "all" {
  for_each    = local.lambdas
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/${each.value.filename}.py"
  output_path = "${var.lambda_folder}/zip/${each.value.filename}.zip"
}

resource "aws_lambda_function" "all" {
  for_each         = local.lambdas
  filename         = "${var.lambda_folder}/zip/${each.value.filename}.zip"
  function_name    = each.value.name
  handler          = each.value.handler
  role             = each.value.role
  runtime          = "python3.9"
  timeout          = 10
  source_code_hash = data.archive_file.all[each.key].output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
  environment {
    variables = each.value.variables
  }
}

# Permissions - common

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

# Permissions - start Athena query

data "aws_iam_policy_document" "query_athena" {
  # Allow Lambda to perform queries in Athena
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
      "glue:GetTable",
    ]
    effect    = "Allow"
    resources = [
      var.athena_workgroup_arn,
      var.athena_s3_output_arn,
      "${var.athena_s3_output_arn}/*",
      "arn:aws:glue:ap-southeast-2:314077822992:catalog",
      "arn:aws:glue:ap-southeast-2:314077822992:database/${var.glue_database_id}",
      var.glue_connection_table_arn,
      var.glue_game_table_arn,
    ]
  }
}

resource "aws_iam_role" "start_query" {
  # Permissions for the Lambda
  name                = "${var.prefix}-QueryAthena"
  description         = "Allows Lambda to start queries in Athena"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "QueryAthena"
    policy = data.aws_iam_policy_document.query_athena.json
  }
}

# Permissions - cache results to DynamoDB

data "aws_iam_policy_document" "get_query_result" {
  statement {
    actions = [
      "athena:GetQueryResults",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListMultipartUploadParts",
    ]
    effect    = "Allow"
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
    resources = [var.dynamodb_table_arn]
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

# Permissions - read DynamoDB cache

data "aws_iam_policy_document" "read_cache" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan",
    ]
    effect    = "Allow"
    resources = [var.dynamodb_table_arn]
  }
}

resource "aws_iam_role" "get_statistics" {
  name                = "${var.prefix}-GetStatistics"
  description         = "Allows Lambda to read cached results in DynamoDB"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadResultsCache"
    policy = data.aws_iam_policy_document.read_cache.json
  }
}
