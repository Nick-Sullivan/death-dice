

resource "aws_cloudwatch_dashboard" "dashboard" {
  dashboard_name = var.name
  dashboard_body = file("${path.module}/cloudwatch_dashboard.json")
}

