

variable "websocket_id" {
  description = "ID of the API Gateway created from the shell"
  type        = string
}

variable "websocket_arn" {
  description = "ARN of the API Gateway created from the shell"
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
