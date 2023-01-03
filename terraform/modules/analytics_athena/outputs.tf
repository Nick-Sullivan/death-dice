output "workgroup_arn" {
  description = "ARN of the Athena processor"
  value       = aws_athena_workgroup.athena.arn
}

output "workgroup_name" {
  description = "Name of the Athena processor"
  value       = aws_athena_workgroup.athena.name
}

output "query_id" {
  description = "ID of the athena named query"
  value       = aws_athena_named_query.all_stats_per_account.id
}

output "glue_database_id" {
  description = "ID of the glue database"
  value       = aws_athena_database.athena.id
}

output "glue_connection_table_arn" {
  description = "ARN of the glue connection table"
  value       = aws_glue_catalog_table.connection.arn
}

output "glue_game_table_arn" {
  description = "ARN of the glue game table"
  value       = aws_glue_catalog_table.game.arn
}
