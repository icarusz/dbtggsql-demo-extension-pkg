SELECT
    game_num,
    date::DATE                                          AS game_date,
    location,
    context,
    knicks_score,
    spurs_score,
    knicks_score - spurs_score                          AS knicks_margin,
    winner,
    CASE WHEN knicks_score > spurs_score THEN 'W' ELSE 'L' END AS knicks_result
FROM {{ ref('raw_head_to_head') }}
