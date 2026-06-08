SELECT
    player,
    team,
    position,
    stat_type,
    games,
    ppg,
    rpg,
    apg,
    spg,
    bpg,
    fg_pct,
    three_pt_pct,
    ts_pct,
    -- Simple impact metric: weighted sum of key stats
    ROUND(ppg + rpg * 1.2 + apg * 1.5 + spg * 2 + bpg * 2, 1) AS impact_score
FROM {{ ref('raw_player_stats') }}
