
# Create an API with a URL, to be populated later

module "game_api_gateway_shell" {
  source = "./../../modules/game_api_gateway_shell"
  name   = local.prefix
}

# Create a database to store game state

module "game_database" {
  source = "./../../modules/game_database"
  prefix = local.prefix
}

# Create the lambdas that will interact with the database

module "game_lambdas" {
  source        = "./../../modules/game_lambdas"
  prefix        = local.prefix
  lambda_folder = "${path.root}/../../../lambda/game"
  gateway_url   = module.game_api_gateway_shell.gateway_url
  table_arn     = module.game_database.table_arn
}

# Populate the API so it will trigger the lambdas

module "game_api_gateway_integration" {
  source        = "./../../modules/game_api_gateway_integration"
  lambdas       = module.game_lambdas.lambdas
  websocket_id  = module.game_api_gateway_shell.websocket_id
  websocket_arn = module.game_api_gateway_shell.websocket_arn
}

# Extract the game history into s3 
# TODO- failures

module "game_history" {
  source        = "./../../modules/game_history"
  prefix        = local.prefix
  prefix_lower  = local.prefix_lower
  lambda_folder = "${path.root}/../../../lambda/history"
  s3_name       = local.permanent_output.s3_database_history_name
  stream_arn    = module.game_database.stream_arn
}

# Create a dashboard for observing correct behaviour

module "game_monitoring" {
  source  = "./../../modules/game_monitoring"
  name    = local.prefix
  name_analytics = local.prefix_analytics
  project = local.tags.Project
}
