output "gateway_url" {
  description = "URL for invoking API Gateway."
  value       = aws_apigatewayv2_stage.production.invoke_url
}

output "websocket_id" {
  value = aws_apigatewayv2_api.websocket.id
}

output "websocket_arn" {
  value = aws_apigatewayv2_api.websocket.execution_arn
}
