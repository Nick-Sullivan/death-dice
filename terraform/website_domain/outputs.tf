output "delegation_set_id" {
  description = "Use this ID in the website_contents terraform"
  value       = aws_route53_delegation_set.name_servers.id
}

output "delegation_set_name_servers" {
  description = "Set these servers for the registered domain"
  value       = aws_route53_delegation_set.name_servers.name_servers
}

