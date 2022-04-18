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

resource "aws_apigatewayv2_route" "all" {
  for_each  = var.lambdas
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = each.value.route
  target    = "integrations/${aws_apigatewayv2_integration.all[each.key].id}"
}

# Integrations connect routes to our lambdas

resource "aws_apigatewayv2_integration" "all" {
  for_each                  = var.lambdas
  api_id                    = aws_apigatewayv2_api.websocket.id
  integration_type          = "AWS_PROXY"
  content_handling_strategy = "CONVERT_TO_TEXT"
  description               = "Lambda connection"
  integration_method        = "POST"
  integration_uri           = each.value.uri
}

# Permissions to invoke lambdas

resource "aws_lambda_permission" "all" {
  for_each      = var.lambdas
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = each.value.name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/${each.value.route}"
}

# Websocket versions are part of a stage, which must be deployed for it to be used

resource "aws_apigatewayv2_stage" "production" {
  api_id        = aws_apigatewayv2_api.websocket.id
  deployment_id = aws_apigatewayv2_deployment.websocket.id
  name          = "production"
}

resource "aws_apigatewayv2_deployment" "websocket" {
  depends_on  = [aws_apigatewayv2_route.all]
  api_id      = aws_apigatewayv2_api.websocket.id
  description = "Terraform deployment"
  lifecycle {
    create_before_destroy = true
  }
}
