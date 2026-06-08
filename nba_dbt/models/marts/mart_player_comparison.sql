-- Regular season vs. playoff splits per player — powers scatter and delta bar charts
WITH reg AS (
    SELECT * FROM {{ ref('stg_player_stats') }} WHERE stat_type = 'regular_season'
),
po AS (
    SELECT * FROM {{ ref('stg_player_stats') }} WHERE stat_type = 'playoffs'
)
SELECT
    r.player,
    r.team,
    r.position,
    -- Regular season
    r.ppg                               AS reg_ppg,
    r.rpg                               AS reg_rpg,
    r.apg                               AS reg_apg,
    r.fg_pct                            AS reg_fg_pct,
    r.ts_pct                            AS reg_ts_pct,
    r.impact_score                      AS reg_impact,
    -- Playoffs
    p.ppg                               AS playoff_ppg,
    p.rpg                               AS playoff_rpg,
    p.apg                               AS playoff_apg,
    p.fg_pct                            AS playoff_fg_pct,
    p.ts_pct                            AS playoff_ts_pct,
    p.impact_score                      AS playoff_impact,
    -- Deltas (positive = improved in playoffs)
    ROUND(p.ppg    - r.ppg,    1)       AS ppg_delta,
    ROUND(p.fg_pct - r.fg_pct, 1)       AS fg_pct_delta,
    ROUND(p.ts_pct - r.ts_pct, 1)       AS ts_pct_delta
FROM reg r
JOIN po p ON r.player = p.player
ORDER BY r.team, p.ppg DESC
