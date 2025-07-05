variable "prefix" {
  description = "Prefix of the components"
  type        = string
}

variable "admin_email" {
  description = "Email to send errors to"
  type        = string
}

variable "game_created_rule_name" {
  description = "Name of the GameCreated event rule"
  type        = string
}
