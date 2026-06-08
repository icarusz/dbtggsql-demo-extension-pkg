-- Series-level playoff summary with opponent difficulty — powers path-to-Finals charts
WITH series AS (
    SELECT
        team,
        round,
        round_num,
        opponent,
        COUNT(*)                            AS games_played,
        SUM(is_win)                         AS wins,
        COUNT(*) - SUM(is_win)              AS losses,
        ROUND(AVG(margin), 1)               AS avg_margin,
        SUM(team_score)                     AS total_scored,
        SUM(opp_score)                      AS total_allowed,
        SUM(team_score) - SUM(opp_score)    AS total_margin
    FROM {{ ref('stg_playoff_games') }}
    GROUP BY team, round, round_num, opponent
)
SELECT
    s.team,
    s.round,
    s.round_num,
    s.opponent,
    s.games_played,
    s.wins,
    s.losses,
    s.avg_margin,
    s.total_scored,
    s.total_allowed,
    s.total_margin,
    o.seed                                  AS opp_seed,
    o.reg_season_wins                       AS opp_wins,
    o.net_rtg                               AS opp_net_rtg,
    o.difficulty_score
FROM series s
LEFT JOIN {{ ref('stg_playoff_opponents') }} o
    ON s.opponent = o.team
ORDER BY s.team, s.round_num
