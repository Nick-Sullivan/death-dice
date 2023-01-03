variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "prefix_lower" {
  description = "Prefix of the components, in lowercase"
  type        = string
}

variable "table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}