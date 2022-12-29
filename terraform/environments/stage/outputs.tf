output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = module.api_gateway_shell.gateway_url
}

output "client_id" {
  description = "ID of the Cognito client"
  value       = module.cognito.client_id
}
