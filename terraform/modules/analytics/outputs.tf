
output "gateway_url" {
  description = "URL for invoking analytics API Gateway."
  value       = module.analytics_api.gateway_url
}
