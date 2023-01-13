output "s3_name" {
  description = "Name of the S3 bucket holding database history"
  value       = aws_s3_bucket.history.bucket
}

output "client_id" {
  description = "ID of the Cognito client"
  value       = aws_cognito_user_pool_client.users.id
}

// Write out variables for use in other terraforms

resource "local_file" "terraform" {
  content  = <<-EOT
    {
      "s3_database_history_name": "${aws_s3_bucket.history.bucket}",
      "cognito_client_id": "${aws_cognito_user_pool_client.users.id}",
      "cognito_user_pool_id": "${aws_cognito_user_pool.users.id}",
      "cognito_user_pool_arn": "${aws_cognito_user_pool.users.arn}"
    }
  EOT
  filename = "../${local.terraform_output}/permanent_values.json"
}
