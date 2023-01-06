output "dynamodb_table_arn" {
  description = "ARN of the dynamoDB table storing analytics results"
  value       = aws_dynamodb_table.cache.arn
}

output "dynamodb_table_name" {
  description = "Name of the dynamoDB table storing analytics results"
  value       = aws_dynamodb_table.cache.name
}

