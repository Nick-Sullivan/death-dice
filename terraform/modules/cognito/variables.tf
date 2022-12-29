variable "name" {
  description = "Name of the cognito infrastructure"
  type        = string
}

variable "callback_url" {
  description = "URL to go to after authentication"
  type        = string
}

variable "domain" {
  description = "Name of the authentication domain"
  type        = string
}
