SELECT
    team,
    eliminated_by,
    round,
    round_num,
    conference,
    reg_season_wins,
    reg_season_losses,
    seed,
    ppg,
    opp_ppg,
    net_rtg,
    series_result,
    series_wins,
    series_losses,
    -- Difficulty score: lower seed + higher net rating = harder opponent
    ROUND((30 - seed) * 1.5 + net_rtg, 1)             AS difficulty_score
FROM {{ ref('raw_playoff_opponents') }}
