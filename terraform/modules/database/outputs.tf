output "stream_arn" {
  description = "ARN for the DynamoDB stream that records changes"
  value       = aws_dynamodb_table.death_dice.stream_arn
}

output "table_arn" {
  description = "ARN for the DynamoDB table"
  value       = aws_dynamodb_table.death_dice.arn
}

output "table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.death_dice.name
}
