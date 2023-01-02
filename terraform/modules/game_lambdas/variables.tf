variable "prefix" {
  description = "Prefix of the Lambdas"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "table_arn" {
  description = "ARN of the database this lambda will be interacting with"
  type        = string
}

variable "gateway_url" {
  description = "URL for invoking API Gateway."
  type        = string
}