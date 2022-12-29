output "client_id" {
  description = "ID of the Cognito client"
  value       = aws_cognito_user_pool_client.client.id
}

output "user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = aws_cognito_user_pool.authentication.id
}

