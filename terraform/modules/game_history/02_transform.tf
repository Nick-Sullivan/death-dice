
locals {
  s3_arn         = "arn:aws:s3:::${var.s3_name}"
  transform_name = "${var.prefix}-Transform"
  event_source = "${var.prefix}.Transform"
}


# A scheduled event starts a transformation lambda

resource "aws_cloudwatch_event_rule" "transform" {
  name                = local.transform_name
  description         = "Transform periodically"
  schedule_expression = "cron(30 0 * * ? *)" # 11:00am adelaide time, every day
  # schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "transform" { # comment to stop all transformations
  rule      = aws_cloudwatch_event_rule.transform.name
  target_id = "InvokeTransformLambda"
  arn       = aws_lambda_function.transform.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_lambda_permission" "transform" {
  statement_id  = "AllowExecutionFromEventBus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transform.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.transform.arn
}


# Transformation Lambda converts the extracted data and uploads to S3

data "archive_file" "transform" {
  type        = "zip"
  source_file = "${var.lambda_folder}/handler/transform.py"
  output_path = "${var.lambda_folder}/zip/transform.zip"
}

resource "aws_lambda_function" "transform" {
  filename                       = "${var.lambda_folder}/zip/transform.zip"
  function_name                  = local.transform_name
  handler                        = "transform.transform"
  role                           = aws_iam_role.transform.arn
  runtime                        = "python3.9"
  memory_size                    = 512 # MB
  timeout                        = 10
  reserved_concurrent_executions = 1
  source_code_hash               = data.archive_file.transform.output_base64sha256
  layers                         = ["arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python39:2"]
  depends_on                     = [aws_cloudwatch_log_group.transform]
  environment {
    variables = {
      "BUCKET_NAME" : var.s3_name,
      "QUEUE_URL" : aws_sqs_queue.extract.url,
      "EVENT_SOURCE" : local.event_source,
    }
  }
}


# Lambda permissions

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "read_sqs" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    effect = "Allow"
    resources = [
      aws_sqs_queue.extract.arn,
    ]
  }
}

data "aws_iam_policy_document" "upload_to_s3" {
  statement {
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject",
    ]
    effect = "Allow"
    resources = [
      local.s3_arn,
      "${local.s3_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "put_event" {
  statement {
    actions = [
      "events:PutEvents",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:events:ap-southeast-2:314077822992:event-bus/default",
    ]
  }
}

resource "aws_iam_role" "transform" {
  name                = "${var.prefix}-LamdbaTransformRole"
  description         = "Allows Lambda to read from SQS and upload to S3"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume_role.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policy {
    name   = "ReadSqs"
    policy = data.aws_iam_policy_document.read_sqs.json
  }
  inline_policy {
    name   = "S3Upload"
    policy = data.aws_iam_policy_document.upload_to_s3.json
  }
  inline_policy {
    name   = "PutEvent"
    policy = data.aws_iam_policy_document.put_event.json
  }
}


# Cloudwatch logs

resource "aws_cloudwatch_log_group" "transform" {
  name              = "/aws/lambda/${local.transform_name}"
  retention_in_days = 90
}


# When the game history has finished uploading to S3, fire a rule

resource "aws_cloudwatch_event_rule" "transform_finished" {
  name        = "${var.prefix}-TransformComplete"
  description = "Game history data has been transformed"
  event_pattern = <<-EOF
    {
      "source": ["${local.event_source}"],
      "detail-type": ["Transformation complete"]
    }
  EOF
}

resource "aws_cloudwatch_event_target" "transform_finished" {
  rule      = aws_cloudwatch_event_rule.transform_finished.name
  target_id = "SendToCloudWatch"
  arn       = aws_cloudwatch_log_group.transform_finished.arn
  retry_policy {
    maximum_retry_attempts       = 0
    maximum_event_age_in_seconds = 24 * 60 * 60
  }
}

resource "aws_cloudwatch_log_group" "transform_finished" {
  name              = "/aws/events/${aws_cloudwatch_event_rule.transform_finished.name}"
  retention_in_days = 90
}
