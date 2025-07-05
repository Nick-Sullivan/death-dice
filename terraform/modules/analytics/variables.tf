variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "prefix_underscore" {
  description = "Prefix of the components, in underscore"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "s3_database_history_arn" {
  description = "ARN of the S3 bucket to store database history"
  type        = string
}

variable "s3_database_history_name" {
  description = "Name of the S3 bucket to store database history"
  type        = string
}

variable "transform_finished_rule_arn" {
  description = "ARN of the rule that fires when transformation finishes"
  type        = string
}

variable "transform_finished_rule_name" {
  description = "ARN of the rule that fires when transformation finishes"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "ARN of the cognito user pool for authentication"
  type        = string
}
