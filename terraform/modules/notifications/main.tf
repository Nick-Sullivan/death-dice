

# Events that admin wants to be notified about

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

resource "aws_cloudwatch_event_target" "game_created" {
  rule      = var.game_created_rule_name
  target_id = "SendToAdmin"
  arn       = aws_sns_topic.admin_email.arn
  input_transformer {
    input_paths = {
      game_id = "$.detail.game_id"
    }
    input_template = "\"A new game was created: <game_id>\""
  }
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

# How to notify admin

resource "aws_sns_topic" "admin_email" {
  name = "${var.prefix}-NotifyAdmin"
}

resource "aws_sns_topic_policy" "admin_email" {
  arn    = aws_sns_topic.admin_email.arn
  policy = data.aws_iam_policy_document.admin_email.json
}

data "aws_iam_policy_document" "admin_email" {
  statement {
    effect = "Allow"
    actions = [
      "SNS:Publish",
    ]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    resources = [
      aws_sns_topic.admin_email.arn,
    ]
  }
}

resource "aws_sns_topic_subscription" "admin_email" {
  topic_arn = aws_sns_topic.admin_email.arn
  protocol  = "email"
  endpoint  = "nick.dave.sullivan@gmail.com"
}
