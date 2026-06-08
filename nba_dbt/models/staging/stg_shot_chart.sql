SELECT
    game_id,
    strptime(game_date::VARCHAR, '%Y%m%d')::DATE        AS game_date,
    team_name,
    player_name,
    period,
    minutes_remaining,
    seconds_remaining,
    -- Seconds elapsed in the game (regulation periods only)
    (period - 1) * 720
        + (12 - minutes_remaining) * 60
        + (60 - seconds_remaining)                     AS game_second,
    action_type,
    shot_type,
    shot_zone_basic                                     AS zone,
    shot_zone_area                                      AS zone_area,
    shot_zone_range                                     AS distance_range,
    shot_distance,
    loc_x,
    loc_y,
    shot_made_flag                                      AS made,
    made_label,
    shot_category                                       AS category,
    htm,
    vtm,
    -- Opponent abbreviation
    CASE
        WHEN team_name = 'San Antonio Spurs'
            THEN CASE WHEN htm = 'SAS' THEN vtm ELSE htm END
        WHEN team_name = 'New York Knicks'
            THEN CASE WHEN htm = 'NYK' THEN vtm ELSE htm END
    END                                                AS opponent_abbr,
    -- Opponent full name
    CASE
        WHEN team_name = 'San Antonio Spurs' THEN
            CASE CASE WHEN htm = 'SAS' THEN vtm ELSE htm END
                WHEN 'POR' THEN 'Portland Trail Blazers'
                WHEN 'MIN' THEN 'Minnesota Timberwolves'
                WHEN 'OKC' THEN 'Oklahoma City Thunder'
            END
        WHEN team_name = 'New York Knicks' THEN
            CASE CASE WHEN htm = 'NYK' THEN vtm ELSE htm END
                WHEN 'ATL' THEN 'Atlanta Hawks'
                WHEN 'PHI' THEN 'Philadelphia 76ers'
                WHEN 'CLE' THEN 'Cleveland Cavaliers'
            END
    END                                                AS opponent
FROM {{ ref('raw_shot_chart') }}
