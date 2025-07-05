variable "prefix" {
  description = "Prefix of the Lambdas"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'handler' folder inside it"
  type        = string
}

variable "athena_workgroup_name" {
  description = "Name of the Athena workgroup that processes queries"
  type        = string
}

variable "athena_s3_output_arn" {
  description = "ARN of the s3 bucket that stores Athena results"
  type        = string
}

variable "athena_workgroup_arn" {
  description = "ARN of the Athena workgroup that processes queries"
  type        = string
}
