output "uri" {
  description = "ARN to invoke the lambda function"
  value       = aws_lambda_function.function.invoke_arn
}

output "function_name" {
  description = "Name of the lambda function"
  value       = aws_lambda_function.function.function_name
}

