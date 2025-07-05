output "event_bus_arn" {
  description = "ARN of the new event bus"
  value       = aws_cloudwatch_event_bus.project_bus.arn
}

output "event_bus_name" {
  description = "Name of the new event bus"
  value       = aws_cloudwatch_event_bus.project_bus.name
}

