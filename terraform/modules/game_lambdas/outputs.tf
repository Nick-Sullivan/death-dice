output "lambdas" {
  description = "Map of lambda objects"
  value = {
    for k, v in local.lambdas : k => merge(v, { uri = aws_lambda_function.all[k].invoke_arn })
  }
}

output "game_created_rule_name" {
  description = "Name of the rule that fires when a game is created"
  value       = aws_cloudwatch_event_rule.game_created.name
}