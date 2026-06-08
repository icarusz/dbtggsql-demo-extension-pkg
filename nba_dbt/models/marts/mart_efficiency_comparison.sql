-- Unpivoted regular-season vs playoff efficiency — powers reg/playoff comparison charts
-- Each row: (team, metric, period, value)
-- ggsql: VISUALISE metric AS x, value AS y, period AS color  DRAW bar  SETTING position => 'dodge'  FACET team

WITH reg AS (
    SELECT * FROM {{ ref('stg_regular_season') }}
),

playoff_scores AS (
    SELECT
        team,
        ROUND(AVG(team_score), 1)  AS playoff_ppg,
        ROUND(AVG(opp_score),  1)  AS playoff_opp_ppg,
        ROUND(AVG(margin),     1)  AS playoff_margin,
        COUNT(*)                   AS playoff_games
    FROM {{ ref('stg_playoff_games') }}
    GROUP BY team
),

-- 3PT offense in playoffs (all three zones combined)
playoff_three_off AS (
    SELECT
        team,
        ROUND(SUM(fgm) * 100.0 / NULLIF(SUM(fga), 0), 1) AS playoff_three_pct
    FROM {{ ref('raw_shot_zones') }}
    WHERE stat_type = 'playoffs'
      AND shot_zone IN ('Above the Break 3', 'Left Corner 3', 'Right Corner 3')
    GROUP BY team
),

-- 3PT defense in playoffs (opponents' 3PT against this team)
playoff_three_def AS (
    SELECT
        team,
        ROUND(SUM(fgm) * 100.0 / NULLIF(SUM(fga), 0), 1) AS playoff_opp_three_pct
    FROM {{ ref('raw_shot_zones') }}
    WHERE stat_type = 'playoffs_allowed'
      AND shot_zone IN ('Above the Break 3', 'Left Corner 3', 'Right Corner 3')
    GROUP BY team
),

combined AS (
    SELECT
        r.team,
        -- Regular season
        r.ppg                     AS reg_ppg,
        r.opp_ppg                 AS reg_opp_ppg,
        r.off_rtg                 AS reg_off_rtg,
        r.def_rtg                 AS reg_def_rtg,
        r.three_pt_pct            AS reg_three_pct,
        r.opp_three_pt_pct        AS reg_opp_three_pct,
        -- Playoffs
        p.playoff_ppg,
        p.playoff_opp_ppg,
        p.playoff_margin,
        t3o.playoff_three_pct,
        t3d.playoff_opp_three_pct
    FROM reg r
    JOIN playoff_scores    p   ON r.team = p.team
    JOIN playoff_three_off t3o ON r.team = t3o.team
    JOIN playoff_three_def t3d ON r.team = t3d.team
)

-- Unpivot into long format
SELECT team, 'Scoring'        AS category, 'Offense'  AS side, 'Regular Season' AS period, reg_ppg            AS value FROM combined
UNION ALL
SELECT team, 'Scoring'        AS category, 'Offense'  AS side, 'Playoffs'        AS period, playoff_ppg        AS value FROM combined
UNION ALL
SELECT team, 'Scoring'        AS category, 'Defense'  AS side, 'Regular Season' AS period, reg_opp_ppg        AS value FROM combined
UNION ALL
SELECT team, 'Scoring'        AS category, 'Defense'  AS side, 'Playoffs'        AS period, playoff_opp_ppg   AS value FROM combined
UNION ALL
SELECT team, '3PT Shooting'   AS category, 'Offense'  AS side, 'Regular Season' AS period, reg_three_pct      AS value FROM combined
UNION ALL
SELECT team, '3PT Shooting'   AS category, 'Offense'  AS side, 'Playoffs'        AS period, playoff_three_pct AS value FROM combined
UNION ALL
SELECT team, '3PT Shooting'   AS category, 'Defense'  AS side, 'Regular Season' AS period, reg_opp_three_pct  AS value FROM combined
UNION ALL
SELECT team, '3PT Shooting'   AS category, 'Defense'  AS side, 'Playoffs'        AS period, playoff_opp_three_pct AS value FROM combined
