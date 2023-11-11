
variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "The ARN of the Cognito user pool performing authorising"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the dynamoDB table storing analytics results"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the dynamoDB table storing analytics results"
  type        = string
}

variable "dynamodb_table_config_arn" {
  description = "ARN of the dynamoDB table storing analytics config"
  type        = string
}

variable "dynamodb_table_config_name" {
  description = "Name of the dynamoDB table storing analytics config"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}
