output "lambdas" {
  description = "Map of lambda objects"
  value = {
    for k, v in local.lambdas : k => merge(v, { uri = aws_lambda_function.all[k].invoke_arn })
  }
}
