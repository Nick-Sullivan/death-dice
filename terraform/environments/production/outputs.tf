output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = module.api_gateway_shell.gateway_url
}