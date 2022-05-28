output "table_arns" {
  description = "ARN tables"
  value = [
    aws_dynamodb_table.death_dice.arn,
    aws_dynamodb_table.connections.arn,
  ]
}
