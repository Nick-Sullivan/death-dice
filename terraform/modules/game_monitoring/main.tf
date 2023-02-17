
# To update this
# - fiddle with the dashboard in the AWS console
# - Actions -> View/Edit Source
# - replace the prefix (DeathDiceAnalytics) with ${name_analytics}
# - replace the prefix (DeathDice) with ${name}
# - replace the project name (Death Dice) with ${project}
# - replace the project name (death-dice) with ${name_lower}
data "template_file" "dashboard" {
  template = file("${path.module}/dashboard.json")
  vars = {
    name_analytics = var.name_analytics
    name           = var.name
    project        = var.project
    name_lower     = var.name_lower
  }
}

resource "aws_cloudwatch_dashboard" "dashboard" {
  dashboard_name = var.name
  dashboard_body = data.template_file.dashboard.rendered
}
