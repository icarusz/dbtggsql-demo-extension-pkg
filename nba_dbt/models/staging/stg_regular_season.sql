SELECT
    team,
    conference,
    seed,
    wins,
    losses,
    wins + losses                                       AS games_played,
    ROUND(wins::FLOAT / (wins + losses) * 100, 1)      AS win_pct,
    ppg,
    opp_ppg,
    ROUND(ppg - opp_ppg, 1)                            AS ppg_margin,
    fg_pct,
    three_pt_pct,
    opp_three_pt_pct,
    off_rtg,
    def_rtg,
    net_rtg,
    pace
FROM {{ ref('raw_regular_season') }}
