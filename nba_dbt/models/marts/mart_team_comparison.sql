-- Unpivoted team stats — one row per team/metric for easy bar chart comparisons in ggsql
WITH base AS (
    SELECT * FROM {{ ref('stg_regular_season') }}
)
SELECT team, 'Wins'        AS metric, wins::FLOAT   AS value FROM base
UNION ALL
SELECT team, 'Win %'       AS metric, win_pct        AS value FROM base
UNION ALL
SELECT team, 'PPG'         AS metric, ppg             AS value FROM base
UNION ALL
SELECT team, 'Opp PPG'     AS metric, opp_ppg         AS value FROM base
UNION ALL
SELECT team, 'PPG Margin'  AS metric, ppg_margin      AS value FROM base
UNION ALL
SELECT team, 'Off Rating'  AS metric, off_rtg          AS value FROM base
UNION ALL
SELECT team, 'Def Rating'  AS metric, def_rtg          AS value FROM base
UNION ALL
SELECT team, 'Net Rating'  AS metric, net_rtg          AS value FROM base
UNION ALL
SELECT team, '3PT%'        AS metric, three_pt_pct     AS value FROM base
UNION ALL
SELECT team, 'FG%'         AS metric, fg_pct           AS value FROM base
