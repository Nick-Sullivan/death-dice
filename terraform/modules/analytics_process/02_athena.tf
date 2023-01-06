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
      type = "array<struct<nickname:string,finished:boolean,id:string,win_counter:int,outcome:string,rolls:array<struct<dice:array<struct<id:string,value:int,is_death_dice:boolean>>>>>>"
    }

  }
}


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

resource "aws_athena_named_query" "roll_count_per_account" {
  name      = "roll_count_per_account"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    WITH 
      rolls AS (
        SELECT
          game.modified_by as player_id
        FROM 
          game
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
      ),
      accounts AS (
        SELECT
          id as player_id,
          account_id
        FROM
          connection
        WHERE
          meta_event_type = 'REMOVE'
      )

    SELECT
      accounts.account_id,
      COUNT(*) as roll_count
    FROM
      rolls
      INNER JOIN accounts ON rolls.player_id = accounts.player_id
    GROUP BY
      accounts.account_id
    ;
  EOT
}

resource "aws_athena_named_query" "roll_count_for_account" {
  name      = "roll_count_for_account"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    WITH 
      rolls AS (
        SELECT
          game.modified_by as player_id
        FROM 
          game
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
      ),
      accounts AS (
        SELECT
          id as player_id,
          account_id
        FROM
          connection
        WHERE
          meta_event_type = 'REMOVE'
          AND account_id = ?
      )

    SELECT
      accounts.account_id,
      COUNT(*) as roll_count
    FROM
      rolls
      INNER JOIN accounts ON rolls.player_id = accounts.player_id
    GROUP BY
      accounts.account_id
    ;
  EOT
}

resource "aws_athena_named_query" "all_stats_per_account" {
  name      = "all_stats_per_account"
  workgroup = aws_athena_workgroup.athena.id
  database  = aws_athena_database.athena.name
  query     = <<-EOT
    WITH
      -- COMMON
      game_time_range AS (
        SELECT
          *
        FROM
          game
        WHERE
          parse_datetime(game.modified_at, 'yyyy-MM-dd HH:mm:ss.SSSSSS') BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '1' DAY
      ),
      connection_time_range AS (
        SELECT
          *
        FROM
          connection
        WHERE
          parse_datetime(connection.modified_at, 'yyyy-MM-dd HH:mm:ss.SSSSSS') BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '1' DAY
      ),
      game_per_player AS (
        SELECT
          game_time_range.*,
          player
        FROM
          game_time_range
          CROSS JOIN UNNEST(players) AS t(player)
      ),
      accounts AS (
        SELECT
          id AS player_id,
          account_id
        FROM
          connection_time_range
        WHERE
          meta_event_type = 'REMOVE'
      ),
          
      -- BASIC ACTIONS
      games_played AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS games_played
        FROM
          game_time_range
        WHERE
          meta_event_type in ('INSERT', 'MODIFY')
          AND modified_action IN ('CREATE_GAME', 'JOIN_GAME')
        GROUP BY
          modified_by
      ),
      dice_rolled AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS dice_rolled
        FROM
          game_time_range
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
        GROUP BY
          modified_by
      ),
          
      -- LAST ROLL OUTCOMES
      rounds_played AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS rounds_played
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND round_finished = true
          AND player.outcome = 'WINNER'
        GROUP BY
          modified_by
      ),
      rounds_tied AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS rounds_tied
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND round_finished = true
          AND player.outcome = 'TIE'
        GROUP BY
          modified_by
      ),
      rounds_won AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS rounds_won,
          MAX(player.win_counter) AS biggest_win_counter
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND round_finished = true
          AND player.outcome = 'WINNER'
        GROUP BY
          modified_by
      ),
      drinks_sipped AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS drinks_sipped
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND round_finished = true
          AND player.outcome = 'SIP_DRINK'
        GROUP BY
          modified_by
      ),
          
      -- IMMEDIATE OUTCOMES
      drinks_finished AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS drinks_finished
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'FINISH_DRINK'
        GROUP BY
          modified_by
      ),
      dual_wields AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS dual_wields
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'DUAL_WIELD'
        GROUP BY
          modified_by
      ),
      showers AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS showers
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'SHOWER'
        GROUP BY
          modified_by
      ),
      head_on_tables AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS head_on_tables
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'HEAD_ON_TABLE'
        GROUP BY
          modified_by
      ),
      gifts_from_wish AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS gifts_from_wish
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'WISH_PURCHASE'
        GROUP BY
          modified_by
      ),
      pools AS (
        SELECT
          modified_by AS player_id,
          COUNT(*) AS pools
        FROM
          game_per_player
        WHERE
          meta_event_type = 'MODIFY'
          AND modified_action = 'ROLL_DICE'
          AND modified_by = player.id
          AND player.outcome = 'POOL'
        GROUP BY
          modified_by
      )
          
    SELECT
      accounts.account_id,
      CURRENT_DATE as date_id,
      SUM(games_played.games_played) AS games_played,
      SUM(dice_rolled.dice_rolled) AS dice_rolled,
      SUM(rounds_played.rounds_played) AS rounds_played,
      SUM(rounds_tied.rounds_tied) AS rounds_tied,
      SUM(rounds_won.rounds_won) AS rounds_won,
      SUM(drinks_sipped.drinks_sipped) AS drinks_sipped,
      SUM(drinks_finished.drinks_finished) AS drinks_finished,
      SUM(dual_wields.dual_wields) AS dual_wields,
      SUM(showers.showers) AS showers,
      SUM(head_on_tables.head_on_tables) AS head_on_tables,
      SUM(gifts_from_wish.gifts_from_wish) AS gifts_from_wish,
      SUM(pools.pools) AS pools
    FROM 
      accounts
      LEFT JOIN games_played ON accounts.player_id = games_played.player_id
      LEFT JOIN dice_rolled ON accounts.player_id = dice_rolled.player_id
      LEFT JOIN rounds_played ON accounts.player_id = rounds_played.player_id
      LEFT JOIN rounds_tied ON accounts.player_id = rounds_tied.player_id
      LEFT JOIN rounds_won ON accounts.player_id = rounds_won.player_id
      LEFT JOIN drinks_sipped ON accounts.player_id = drinks_sipped.player_id
      LEFT JOIN drinks_finished ON accounts.player_id = drinks_finished.player_id
      LEFT JOIN dual_wields ON accounts.player_id = dual_wields.player_id
      LEFT JOIN showers ON accounts.player_id = showers.player_id
      LEFT JOIN head_on_tables ON accounts.player_id = head_on_tables.player_id
      LEFT JOIN gifts_from_wish ON accounts.player_id = gifts_from_wish.player_id
      LEFT JOIN pools ON accounts.player_id = pools.player_id
    GROUP BY
      account_id
    ;

  EOT
}


// -- TRIGGERED BY PLAYER ACTION

// games played  -  MODIFY/JOIN_GAME matching modified_by, count

// dice rolled - MODIFY/ROLL_DICE matching modified_by, count
// LATER biggest roll - MODIFY/ROLL_DICE matching modified_by, sum roll values
// LATER rolls with death dice - MODIFY/ROLL_DICE matching modified_by is_death_dice

// -- TRIGGERED BY OTHER PLAYERS

// sips - MODIFY/ROLL_DICE/round_finished/player.outcome=SIP_DRINK, count
// rounds won - MODIFY/ROLL_DICE/round_finished/player.outcome=WINNER
// biggest win_counter - MODIFY/ROLL_DICE/round_finished/player.outcome=WINNER, max(win_counter)
// rounds tied - MODIFY/ROLL_DICE/round_finished/player.outcome=TIE
// rounds played - MODIFY/ROLL_DICE/round_finished matching in players, count
// three way ties - MODIFY/ROLL_DICE/player.outcome=THREE_WAY_TIE


// -- MID ROUND

// finished drinks - MODIFY/ROLL_DICE matching modified_by
// dual wield - MODIFY/ROLL_DICE matching modified_by
// showers - MODIFY/ROLL_DICE matching modified_by
// heads on tables - MODIFY/ROLL_DICE matching modified_by
// wish.com - MODIFY/ROLL_DICE matching modified_by
// pool - MODIFY/ROLL_DICE matching modified_by

// finished drinks (safe)
// dual wield (safe)
// showers (safe)
// heads on tables (safe)
// wish.com (safe)
// pool (safe)

// account age
