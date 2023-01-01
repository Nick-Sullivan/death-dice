variable "prefix" {
  description = "Prefix of the Lambdas"
  type        = string
}

variable "lambda_folder" {
  description = "Location of the folder with lambda source code, expected to have a 'src' folder inside it"
  type        = string
}

variable "athena_s3_output_arn" {
  description = "ARN of the s3 bucket that stores Athena results"
  type        = string
}

variable "athena_workgroup_arn" {
  description = "ARN of the Athena workgroup that processes queries"
  type        = string
}

variable "athena_workgroup_name" {
  description = "Name of the Athena workgroup that processes queries"
  type        = string
}

variable "athena_query_game_count_id" {
  description = "ID of the Athena query that counts the number of games"
  type        = string
}

variable "glue_database_id" {
  description = "ID of the glue database to be used in the query"
  type        = string
}

variable "glue_table_arn" {
  description = "ARN of the glue table to be used in the query"
  type        = string
}


