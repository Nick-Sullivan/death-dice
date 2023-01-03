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
    "StartQuery" = {
      name     = "${var.prefix}-StartQuery"
      filename = "start_query"
      handler  = "start_query.start_query"
      route    = "$start_query"
    },
    "CacheResult" = {
      name     = "${var.prefix}-CacheResult"
      filename = "cache_result"
      handler  = "cache_result.cache_result"
      route    = "$cache_result"
    },
    # "GetStatistics" = {
    #   name     = "${var.prefix}-GetStatistics"
    #   filename = "get_statistics"
    #   handler  = "get_statistics.get_statistics"
    #   route    = "$get_statistics"
    # },
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
  role             = aws_iam_role.role.arn
  runtime          = "python3.9"
  timeout          = 10
  source_code_hash = data.archive_file.all[each.key].output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
  environment {
    variables = {
      "PROJECT" : var.prefix,
      "WORKGROUP": var.athena_workgroup_name,
      "QUERY_ID": var.athena_query_id,
    }
  }
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

data "aws_iam_policy_document" "access_dynamodb" {
  # Allow Lambda to interact with the dynamo database
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

resource "aws_iam_role" "role" {
  # Permissions for the Lambda
  name                = "${var.prefix}LamdbaRole"
  description         = "Allows Lambda to query Athena"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "QueryAthena"
    policy = data.aws_iam_policy_document.query_athena.json
  }
  inline_policy {
    name   = "WriteResultsCache"
    policy = data.aws_iam_policy_document.access_dynamodb.json
  }
}
