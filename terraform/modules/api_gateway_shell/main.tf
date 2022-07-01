# Creates an empty API gateway shell, to generate a URL.

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

resource "aws_apigatewayv2_stage" "production" {
  api_id = aws_apigatewayv2_api.websocket.id
  name   = "production"
  default_route_settings {
    data_trace_enabled     = true
    logging_level          = "INFO"
    throttling_burst_limit = 5000
    throttling_rate_limit  = 10000
  }
}
