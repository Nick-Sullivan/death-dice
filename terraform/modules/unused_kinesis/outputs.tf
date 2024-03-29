output "s3_arn" {
  description = "ARN of the s3 bucket saving history"
  value       = aws_s3_bucket.kinesis.arn
}

output "s3_name" {
  description = "Name of the s3 bucket saving history"
  value       = aws_s3_bucket.kinesis.bucket
}