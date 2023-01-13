
# Users interact with an API URL

module "game_api_gateway_shell" {
  source = "./../../modules/game_api_gateway_shell"
  name   = local.prefix
}


# The API triggers a lambda

module "game_api_gateway_integration" {
  source        = "./../../modules/game_api_gateway_integration"
  lambdas       = module.game_lambdas.lambdas
  websocket_id  = module.game_api_gateway_shell.websocket_id
  websocket_arn = module.game_api_gateway_shell.websocket_arn
}


# The lambda's update game state

module "game_lambdas" {
  source        = "./../../modules/game_lambdas"
  lambda_folder = "${path.root}/../../../lambda/game"
  prefix        = local.prefix
  gateway_url   = module.game_api_gateway_shell.gateway_url
  table_arn     = module.game_database.table_arn
}


# The database stores the game state

module "game_database" {
  source = "./../../modules/game_database"
  prefix = local.prefix
}


# Whenever the game state changes, we save it to S3
# TODO- failures

module "game_history" {
  source         = "./../../modules/game_history"
  lambda_folder  = "${path.root}/../../../lambda/history"
  aws_account_id = local.aws_account_id
  prefix         = local.prefix
  prefix_lower   = local.prefix_lower
  s3_name        = local.permanent_output.s3_database_history_name
  stream_arn     = module.game_database.stream_arn
}


# Monitor using a cloudwatch dashboard 
module "game_monitoring" {
  source         = "./../../modules/game_monitoring"
  name           = local.prefix
  name_analytics = local.prefix_analytics
  project        = local.tags.Project
}

module "notifications" {
  source      = "./../../modules/notifications"
  prefix      = local.prefix
  admin_email = local.admin_email
}
