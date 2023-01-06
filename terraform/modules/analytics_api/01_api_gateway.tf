terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# When API requests come in, triggers the lambda to look up the cache

resource "aws_api_gateway_rest_api" "api" {
  name = var.prefix
}

resource "aws_api_gateway_authorizer" "api" {
  name        = "cognito"
  rest_api_id = aws_api_gateway_rest_api.api.id
  type        = "COGNITO_USER_POOLS"
  # authorizer_credentials = aws_iam_role.invocation_role.arn
  provider_arns = [var.cognito_user_pool_arn]
}


# /statistics

resource "aws_api_gateway_resource" "statistics" {
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "statistics"
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "statistics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.statistics.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "statistics_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.statistics.id
  http_method = aws_api_gateway_method.statistics.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Content-Type"   = true
    "method.response.header.Content-Length" = true
    "method.response.header.Timestamp"      = true
  }
}

resource "aws_api_gateway_integration" "statistics" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.statistics.id
  http_method             = aws_api_gateway_method.statistics.http_method
  content_handling        = "CONVERT_TO_TEXT"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.all["GetStatistics"].invoke_arn
}

resource "aws_lambda_permission" "statistics" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.all["GetStatistics"].function_name
  principal     = "apigateway.amazonaws.com"
  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:ap-southeast-2:314077822992:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.statistics.http_method}${aws_api_gateway_resource.statistics.path}"
}

# Deploy

resource "aws_api_gateway_deployment" "api" {
  depends_on = [
    aws_api_gateway_integration.statistics,
  ]
  rest_api_id = aws_api_gateway_rest_api.api.id
  description = "Terraform deployment"

  lifecycle {
    create_before_destroy = true
  }

  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.statistics.id,
      aws_api_gateway_method.statistics.id,
      aws_api_gateway_integration.statistics.id,
    ]))
  }
}

resource "aws_api_gateway_stage" "api" {
  deployment_id = aws_api_gateway_deployment.api.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "v1"
}
