output "s3_arn" {
  description = "ARN of the s3 bucket saving history"
  value       = local.s3_arn
}

output "s3_name" {
  description = "Name of the s3 bucket saving history"
  value       = var.s3_name
}