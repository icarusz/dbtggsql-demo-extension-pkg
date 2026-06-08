SELECT
    team,
    conference,
    round,
    round_num,
    opponent,
    game_num,
    team_score,
    opp_score,
    team_score - opp_score                             AS margin,
    result,
    location,
    CASE WHEN result = 'W' THEN 1 ELSE 0 END           AS is_win,
    ROW_NUMBER() OVER (
        PARTITION BY team ORDER BY round_num, game_num
    )                                                  AS playoff_game_num
FROM {{ ref('raw_playoff_games') }}
