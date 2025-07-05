
# Users interact with an API URL

module "game_api_gateway_shell" {
  source = "./../../modules/game_api_gateway_shell"
  name   = var.prefix
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
  source         = "./../../modules/game_lambdas"
  lambda_folder  = "${path.root}/../../../lambda/game"
  aws_account_id = var.aws_account_id
  prefix         = var.prefix
  gateway_url    = module.game_api_gateway_shell.gateway_url
  table_arn      = module.game_database.table_arn
  websocket_table_arn = module.game_database.websocket_table_arn
  websocket_table_name = module.game_database.websocket_table_name
}


# The database stores the game state

module "game_database" {
  source = "./../../modules/game_database"
  prefix = var.prefix
}


# Whenever the game state changes, we save it to S3

module "game_history" {
  source         = "./../../modules/game_history"
  lambda_folder  = "${path.root}/../../../lambda/history"
  aws_account_id = var.aws_account_id
  prefix         = var.prefix
  prefix_lower   = var.prefix_lower
  s3_name        = var.s3_database_history_name
  stream_arn     = module.game_database.stream_arn
}
