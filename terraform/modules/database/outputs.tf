output "database_arn" {
  description = "ARN to of the database"
  value       = aws_dynamodb_table.lobbies.arn
}
