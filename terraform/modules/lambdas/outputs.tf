# output "connect_uri" {
#   description = "ARN to invoke the connecting lambda function"
#   value       = aws_lambda_function.connect.invoke_arn
# }

output "lambdas" {
  description = "Map of lambda objects"
  value = {
    for k, v in local.lambdas : k => merge(v, { uri = aws_lambda_function.all[k].invoke_arn })
  }
}