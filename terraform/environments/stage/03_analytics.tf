
# When the game history is uploaded to S3, start SQL queries

module "analytics_process" {
  source                       = "./../../modules/analytics_process"
  lambda_folder                = "${path.root}/../../../lambda/analytics"
  aws_account_id               = local.aws_account_id
  prefix                       = local.prefix_analytics
  prefix_underscore            = local.prefix_analytics_underscore
  s3_arn                       = module.game_history.s3_arn
  s3_name                      = module.game_history.s3_name
  transform_finished_rule_arn  = module.game_history.transform_finished_rule_arn
  transform_finished_rule_name = module.game_history.transform_finished_rule_name
}


# When SQL queries are finished, save it to a cache

module "analytics_cache" {
  source                = "./../../modules/analytics_cache"
  lambda_folder         = "${path.root}/../../../lambda/analytics"
  prefix                = local.prefix_analytics
  athena_s3_output_arn  = module.analytics_process.athena_s3_output_arn
  athena_workgroup_arn  = module.analytics_process.workgroup_arn
  athena_workgroup_name = module.analytics_process.workgroup_name
}


# The cache is accessed by API

module "analytics_api" {
  source                = "./../../modules/analytics_api"
  lambda_folder         = "${path.root}/../../../lambda/analytics"
  aws_account_id        = local.aws_account_id
  prefix                = local.prefix_analytics
  cognito_user_pool_arn = local.permanent_output.cognito_user_pool_arn
  dynamodb_table_arn    = module.analytics_cache.dynamodb_table_arn
  dynamodb_table_name   = module.analytics_cache.dynamodb_table_name
}
