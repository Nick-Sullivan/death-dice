

resource "aws_cloudwatch_metric_alarm" "transform" {
  alarm_name          = var.prefix
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  period              = "120"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Monitors lambda failures"
  namespace           = "AWS/Lambda"
  alarm_actions       = [aws_sns_topic.admin_email.arn]
}

resource "aws_sns_topic" "admin_email" {
  name = "${var.prefix}-NotifyAdmin"
}

resource "aws_sns_topic_subscription" "admin_email" {
  topic_arn = aws_sns_topic.admin_email.arn
  protocol  = "email"
  endpoint  = "nick.dave.sullivan@gmail.com"
}
