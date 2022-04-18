
variable "name" {
  description = "Name of the API gateway"
  type        = string
}

variable "lambdas" {
  description = "Lambda function name, gateway route, and invoke URI"
  type = map(object({
    name  = string
    route = string
    uri   = string
  }))
}
