
variable "name" {
  description = "The URL to be redirected"
  type        = string
}

variable "zone_id" {
  description = "The Route53 zone ID of the domain being redirected"
  type        = string
}

variable "alias_name" {
  description = "The URL to redirect to"
  type        = string
}

variable "alias_zone_id" {
  description = "The Route53 zone ID to redirect to"
  type        = string
}
