output "s3_arn" {
  description = "ARN of the s3 bucket saving history"
  value       = local.s3_arn
}

output "s3_name" {
  description = "Name of the s3 bucket saving history"
  value       = var.s3_name
}

output "transform_finished_rule_arn" {
  description = "ARN of the rule that fires when transformation has finished"
  value       = aws_cloudwatch_event_rule.transform_finished.arn
}

output "transform_finished_rule_name" {
  description = "Name of the rule that fires when transformation has finished"
  value       = aws_cloudwatch_event_rule.transform_finished.name
}