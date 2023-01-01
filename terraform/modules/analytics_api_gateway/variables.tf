
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