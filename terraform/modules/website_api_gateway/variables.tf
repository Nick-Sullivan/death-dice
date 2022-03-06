
variable "name" {
  description = "Name of the API gateway"
  type        = string
}

variable "integration_uri" {
  description = "URI to call from this gateway"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the lambda function we will be using"
  type        = string
}
