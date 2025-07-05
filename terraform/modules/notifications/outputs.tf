output "topic_arn" {
  description = "ARN of the SNS topic that notifies the administrator"
  value       = aws_sns_topic.admin_email.arn
}
