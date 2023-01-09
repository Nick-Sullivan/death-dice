-- Note, due to DISTINCT these aggregations are not correct for players without accounts

WITH 
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
      player.account_id AS account_id,
      'games_played' AS metric,
      COUNT( DISTINCT id ) AS count
    FROM 
      game_per_player
    WHERE 
      player.finished
      AND player.outcome != ''  --Just joined
    GROUP BY 
      date_id,
      player.account_id
  ),
  rounds_played AS (
    SELECT
      date_id,
      player.account_id AS account_id,
      'rounds_played' AS metric,
      COUNT( DISTINCT round_id ) AS count
    FROM
      game_per_player
    WHERE
      player.finished
      AND player.outcome != ''  --Just joined
    GROUP BY
      date_id,
      player.account_id
  ),
  dice_rolled AS (
    SELECT 
      date_id,
      player.account_id AS account_id,
      'dice_rolled' as metric,
      COUNT(*) AS count
    FROM 
      game_per_player
    WHERE 
      meta_event_type = 'MODIFY'
      AND modified_action = 'ROLL_DICE'
      AND player.id = modified_by
    GROUP BY 
      date_id,
      player.account_id
  ),
  round_outcomes AS (
    SELECT
      date_id,
      player.account_id AS account_id,
      CONCAT('outcome_', LOWER(player.outcome)) AS metric,
      COUNT( DISTINCT round_id ) AS count
    FROM
      game_per_player
    WHERE
      player.finished = true
      AND player.outcome != ''  --Just joined
    GROUP BY
      date_id,
      player.account_id,
      player.outcome
  ),
  all_stats AS (
    SELECT * FROM games_played
    UNION ALL SELECT * FROM rounds_played
    UNION ALL SELECT * FROM dice_rolled
    UNION ALL SELECT * FROM round_outcomes
  )

SELECT 
  * 
FROM 
  all_stats
WHERE 
  date_id = ?
  AND account_id IS NOT NULL
