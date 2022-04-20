output "table_arns" {
  description = "ARN tables"
  value = [
    aws_dynamodb_table.players.arn,
    aws_dynamodb_table.games.arn,
    aws_dynamodb_table.rolls.arn,
    "${aws_dynamodb_table.players.arn}/index/*",
    "${aws_dynamodb_table.games.arn}/index/*",
    "${aws_dynamodb_table.rolls.arn}/index/*",
  ]
}
