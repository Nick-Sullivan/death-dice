variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "prefix_lower" {
  description = "Prefix of the components, in lowercase"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "s3_database_history_name" {
  description = "Name of the S3 bucket to store database history"
  type        = string
}
