
variable "name" {
  description = "Name of the API gateway"
  type        = string
}

variable "lambda_name" {
  description = "The name of the Lambda to be invoked"
  type        = string
}

variable "lambda_uri" {
  description = "The URI of the Lambda to be invoked"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "The ARN of the Cognito user pool performing authorising"
  type        = string
}
