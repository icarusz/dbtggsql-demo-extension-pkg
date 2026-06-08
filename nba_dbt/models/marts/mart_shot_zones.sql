-- Shot zone breakdown (offense + defense allowed) — powers zone bar/tile charts
SELECT
    team,
    stat_type,
    shot_zone,
    fga,
    fgm,
    fg_pct,
    pct_of_fga,
    -- Canonical zone ordering for chart axis sorting
    CASE shot_zone
        WHEN 'Restricted Area'        THEN 1
        WHEN 'In The Paint (Non-RA)'  THEN 2
        WHEN 'Mid-Range'              THEN 3
        WHEN 'Left Corner 3'          THEN 4
        WHEN 'Right Corner 3'         THEN 5
        WHEN 'Above the Break 3'      THEN 6
        ELSE 7
    END                                     AS zone_order
FROM {{ ref('raw_shot_zones') }}
ORDER BY team, stat_type, zone_order
