variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "prefix_underscore" {
  description = "Prefix of the components, in lowercase and with underscores"
  type        = string
}

variable "s3_name" {
  description = "Name of the s3 bucket to ingest and store results"
  type        = string
}
