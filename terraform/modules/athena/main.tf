# Extracts data from DynamoDB to S3
# Note - saving this as parquet reduces the amount of data scanned by 10 to 30x

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_athena_database" "athena" {
  name   = var.prefix_underscore
  bucket = var.s3_name
}

resource "aws_athena_workgroup" "athena" {
  # Processor settings
  name          = var.prefix
  force_destroy = true
  configuration {
    bytes_scanned_cutoff_per_query     = 10 * 1024 * 1024 // bytes, minimum 10 MB
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.s3_name}/athena"
    }
  }
}

resource "aws_glue_catalog_table" "connection" {
  name          = "connection"
  database_name = aws_athena_database.athena.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    EXTERNAL       = "TRUE"
    classification = "parquet"
  }

  storage_descriptor {
    location = "s3://${var.s3_name}/data/table=Connection/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
      
      parameters = {
        "serialization.format"  = 1
        "ignore.malformed.json" = false
        "dots.in.keys"          = false
        "case.insensitive"      = true
        "mapping"               = true
      }
    }

    columns {
      name = "meta_event_type"
      type = "string"
    }
    columns {
      name = "modified_action"
      type = "string"
    }
    columns {
      name = "modified_at"
      type = "string"
    }
    columns {
      name = "id"
      type = "string"
    }
    columns {
      name = "account_id"
      type = "string"
    }
    columns {
      name = "game_id"
      type = "string"
    }
    columns {
      name = "version"
      type = "int"
    }
    columns {
      name = "nickname"
      type = "string"
    }

  }
}

# resource "aws_glue_catalog_table" "connection_json" {
#   name          = "connection_json"
#   database_name = aws_athena_database.athena.name
#   table_type    = "EXTERNAL_TABLE"
#   parameters = {
#     EXTERNAL       = "TRUE"
#     classification = "json"
#   }

#   storage_descriptor {
#     location = "s3://${var.s3_name}/data/table=ConnectionJson/"

#     input_format  = "org.apache.hadoop.mapred.TextInputFormat"
#     output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

#     ser_de_info {
#       serialization_library = "org.openx.data.jsonserde.JsonSerDe"
      
#       parameters = {
#         "serialization.format"  = 1
#         "ignore.malformed.json" = false
#         "dots.in.keys"          = false
#         "case.insensitive"      = true
#         "mapping"               = true
#       }
#     }

#     columns {
#       name = "meta_event_type"
#       type = "string"
#     }
#     columns {
#       name = "modified_action"
#       type = "string"
#     }
#     columns {
#       name = "modified_at"
#       type = "timestamp"
#     }
#     columns {
#       name = "id"
#       type = "string"
#     }
#     columns {
#       name = "account_id"
#       type = "string"
#     }
#     columns {
#       name = "game_id"
#       type = "string"
#     }
#     columns {
#       name = "version"
#       type = "int"
#     }
#     columns {
#       name = "nickname"
#       type = "string"
#     }

#   }
# }

resource "aws_glue_catalog_table" "game" {
  name          = "game"
  database_name = aws_athena_database.athena.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    EXTERNAL       = "TRUE"
    classification = "parquet"
  }

  storage_descriptor {
    location = "s3://${var.s3_name}/data/table=Game/"

    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
      parameters = {
        "serialization.format"  = 1
        "ignore.malformed.json" = false
        "dots.in.keys"          = false
        "case.insensitive"      = true
        "mapping"               = true
      }
    }

    columns {
      name = "meta_event_type"
      type = "string"
    }
    columns {
      name = "modified_action"
      type = "string"
    }
    columns {
      name = "modified_at"
      type = "string"
    }
    columns {
      name = "modified_by"
      type = "string"
    }
    columns {
      name = "id"
      type = "string"
    }
    columns {
      name = "version"
      type = "int"
    }
    columns {
      name = "round_finished"
      type = "boolean"
    }
    columns {
      name = "mr_eleven"
      type = "string"
    }
    # Whitespace is not allowed
    columns {
      name = "players"
      type = "array<struct<nickname:string,finished:boolean,id:string,win_counter:int,outcome:string>>"
    }

  }
}

# resource "aws_glue_catalog_table" "game_json" {
#   name          = "game_json"
#   database_name = aws_athena_database.athena.name
#   table_type    = "EXTERNAL_TABLE"
#   parameters = {
#     EXTERNAL       = "TRUE"
#     classification = "json"
#   }

#   storage_descriptor {
#     location = "s3://${var.s3_name}/data/table=GameJson/"

#     input_format  = "org.apache.hadoop.mapred.TextInputFormat"
#     output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

#     ser_de_info {
#       serialization_library = "org.openx.data.jsonserde.JsonSerDe"
#       parameters = {
#         "serialization.format"  = 1
#         "ignore.malformed.json" = false
#         "dots.in.keys"          = false
#         "case.insensitive"      = true
#         "mapping"               = true
#       }
#     }

#     columns {
#       name = "meta_event_type"
#       type = "string"
#     }
#     columns {
#       name = "modified_action"
#       type = "string"
#     }
#     columns {
#       name = "modified_at"
#       type = "timestamp"
#     }
#     columns {
#       name = "modified_by"
#       type = "string"
#     }
#     columns {
#       name = "id"
#       type = "string"
#     }
#     columns {
#       name = "version"
#       type = "int"
#     }
#     columns {
#       name = "round_finished"
#       type = "boolean"
#     }
#     columns {
#       name = "mr_eleven"
#       type = "string"
#     }
#     # Whitespace is not allowed
#     columns {
#       name = "players"
#       type = "array<struct<nickname:string,finished:boolean,id:string,win_counter:int,outcome:string>>"
#     }

#   }
# }

resource "aws_athena_named_query" "connection_list" {
  name      = "connection_list"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    SELECT
      *
    FROM 
      ${aws_glue_catalog_table.connection.name}
    LIMIT 1000;
  EOT
}

resource "aws_athena_named_query" "game_list" {
  name      = "game_list"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    SELECT
      *
    FROM 
      ${aws_glue_catalog_table.game.name}
    LIMIT 1000;
  EOT
}

resource "aws_athena_named_query" "game_count" {
  name      = "game_count"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    SELECT
      COUNT(*) AS game_count
    FROM 
      ${aws_glue_catalog_table.game.name}
    WHERE
      modified_action = 'CREATE_GAME';
  EOT
}

resource "aws_athena_named_query" "round_count" {
  name      = "round_count"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    SELECT
      COUNT(*) AS round_count
    FROM 
      ${aws_glue_catalog_table.game.name}
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND round_finished = true;
  EOT
}

resource "aws_athena_named_query" "roll_count" {
  name      = "roll_count"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    SELECT
      COUNT(*) AS roll_count
    FROM 
      ${aws_glue_catalog_table.game.name}
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE';
  EOT
}

