output "s3_database_history_arn" {
  description = "ARN of the s3 bucket saving history"
  value       = module.game_history.s3_arn
}

output "transform_finished_rule_arn" {
  description = "ARN of the rule that fires when transformation has finished"
  value       = module.game_history.transform_finished_rule_arn
}

output "transform_finished_rule_name" {
  description = "Name of the rule that fires when transformation has finished"
  value       = module.game_history.transform_finished_rule_name
}

output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = module.game_api_gateway_shell.gateway_url
}
