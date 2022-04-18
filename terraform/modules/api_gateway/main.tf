# Creates an API gateway that takes Websocket requests, and executes the appropriate lambda function

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_apigatewayv2_api" "websocket" {
  name                       = var.name
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}

# Routes are different entry points for the websocket

resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect.id}"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect.id}"
}

resource "aws_apigatewayv2_route" "join_lobby" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "joinLobby"
  target    = "integrations/${aws_apigatewayv2_integration.join_lobby.id}"
}

resource "aws_apigatewayv2_route" "send_message" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "sendMessage"
  target    = "integrations/${aws_apigatewayv2_integration.send_message.id}"
}

# Integrations connect routes to our lambdas

resource "aws_apigatewayv2_integration" "connect" {
  api_id                    = aws_apigatewayv2_api.websocket.id
  integration_type          = "AWS_PROXY"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Lambda connection"
  integration_method        = "POST"
  integration_uri           = var.connect_uri
}

resource "aws_apigatewayv2_integration" "disconnect" {
  api_id                    = aws_apigatewayv2_api.websocket.id
  integration_type          = "AWS_PROXY"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Lambda disconnection"
  integration_method        = "POST"
  integration_uri           = var.disconnect_uri
}

resource "aws_apigatewayv2_integration" "join_lobby" {
  api_id                    = aws_apigatewayv2_api.websocket.id
  integration_type          = "AWS_PROXY"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Lambda message"
  integration_method        = "POST"
  integration_uri           = var.join_lobby_uri
}

resource "aws_apigatewayv2_integration" "send_message" {
  api_id                    = aws_apigatewayv2_api.websocket.id
  integration_type          = "AWS_PROXY"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Lambda message"
  integration_method        = "POST"
  integration_uri           = var.send_message_uri
}

# Permissions to invoke lambdas

resource "aws_lambda_permission" "connect" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.connect_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/${aws_apigatewayv2_route.connect.route_key}"
}

resource "aws_lambda_permission" "disconnect" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.disconnect_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/${aws_apigatewayv2_route.disconnect.route_key}"
}

resource "aws_lambda_permission" "join_lobby" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.join_lobby_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/${aws_apigatewayv2_route.join_lobby.route_key}"
}

resource "aws_lambda_permission" "send_message" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.send_message_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/${aws_apigatewayv2_route.send_message.route_key}"
}

# Websocket versions are part of a stage, which must be deployed for it to be used

resource "aws_apigatewayv2_stage" "production" {
  api_id        = aws_apigatewayv2_api.websocket.id
  deployment_id = aws_apigatewayv2_deployment.websocket.id
  name          = "production"
}

resource "aws_apigatewayv2_deployment" "websocket" {
  depends_on  = [aws_apigatewayv2_route.connect, aws_apigatewayv2_route.disconnect, aws_apigatewayv2_route.send_message]
  api_id      = aws_apigatewayv2_api.websocket.id
  description = "Terraform deployment"
  lifecycle {
    create_before_destroy = true
  }
}
