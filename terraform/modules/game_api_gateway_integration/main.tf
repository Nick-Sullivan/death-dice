# Edits an API gateway so API requests execute the appropriate lambda function

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# Routes are different entry points for the websocket

resource "aws_apigatewayv2_route" "all" {
  for_each  = var.lambdas
  api_id    = var.websocket_id
  route_key = each.value.route
  target    = "integrations/${aws_apigatewayv2_integration.all[each.key].id}"
}

# Integrations connect routes to our lambdas

resource "aws_apigatewayv2_integration" "all" {
  for_each                  = var.lambdas
  api_id                    = var.websocket_id
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
  source_arn    = "${var.websocket_arn}/*/${each.value.route}"
}

# Deploy the websocket so it is accessible

resource "aws_apigatewayv2_deployment" "websocket" {
  depends_on  = [aws_apigatewayv2_route.all, aws_apigatewayv2_integration.all]
  api_id      = var.websocket_id
  description = "Terraform deployment"

  lifecycle {
    create_before_destroy = true
  }
}
