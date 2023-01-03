output "s3_name" {
  description = "Name of the S3 bucket holding database history"
  value       = aws_s3_bucket.history.bucket
}
