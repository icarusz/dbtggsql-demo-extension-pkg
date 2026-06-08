-- Shot-by-shot chart data with coordinates — powers the ggsql shot chart scatter plot
SELECT
    team_name                               AS team,
    player_name                             AS player,
    game_date,
    period,
    game_second,
    action_type,
    shot_type,
    zone,
    zone_area,
    distance_range,
    shot_distance,
    loc_x,
    loc_y,
    made,
    made_label,
    category,
    opponent_abbr,
    opponent
FROM {{ ref('stg_shot_chart') }}
