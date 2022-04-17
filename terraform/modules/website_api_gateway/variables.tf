
variable "name" {
  description = "Name of the API gateway"
  type        = string
}

variable "connect_function_name" {
  description = "Name of the lambda function upon connections"
  type        = string
}

variable "connect_uri" {
  description = "URI to call from this gateway upon connections"
  type        = string
}

variable "disconnect_function_name" {
  description = "Name of the lambda function upon disconnections"
  type        = string
}

variable "disconnect_uri" {
  description = "URI to call from this gateway upon disconnections"
  type        = string
}

variable "send_message_function_name" {
  description = "Name of the lambda function to send messages"
  type        = string
}

variable "send_message_uri" {
  description = "URI to call from this gateway to send messages"
  type        = string
}
