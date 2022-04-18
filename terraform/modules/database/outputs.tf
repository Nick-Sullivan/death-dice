output "table_arns" {
  description = "ARN tables"
  value = [
    aws_dynamodb_table.connections.arn,
    aws_dynamodb_table.games.arn,
    "${aws_dynamodb_table.connections.arn}/index/*",
    "${aws_dynamodb_table.games.arn}/index/*",
  ]
}
