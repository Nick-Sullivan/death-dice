variable "prefix" {
  description = "Prefix of the component names"
  type        = string
}

variable "prefix_underscore" {
  description = "Prefix of the components, in lowercase and with underscores"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'handler' folder inside it"
  type        = string
}

variable "s3_name" {
  description = "Name of the s3 bucket to ingest and store results"
  type        = string
}

variable "s3_arn" {
  description = "ARN of the s3 bucket to ingest and store results"
  type        = string
}
