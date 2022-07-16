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
    "Connect" = {
      name    = "${var.prefix}-Connect"
      filename = "connect"
      handler = "connect.connect"
      route   = "$connect"
    },
    "Disconnect" = {
      name    = "${var.prefix}-Disconnect"
      filename = "disconnect"
      handler = "disconnect.disconnect"
      route   = "$disconnect"
    },
    "CreateGame" = {
      name    = "${var.prefix}-CreateGame"
      filename = "create_game"
      handler = "create_game.create_game"
      route   = "createGame"
    },
    "JoinGame" = {
      name    = "${var.prefix}-JoinGame"
      filename = "join_game"
      handler = "join_game.join_game"
      route   = "joinGame"
    },
    "NewRound" = {
      name    = "${var.prefix}-NewRound"
      filename = "new_round"
      handler = "new_round.new_round"
      route   = "newRound"
    },
    "RollDice" = {
      name    = "${var.prefix}-RollDice"
      filename = "roll_dice"
      handler = "roll_dice.roll_dice"
      route   = "rollDice"
    },
    "SetNickname" = {
      name    = "${var.prefix}-SetNickname"
      filename = "set_nickname"
      handler = "set_nickname.set_nickname"
      route   = "setNickname"
    }
  }
}

# Logging for all lambda invocations, print statements will appear here

resource "aws_cloudwatch_log_group" "all" {
  for_each          = local.lambdas
  name              = "/aws/lambda/${each.value.name}"
  retention_in_days = 90
}

# Create the functions using the source code zips

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${var.lambda_folder}/layer"
  excludes    = ["__pycache__.py"]
  output_path = "${var.lambda_folder}/zip/layer.zip"
}

data "archive_file" "all" {
  for_each = local.lambdas
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/${each.value.filename}.py"
  output_path = "${var.lambda_folder}/zip/${each.value.filename}.zip"
}

resource "aws_lambda_layer_version" "layer" {
  filename            = "${var.lambda_folder}/zip/layer.zip"
  layer_name          = "${var.prefix}-Logic"
  compatible_runtimes = ["python3.9"]
  source_code_hash    = data.archive_file.layer.output_base64sha256
}

resource "aws_lambda_function" "all" {
  for_each         = local.lambdas
  filename         = "${var.lambda_folder}/zip/${each.value.filename}.zip"
  function_name    = each.value.name
  handler          = each.value.handler
  layers           = [aws_lambda_layer_version.layer.arn]
  role             = aws_iam_role.role.arn
  runtime          = "python3.9"
  timeout          = 10
  source_code_hash = data.archive_file.all[each.key].output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
  environment {
    variables = {
      "PROJECT" : var.prefix,
      "GATEWAY_URL" : var.gateway_url,
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
    resources = var.table_arns
  }
}

data "aws_iam_policy_document" "api_connections" {
  # Allow Lambda to send messages to API gateway connections
  # TODO - restrict resources. We don't know the Gateway ARN because it's not made yet :(
  statement {
    actions = [
      "execute-api:ManageConnections",
    ]
    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role" "role" {
  # Permissions for the Lambda
  name                = "${var.prefix}LamdbaRole"
  description         = "Allows Lambda to write to Cloudwatch"
  assume_role_policy  = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "DynamoWriteAccess"
    policy = data.aws_iam_policy_document.access_dynamodb.json
  }
  inline_policy {
    name   = "ApiGatewayConnections"
    policy = data.aws_iam_policy_document.api_connections.json
  }
}
