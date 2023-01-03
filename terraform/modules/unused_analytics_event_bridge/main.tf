
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_cloudwatch_event_bus" "project_bus" {
  name = var.prefix
}

resource "aws_cloudwatch_event_rule" "to_custom_bus" {
  name        = "${var.prefix}Analytics-ToCustomBus"
  description = "Send events to the project bus"
  event_pattern = <<-EOF
    {
      "source": ["aws.athena"],
      "detail-type": ["Athena Query State Change"],
      "detail": {
        "workgroupName": ["${var.prefix}"]
      }
    }
  EOF
}

resource "aws_cloudwatch_event_target" "to_custom_bus" {
  target_id = "SendToCustomBus"
  rule      = aws_cloudwatch_event_rule.to_custom_bus.name
  arn       = aws_cloudwatch_event_bus.project_bus.arn
  role_arn  = aws_iam_role.to_custom_bus.arn
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "to_custom_bus" {
  statement {
    actions = [
      "events:PutEvents",
    ]
    effect    = "Allow"
    resources = [aws_cloudwatch_event_bus.project_bus.arn]
  }
}

resource "aws_iam_role" "to_custom_bus" {
  name               = "${var.prefix}AnalyticsSendEvents"
  description        = "Allows the event bus to send messages to the custom event bus"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  inline_policy {
    name   = "SendToCustomBus"
    policy = data.aws_iam_policy_document.to_custom_bus.json
  }
}
