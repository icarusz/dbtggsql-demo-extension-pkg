-- Game-by-game playoff scores for both teams — powers margin charts and score timelines
SELECT
    team,
    conference,
    round,
    round_num,
    opponent,
    game_num,
    playoff_game_num,
    team_score,
    opp_score,
    margin,
    result,
    is_win,
    location
FROM {{ ref('stg_playoff_games') }}
ORDER BY team, round_num, game_num
