
# Athena for running SQL

module "analytics_athena" {
  source            = "./../../modules/analytics_athena"
  prefix            = local.prefix_analytics
  prefix_underscore = local.prefix_analytics_underscore
  s3_name           = module.game_history.s3_name
}

# Lambda for orchestrating analytics

module "analytics_lambdas" {
  source                    = "./../../modules/analytics_lambdas"
  prefix                    = local.prefix_analytics
  lambda_folder             = "${path.root}/../../../lambda/analytics"
  athena_s3_output_arn      = module.game_history.s3_arn
  athena_workgroup_arn      = module.analytics_athena.workgroup_arn
  athena_workgroup_name     = module.analytics_athena.workgroup_name
  athena_query_id           = module.analytics_athena.query_id
  glue_database_id          = module.analytics_athena.glue_database_id
  glue_connection_table_arn = module.analytics_athena.glue_connection_table_arn
  glue_game_table_arn       = module.analytics_athena.glue_game_table_arn
  dynamodb_table_arn        = aws_dynamodb_table.analytics_cache.arn
  dynamodb_table_name       = aws_dynamodb_table.analytics_cache.name
}

# API for accessing analytics results

module "analytics_api_gateway" {
  source                = "./../../modules/analytics_api_gateway"
  name                  = local.prefix_analytics
  cognito_user_pool_arn = local.permanent_output.cognito_user_pool_arn
  lambda_name           = module.analytics_lambdas.lambdas["GetStatistics"].name
  lambda_uri            = module.analytics_lambdas.lambdas["GetStatistics"].uri
}

# Trigger a rule when Athena queries succeed

resource "aws_cloudwatch_event_rule" "events" {
  name        = "${local.prefix}-AthenaQuerySucceeded"
  description = ""

  event_pattern = <<-EOF
    {
      "source": ["aws.athena"],
      "detail-type": ["Athena Query State Change"],
      "detail": {
        "workgroupName": ["${module.analytics_athena.workgroup_name}"],
        "currentState": ["SUCCEEDED"]
      }
    }
  EOF
}

# Log when rule fires

resource "aws_cloudwatch_event_target" "events" {
  rule      = aws_cloudwatch_event_rule.events.name
  target_id = "SendToCloudWatch"
  arn       = aws_cloudwatch_log_group.events.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
  # dead_letter_config {
  # arn = 
  # }
}

resource "aws_cloudwatch_log_group" "events" {
  name              = "/aws/events/${aws_cloudwatch_event_rule.events.name}"
  retention_in_days = 90
}

# Invoke lambda when rule fires

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.events.name
  target_id = "InvokeCacheLambda"
  arn       = module.analytics_lambdas.lambdas["CacheResult"].arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
  # dead_letter_config {
  # arn = 
  # }
}

resource "aws_lambda_permission" "all" {
  statement_id  = "AllowExecutionFromEventBus"
  action        = "lambda:InvokeFunction"
  function_name = module.analytics_lambdas.lambdas["CacheResult"].name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.events.arn
}

# Table for caching queries

resource "aws_dynamodb_table" "analytics_cache" {
  name         = local.prefix_analytics
  hash_key     = "id"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "id"
    type = "S"
  }
}

