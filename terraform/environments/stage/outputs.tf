output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = module.game_api_gateway_shell.gateway_url
}

output "analytics_gateway_url" {
  description = "URL for invoking analytics API Gateway."
  value       = module.analytics_api_gateway.gateway_url
}

output "client_id" {
  description = "ID of the Cognito client"
  value       = module.cognito.client_id
}
