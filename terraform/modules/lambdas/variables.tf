variable "prefix" {
  description = "Prefix of the Lambdas"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "table_arns" {
  description = "ARNs of the database this lambda will be interacting with"
  type        = list(string)
}
