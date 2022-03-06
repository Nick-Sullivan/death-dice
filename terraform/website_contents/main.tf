terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.70.0"
    }
  }
  backend "s3" {
    bucket = "nicks-terraform-states"
    key    = "uncomfortable_questions_website/website_contents/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

locals {
  url     = var.domain
  url_www = "www.${local.url}"
  tags = {
    Project = "Uncomfortable Questions"
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = local.tags
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "us-east-1"
  default_tags {
    tags = local.tags
  }
}

# Create a public S3 bucket to host the files.

module "s3_bucket" {
  source        = "./../modules/website_s3_bucket"
  name          = local.url
  source_folder = "${path.root}/../../src"
}

# Create the lambda that will interact with the database

module "website_lambda" {
  source = "./../modules/website_lambda"
  name = "UncomfortableQuestions"
  lambda_folder = "${path.root}/../../lambda"
}

# Create an API for the website to talk to, that will trigger the lambdas (version 2)

module "website_api_gateway" {
  source = "./../modules/website_api_gateway"
  name = "UncomfortableQuestions"
  integration_uri = module.website_lambda.uri
  lambda_function_name = module.website_lambda.function_name
}













# API gateway (v1)

# resource "aws_api_gateway_rest_api" "apiLambda" {
#   name        = "myAPI"
# }

# resource "aws_api_gateway_resource" "proxy" {
#    rest_api_id = aws_api_gateway_rest_api.apiLambda.id
#    parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
#    path_part   = "{proxy+}"
# }

# resource "aws_api_gateway_method" "proxyMethod" {
#    rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
#    resource_id   = aws_api_gateway_resource.proxy.id
#    http_method   = "ANY"
#    authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "lambda" {
#    rest_api_id = aws_api_gateway_rest_api.apiLambda.id
#    resource_id = aws_api_gateway_method.proxyMethod.resource_id
#    http_method = aws_api_gateway_method.proxyMethod.http_method

#    integration_http_method = "POST"
#    type                    = "AWS_PROXY"
#    uri                     = aws_lambda_function.lambda.invoke_arn
# }

# resource "aws_api_gateway_method" "proxy_root" {
#    rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
#    resource_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
#    http_method   = "ANY"
#    authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "lambda_root" {
#    rest_api_id = aws_api_gateway_rest_api.apiLambda.id
#    resource_id = aws_api_gateway_method.proxy_root.resource_id
#    http_method = aws_api_gateway_method.proxy_root.http_method

#    integration_http_method = "POST"
#    type                    = "AWS_PROXY"
#    uri                     = aws_lambda_function.lambda.invoke_arn
# }

# resource "aws_api_gateway_deployment" "apideploy" {
#    depends_on = [
#      aws_api_gateway_integration.lambda,
#      aws_api_gateway_integration.lambda_root,
#    ]

#    rest_api_id = aws_api_gateway_rest_api.apiLambda.id
#    stage_name  = "test"
# }

# resource "aws_lambda_permission" "apigw" {
#    statement_id  = "AllowAPIGatewayInvoke"
#    action        = "lambda:InvokeFunction"
#    function_name = aws_lambda_function.lambda.function_name
#    principal     = "apigateway.amazonaws.com"

#    # The "/*/*" portion grants access from any method on any resource
#    # within the API Gateway REST API.
#    source_arn = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"
# }

# module "cors" {
#   source  = "squidfunk/api-gateway-enable-cors/aws"
#   version = "0.3.3"

#   api_id            = aws_api_gateway_rest_api.apiLambda.id
#   api_resource_id   = aws_api_gateway_resource.proxy.id
#   allow_credentials = true
# }












##### SHIT FOR LATER #####


# Create a table to store lobbies

# resource "aws_dynamodb_table" "basic-dynamodb-table" {
#   # note - doesn't have autoscaling
#   name           = "UncomfortableQuestionsLobbies"
#   hash_key       = "LobbyId"
#   billing_mode   = "PROVISIONED"
#   read_capacity  = 5
#   write_capacity = 5

#   attribute {
#     name = "LobbyId"
#     type = "S"
#   }
# }


# data "aws_iam_policy_document" "inline_policy" {
#   statement {
#     actions   = ["dynamodb:PutItem"]
#     effect    = "Allow"
#     resources = [aws_dynamodb_table.basic-dynamodb-table.arn]
#   }
# }







# # Create an API for the website to talk to, that will trigger the lambdas

# resource "aws_api_gateway_rest_api" "uncomfortable_questions" {
#   name = "UncomfortableQuestions"

#   endpoint_configuration {
#     types = ["EDGE"]
#   }
# }

# resource "aws_api_gateway_deployment" "uncomfortable_questions" {
#   rest_api_id = aws_api_gateway_rest_api.uncomfortable_questions.id

#   depends_on = [
#     aws_api_gateway_method.one,
#     aws_api_gateway_method_response.one_response_200,
#     aws_api_gateway_integration.one,
#     aws_api_gateway_integration_response.one,
#   ]

#   triggers = {
#     redeployment = sha1(jsonencode(aws_api_gateway_rest_api.uncomfortable_questions.body))
#   }

#   lifecycle {
#     create_before_destroy = true
#   }

#   # We need this to redeploy when we update resources
#   # https://github.com/hashicorp/terraform/issues/6613#issuecomment-322264393
#   stage_description = md5(file("main.tf"))
# }

# resource "aws_api_gateway_stage" "example" {
#   deployment_id = aws_api_gateway_deployment.uncomfortable_questions.id
#   rest_api_id   = aws_api_gateway_rest_api.uncomfortable_questions.id
#   stage_name    = "prod"
# }

# resource "aws_api_gateway_resource" "one" {
#   rest_api_id = aws_api_gateway_rest_api.uncomfortable_questions.id
#   parent_id   = aws_api_gateway_rest_api.uncomfortable_questions.root_resource_id
#   path_part   = "one"
# }

# resource "aws_api_gateway_method" "one" {
#   rest_api_id   = aws_api_gateway_rest_api.uncomfortable_questions.id
#   resource_id   = aws_api_gateway_resource.one.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "one" {
#   rest_api_id             = aws_api_gateway_rest_api.uncomfortable_questions.id
#   resource_id             = aws_api_gateway_resource.one.id
#   http_method             = aws_api_gateway_method.one.http_method
#   integration_http_method = "GET"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.lambda.invoke_arn
# }

# resource "aws_api_gateway_method_response" "one_response_200" {
#   rest_api_id = aws_api_gateway_rest_api.uncomfortable_questions.id
#   resource_id = aws_api_gateway_resource.one.id
#   http_method = aws_api_gateway_method.one.http_method
#   status_code = "200"

#   response_models = {
#     "application/json" = "Empty"
#   }

#   response_parameters = {
#     "method.response.header.Access-Control-Allow-Headers"     = true,
#     "method.response.header.Access-Control-Allow-Methods"     = true,
#     "method.response.header.Access-Control-Allow-Origin"      = true,
#     "method.response.header.Access-Control-Allow-Credentials" = true
#   }
# }

# resource "aws_api_gateway_integration_response" "one" {
#   rest_api_id = aws_api_gateway_rest_api.uncomfortable_questions.id
#   resource_id = aws_api_gateway_resource.one.id
#   http_method = aws_api_gateway_method.one.http_method
#   status_code = aws_api_gateway_method_response.one_response_200.status_code

#   response_templates = {
#     "application/json" = ""
#   }

#   response_parameters = {
#     "method.response.header.Access-Control-Allow-Headers"     = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
#     "method.response.header.Access-Control-Allow-Methods"     = "'GET,OPTIONS,POST,PUT'",
#     "method.response.header.Access-Control-Allow-Origin"      = "'*'",
#     "method.response.header.Access-Control-Allow-Credentials" = "'true'"
#   }
# }

# module "cors" {
#   source  = "squidfunk/api-gateway-enable-cors/aws"
#   version = "0.3.3"

#   api_id            = aws_api_gateway_rest_api.uncomfortable_questions.id
#   api_resource_id   = aws_api_gateway_resource.one.id
#   allow_credentials = true
# }

# Create a hosted zone for our domain and point it to CloudFront

# resource "aws_route53_zone" "website" {
#   name              = local.url
#   delegation_set_id = var.delegation_set_id
# }

# module "alias" {
#   source        = "./../modules/website_alias"
#   name          = local.url
#   zone_id       = aws_route53_zone.website.zone_id
#   alias_name    = module.cloudfront.domain_name
#   alias_zone_id = module.cloudfront.hosted_zone_id
# }

# module "alias_www" {
#   source        = "./../modules/website_alias"
#   name          = local.url_www
#   zone_id       = aws_route53_zone.website.zone_id
#   alias_name    = module.cloudfront.domain_name
#   alias_zone_id = module.cloudfront.hosted_zone_id
# }

# # Create a CloudFront distribution that redirects to our S3 bucket, and allows SSL

# module "cloudfront" {
#   source            = "./../modules/website_cloudfront"
#   domain_name       = local.url
#   alternative_names = [local.url_www]
#   s3_url            = module.s3_bucket.public_url
#   zone_id           = aws_route53_zone.website.zone_id
#   providers = {
#     aws = aws.us-east-1
#   }
# }
