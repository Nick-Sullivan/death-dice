
variable "name" {
  description = "Name of the bucket, normal to use the domain name"
  type        = string
}

variable "source_folder" {
  description = "Location of the source folder, contents will be uploaded to S3"
  type        = string
}
