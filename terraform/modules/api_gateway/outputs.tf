output "production_url" {
  description = "Production URL for API Gateway."
  value       = aws_apigatewayv2_stage.production.invoke_url
}
