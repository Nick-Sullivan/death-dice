
locals {
  lambdas = {
    "GetStatistics" = {
      name     = "${var.prefix}-GetStatistics"
      filename = "get_statistics"
      handler  = "get_statistics.get_statistics"
      route    = "$get_statistics"
      role     = aws_iam_role.read_cache.arn
      variables = {
        "RESULT_CACHE_TABLE_NAME" : var.dynamodb_table_name,
      }
    },
    "GetConfig" = {
      name     = "${var.prefix}-GetConfig"
      filename = "get_config"
      handler  = "get_config.get_config"
      route    = "$get_config"
      role     = aws_iam_role.read_config.arn
      variables = {
        "RESULT_CONFIG_TABLE_NAME" : var.dynamodb_table_config_name,
      }
    },
    "SetConfig" = {
      name     = "${var.prefix}-SetConfig"
      filename = "set_config"
      handler  = "set_config.set_config"
      route    = "$set_config"
      role     = aws_iam_role.write_config.arn
      variables = {
        "RESULT_CONFIG_TABLE_NAME" : var.dynamodb_table_config_name,
      }
    },
  }
}


# Lambdas load data from the cache and return it in a nice format

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
  runtime          = "python3.12"
  timeout          = 10
  source_code_hash = data.archive_file.all[each.key].output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
  environment {
    variables = each.value.variables
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

data "aws_iam_policy_document" "read_cache" {
  statement {
    actions = [
      "dynamodb:Query",
    ]
    effect    = "Allow"
    resources = [var.dynamodb_table_arn]
  }
}

data "aws_iam_policy_document" "read_config" {
  statement {
    actions = [
      "dynamodb:Query",
      "dynamodb:Scan",
    ]
    effect    = "Allow"
    resources = [var.dynamodb_table_config_arn]
  }
}

data "aws_iam_policy_document" "write_config" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]
    effect    = "Allow"
    resources = [var.dynamodb_table_config_arn]
  }
}

resource "aws_iam_role" "read_cache" {
  name                = "${var.prefix}-ReadCache"
  description         = "Allows Lambda to read cached results in DynamoDB"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadResultsCache"
    policy = data.aws_iam_policy_document.read_cache.json
  }
}

resource "aws_iam_role" "read_config" {
  name                = "${var.prefix}-ReadConfig"
  description         = "Allows Lambda to read config in DynamoDB"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadConfig"
    policy = data.aws_iam_policy_document.read_config.json
  }
}

resource "aws_iam_role" "write_config" {
  name                = "${var.prefix}-WriteConfig"
  description         = "Allows Lambda to write config in DynamoDB"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "WriteConfig"
    policy = data.aws_iam_policy_document.write_config.json
  }
}

# Lambda logging

resource "aws_cloudwatch_log_group" "all" {
  for_each          = local.lambdas
  name              = "/aws/lambda/${each.value.name}"
  retention_in_days = 90
}

