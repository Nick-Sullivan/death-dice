locals {
  s3_output_arn      = "${var.s3_arn}/athena"
  s3_output_location = "s3://${var.s3_name}/athena"
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
      output_location = local.s3_output_location
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
    location      = "s3://${var.s3_name}/data/table=Connection/"
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
      name = "date_id"
      type = "string"
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

resource "aws_glue_catalog_table" "game" {
  name          = "game"
  database_name = aws_athena_database.athena.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    EXTERNAL       = "TRUE"
    classification = "parquet"
  }

  partition_keys {
    name    = "date_id"
    type    = "string"
    comment = "YYYY-MM-DD of when this was modified"
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
      name = "round_id"
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
      type = "array<struct<id:string,account_id:string,nickname:string,finished:boolean,win_counter:int,outcome:string,rolls:array<struct<dice:array<struct<id:string,value:int,is_death_dice:boolean>>>>>>"
    }
    columns {
      name = "spectators"
      type = "array<struct<id:string,account_id:string,nickname:string>>"
    }

  }
}

resource "aws_athena_named_query" "all_stats_per_account" {
  name      = "all_stats_per_account"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = file("${path.module}/query.sql")
}
