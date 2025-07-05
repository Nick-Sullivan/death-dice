
output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = aws_api_gateway_stage.api.invoke_url
}
