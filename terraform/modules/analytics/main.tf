
# When the game history is uploaded to S3, start SQL queries

module "analytics_process" {
  source                       = "./../../modules/analytics_process"
  lambda_folder                = "${path.root}/../../../lambda/analytics"
  aws_account_id               = var.aws_account_id
  prefix                       = var.prefix
  prefix_underscore            = var.prefix_underscore
  s3_arn                       = var.s3_database_history_arn
  s3_name                      = var.s3_database_history_name
  transform_finished_rule_arn  = var.transform_finished_rule_arn
  transform_finished_rule_name = var.transform_finished_rule_name
}


# When SQL queries are finished, save it to a cache

module "analytics_cache" {
  source                = "./../../modules/analytics_cache"
  lambda_folder         = "${path.root}/../../../lambda/analytics"
  prefix                = var.prefix
  athena_s3_output_arn  = module.analytics_process.athena_s3_output_arn
  athena_workgroup_arn  = module.analytics_process.workgroup_arn
  athena_workgroup_name = module.analytics_process.workgroup_name
}


# The cache is accessed by API

module "analytics_api" {
  source                = "./../../modules/analytics_api"
  lambda_folder         = "${path.root}/../../../lambda/analytics"
  aws_account_id        = var.aws_account_id
  prefix                = var.prefix
  cognito_user_pool_arn = var.cognito_user_pool_arn
  dynamodb_table_arn    = module.analytics_cache.dynamodb_table_arn
  dynamodb_table_name   = module.analytics_cache.dynamodb_table_name
  dynamodb_table_config_arn    = module.analytics_cache.dynamodb_table_config_arn
  dynamodb_table_config_name   = module.analytics_cache.dynamodb_table_config_name
}
