output "connect_uri" {
  description = "ARN to invoke the connecting lambda function"
  value       = aws_lambda_function.connect.invoke_arn
}

output "connect_function_name" {
  description = "Name of the connecting lambda function"
  value       = aws_lambda_function.connect.function_name
}

output "disconnect_uri" {
  description = "ARN to invoke the disconnecting lambda function"
  value       = aws_lambda_function.disconnect.invoke_arn
}

output "disconnect_function_name" {
  description = "Name of the disconnecting lambda function"
  value       = aws_lambda_function.disconnect.function_name
}

output "send_message_uri" {
  description = "ARN to invoke the messaging lambda function"
  value       = aws_lambda_function.send_message.invoke_arn
}

output "send_message_function_name" {
  description = "Name of the message lambda function"
  value       = aws_lambda_function.send_message.function_name
}
