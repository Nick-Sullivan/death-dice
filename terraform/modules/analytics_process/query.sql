WITH 
  accounts AS (
    SELECT 
      id AS player_id,
      account_id
    FROM 
      connection
    WHERE 
      meta_event_type = 'REMOVE'
  ),

  game_per_player AS (
    SELECT 
      game.*,
      player
    FROM 
      game
      CROSS JOIN UNNEST(players) AS t(player)
  ),

  games_played AS (
    SELECT 
      date_id,
      player.id AS player_id,
      'games_played' AS metric,
      COUNT( DISTINCT id ) AS count
    FROM 
      game_per_player
    WHERE 
      player.finished
      AND player.outcome != ''  --Just joined
    GROUP BY 
      date_id,
      player.id
  ),
  rounds_played AS (
    SELECT
      date_id,
      player.id AS player_id,
      'rounds_played' AS metric,
      COUNT( DISTINCT round_id ) AS count
    FROM
      game_per_player
    WHERE
      player.finished
      AND player.outcome != ''  --Just joined
    GROUP BY
      date_id,
      player.id
  ),
  dice_rolled AS (
    SELECT 
      date_id,
      modified_by AS player_id,
      'dice_rolled' as metric,
      COUNT(*) AS count
    FROM 
      game
    WHERE 
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
    GROUP BY 
      date_id,
      modified_by
  ),
  round_outcomes AS (
    SELECT
      date_id,
      player.id AS player_id,
      CONCAT('outcome_', LOWER(player.outcome)) AS metric,
      COUNT( DISTINCT round_id ) AS count
    FROM
      game_per_player
    WHERE
      player.finished = true
      AND player.outcome != ''  --Just joined
    GROUP BY
      date_id,
      player.id,
      player.outcome
  ),

  all_stats_by_player AS (
    SELECT * FROM games_played
    UNION ALL SELECT * FROM rounds_played
    UNION ALL SELECT * FROM dice_rolled
    UNION ALL SELECT * FROM round_outcomes
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
