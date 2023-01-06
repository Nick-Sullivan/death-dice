
output "workgroup_name" {
  description = "Name of the Athena processor"
  value       = aws_athena_workgroup.athena.name
}

output "athena_s3_output_arn" {
  description = "ARN of the s3 bucket that stores Athena results"
  value       = local.s3_output_arn
}

output "workgroup_arn" {
  description = "ARN of the Athena processor"
  value       = aws_athena_workgroup.athena.arn
}
