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
      name     = "${var.prefix}-Connect"
      filename = "handler"
      handler  = "handler.connect"
      route    = "$connect"
    },
    "GetSession" = {
      name     = "${var.prefix}-GetSession"
      filename = "handler"
      handler  = "handler.get_session"
      route    = "getSession"
    },
    "SetSession" = {
      name     = "${var.prefix}-SetSession"
      filename = "handler"
      handler  = "handler.set_session"
      route    = "setSession"
    },
    "DestroySession" = {
      name     = "${var.prefix}-DestroySession"
      filename = "handler"
      handler  = "handler.destroy_session"
      route    = "destroySession"
    },
    "Disconnect" = {
      name     = "${var.prefix}-Disconnect"
      filename = "handler"
      handler  = "handler.disconnect"
      route    = "$disconnect"
    },
    "CreateGame" = {
      name     = "${var.prefix}-CreateGame"
      filename = "handler"
      handler  = "handler.create_game"
      route    = "createGame"
    },
    "Heartbeat" = {
      name     = "${var.prefix}-Heartbeat"
      filename = "handler"
      handler  = "handler.heartbeat"
      route    = "heartbeat"
    },
    "JoinGame" = {
      name     = "${var.prefix}-JoinGame"
      filename = "handler"
      handler  = "handler.join_game"
      route    = "joinGame"
    },
    "NewRound" = {
      name     = "${var.prefix}-NewRound"
      filename = "handler"
      handler  = "handler.new_round"
      route    = "newRound"
    },
    "RollDice" = {
      name     = "${var.prefix}-RollDice"
      filename = "handler"
      handler  = "handler.roll_dice"
      route    = "rollDice"
    },
    "SetNickname" = {
      name     = "${var.prefix}-SetNickname"
      filename = "handler"
      handler  = "handler.set_nickname"
      route    = "setNickname"
    },
    "StartSpectating" = {
      name     = "${var.prefix}-StartSpectating"
      filename = "handler"
      handler  = "handler.start_spectating"
      route    = "startSpectating"
    },
    "StopSpectating" = {
      name     = "${var.prefix}-StopSpectating"
      filename = "handler"
      handler  = "handler.stop_spectating"
      route    = "stopSpectating"
    },
    "CheckSessionTimeout" = {
      name     = "${var.prefix}-CheckSessionTimeout"
      filename = "handler"
      handler  = "handler.check_session_timeout"
      route    = "checkSessionTimeout"
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

data "archive_file" "libs" {
  type        = "zip"
  source_dir  = "${var.lambda_folder}/libs"
  excludes    = ["__pycache__.py"]
  output_path = "${var.lambda_folder}/zip/libs.zip"
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${var.lambda_folder}/layer"
  excludes    = ["__pycache__.py"]
  output_path = "${var.lambda_folder}/zip/layer.zip"
}

data "archive_file" "all" {
  for_each    = local.lambdas
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/${each.value.filename}.py"
  output_path = "${var.lambda_folder}/zip/${each.value.filename}.zip"
}

resource "aws_lambda_layer_version" "libs" {
  filename            = data.archive_file.libs.output_path
  layer_name          = "${var.prefix}-Libs"
  compatible_runtimes = ["python3.12"]
  source_code_hash    = data.archive_file.libs.output_base64sha256
}

resource "aws_lambda_layer_version" "layer" {
  filename            = "${var.lambda_folder}/zip/layer.zip"
  layer_name          = "${var.prefix}-Logic"
  compatible_runtimes = ["python3.12"]
  source_code_hash    = data.archive_file.layer.output_base64sha256
}

resource "aws_lambda_function" "all" {
  for_each         = local.lambdas
  filename         = "${var.lambda_folder}/zip/${each.value.filename}.zip"
  function_name    = each.value.name
  handler          = each.value.handler
  layers           = [aws_lambda_layer_version.libs.arn, aws_lambda_layer_version.layer.arn]
  role             = aws_iam_role.role.arn
  runtime          = "python3.12"
  timeout          = 10
  source_code_hash = data.archive_file.all[each.key].output_base64sha256
  depends_on       = [aws_cloudwatch_log_group.all]
  environment {
    variables = {
      "PROJECT" : var.prefix,
      "GATEWAY_URL" : var.gateway_url,
      "WEBSOCKET_TABLE_NAME": var.websocket_table_name,
      "DISCONNECT_TIMEOUT": aws_sqs_queue.websocket_disconnected_queue.delay_seconds,
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
    resources = [var.table_arn, var.websocket_table_arn]
  }
}

data "aws_iam_policy_document" "api_connections" {
  # Allow Lambda to send messages to API gateway connections
  statement {
    actions = [
      "execute-api:ManageConnections",
    ]
    effect    = "Allow"
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "put_event" {
  statement {
    actions = [
      "events:PutEvents",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:events:ap-southeast-2:${var.aws_account_id}:event-bus/default",
    ]
  }
}

data "aws_iam_policy_document" "read_sqs" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    effect = "Allow"
    resources = [
      aws_sqs_queue.websocket_disconnected_queue.arn,
    ]
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
  inline_policy {
    name   = "PutEvent"
    policy = data.aws_iam_policy_document.put_event.json
  }
  inline_policy {
    name   = "ReadSqs"
    policy = data.aws_iam_policy_document.read_sqs.json
  }
}

# Events

resource "aws_cloudwatch_event_rule" "game_created" {
  name          = "${var.prefix}-GameCreated"
  description   = "A game has been created"
  event_pattern = <<-EOF
    {
      "source": ["${var.prefix}.GameCreated"],
      "detail-type": ["Game created"]
    }
  EOF
}

resource "aws_cloudwatch_event_target" "game_created" {
  rule      = aws_cloudwatch_event_rule.game_created.name
  target_id = "SendToCloudWatch"
  arn       = aws_cloudwatch_log_group.game_created.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_cloudwatch_log_group" "game_created" {
  name              = "/aws/events/${aws_cloudwatch_event_rule.game_created.name}"
  retention_in_days = 90
}

resource "aws_cloudwatch_event_rule" "websocket_disconnected" {
  name          = "${var.prefix}-WebsocketDisconnected"
  description   = "A player has disconnected from the websocket"
  event_pattern = <<-EOF
    {
      "source": ["${var.prefix}.Websocket"],
      "detail-type": ["Disconnected"]
    }
  EOF
}

resource "aws_cloudwatch_event_target" "websocket_disconnected" {
  rule      = aws_cloudwatch_event_rule.websocket_disconnected.name
  target_id = "SendToCloudWatch"
  arn       = aws_cloudwatch_log_group.websocket_disconnected.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_cloudwatch_log_group" "websocket_disconnected" {
  name              = "/aws/events/${aws_cloudwatch_event_rule.websocket_disconnected.name}"
  retention_in_days = 90
}

# SQS queue to delay event invocation

resource "aws_cloudwatch_event_target" "websocket_disconnected_queue" { 
  rule      = aws_cloudwatch_event_rule.websocket_disconnected.name
  target_id = "AddToSqs"
  arn       = aws_sqs_queue.websocket_disconnected_queue.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 60
  }
}

resource "aws_sqs_queue" "websocket_disconnected_queue" {
  name                      = "${var.prefix}-WebsocketDisconnection"
  delay_seconds = 60
  message_retention_seconds = 6 * 60 * 60
}

resource "aws_sqs_queue_policy" "websocket_disconnected_queue" {
  queue_url = aws_sqs_queue.websocket_disconnected_queue.id
  policy    = data.aws_iam_policy_document.websocket_disconnected_queue.json
}

data "aws_iam_policy_document" "websocket_disconnected_queue" {
  statement {
    actions = [
      "sqs:SendMessage",
    ]
    effect = "Allow"
    resources = [
      aws_sqs_queue.websocket_disconnected_queue.arn,
    ]
    principals {
      type = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    condition {
      test = "ArnEquals"
      variable = "aws:SourceArn"
      values = [aws_cloudwatch_event_rule.websocket_disconnected.arn]
    }
  }
}

resource "aws_lambda_event_source_mapping" "check_session_timeout" {
  event_source_arn = aws_sqs_queue.websocket_disconnected_queue.arn
  function_name    = local.lambdas["CheckSessionTimeout"]["name"]
  batch_size       = 1
}
