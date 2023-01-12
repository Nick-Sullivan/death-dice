variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "prefix_lower" {
  description = "Prefix of the components, in lowercase"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "stream_arn" {
  description = "ARN of the DynamoDB stream"
  type        = string
}

variable "s3_name" {
  description = "Name of the S3 bucket to store database history"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}
