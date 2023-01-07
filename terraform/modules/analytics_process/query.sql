WITH 
  -- COMMON
  connection_with_date AS (
    SELECT 
      date_format(parse_datetime(connection.modified_at, 'yyyy-MM-dd HH:mm:ss.SSSSSS'), '%Y-%m-%d') as date_id,
      connection.*
    FROM 
      connection
  ),
  game_with_date AS (
    SELECT 
      date_format(parse_datetime(game.modified_at, 'yyyy-MM-dd HH:mm:ss.SSSSSS'), '%Y-%m-%d') as date_id,
      game.*
    FROM 
      game
  ),
  game_per_player AS (
    SELECT 
      game_with_date.*,
      player
    FROM 
      game_with_date
      CROSS JOIN UNNEST(players) AS t(player)
  ),

  -- BASIC ACTIONS
  games_played AS (
    SELECT 
      date_id,
      modified_by AS player_id,
      'games_played' AS metric,
      COUNT(*) AS count
    FROM 
      game_with_date
    WHERE 
      meta_event_type in ('INSERT', 'MODIFY')
      AND modified_action IN ('CREATE_GAME', 'JOIN_GAME')
    GROUP BY 
      date_id,
      modified_by
  ),
  dice_rolled AS (
    SELECT 
      date_id,
      modified_by AS player_id,
      'dice_rolled' as metric,
      COUNT(*) AS count
    FROM 
      game_with_date
    WHERE 
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
    GROUP BY 
      date_id,
      modified_by
  ),

  -- LAST ROLL OUTCOMES
  rounds_played AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'rounds_played' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND round_finished = true
      AND player.outcome = 'WINNER'
    GROUP BY
      date_id,
      modified_by
  ),
  rounds_tied AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'rounds_tied' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND round_finished = true
      AND player.outcome = 'TIE'
    GROUP BY
      date_id,
      modified_by
  ),
  rounds_won AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'rounds_won' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND round_finished = true
      AND player.outcome = 'WINNER'
    GROUP BY
      date_id,
      modified_by
  ),
  drinks_sipped AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'drinks_sipped' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND round_finished = true
      AND player.outcome = 'SIP_DRINK'
    GROUP BY
      date_id,
      modified_by
  ),
      
  -- IMMEDIATE OUTCOMES
  drinks_finished AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'drinks_finished' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'FINISH_DRINK'
    GROUP BY
      date_id,
      modified_by
  ),
  dual_wields AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'dual_wields' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'DUAL_WIELD'
    GROUP BY
      date_id,
      modified_by
  ),
  showers AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'showers' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'SHOWER'
    GROUP BY
      date_id,
      modified_by
  ),
  head_on_tables AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'head_on_tables' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'HEAD_ON_TABLE'
    GROUP BY
      date_id,
      modified_by
  ),
  gifts_from_wish AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'gifts_from_wish' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'WISH_PURCHASE'
    GROUP BY
      date_id,
      modified_by
  ),
  pools AS (
    SELECT
      date_id,
      modified_by AS player_id,
      'pools' AS metric,
      COUNT(*) AS count
    FROM
      game_per_player
    WHERE
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND modified_by = player.id
      AND player.outcome = 'POOL'
    GROUP BY
      date_id,
      modified_by
  ),


  accounts AS (
    SELECT 
      id AS player_id,
      account_id
    FROM 
      connection_with_date
    WHERE 
      meta_event_type = 'REMOVE'
  ),
  all_stats_by_player AS (

    SELECT * FROM games_played
    UNION ALL SELECT * FROM dice_rolled
    UNION ALL SELECT * FROM rounds_played
    UNION ALL SELECT * FROM rounds_tied
    UNION ALL SELECT * FROM rounds_won
    UNION ALL SELECT * FROM drinks_sipped
    UNION ALL SELECT * FROM drinks_finished
    UNION ALL SELECT * FROM dual_wields
    UNION ALL SELECT * FROM showers
    UNION ALL SELECT * FROM head_on_tables
    UNION ALL SELECT * FROM gifts_from_wish
    UNION ALL SELECT * FROM pools
  )

SELECT 
  accounts.account_id,
  all_stats_by_player.date_id,
  all_stats_by_player.metric,
  SUM(all_stats_by_player.count) AS count
FROM 
  accounts
	RIGHT JOIN all_stats_by_player ON accounts.player_id = all_stats_by_player.player_id
WHERE 
  all_stats_by_player.date_id = ?
GROUP BY
  accounts.account_id,
  all_stats_by_player.date_id,
  all_stats_by_player.metric
;