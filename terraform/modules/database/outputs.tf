output "table_arn" {
  description = "ARN tables"
  value       = aws_dynamodb_table.death_dice.arn
}
