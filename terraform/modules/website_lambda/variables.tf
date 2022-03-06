
variable "name" {
  description = "Name of the Lambda"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "dynamo_db_arn" {
  description = "ARN of the database this lambda will be interacting with"
  type        = string
}
