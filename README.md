# dbt-ggsql · community extension · posit hackathon 2026

SQL engineers already know how to transform data. What they don't have is a way to visualize it without leaving the pipeline. Every dbt project ends the same way: the marts are ready, the data is clean, and someone opens Tableau to see what's already there.

[ggsql](https://github.com/posit-dev/ggsql) extends SQL with Grammar of Graphics syntax. `dbt-ggsql` wraps both into a single command — **`dbt-ggsql build` runs your dbt pipeline and renders your visualizations in one step.**

```bash
pip install dbt-ggsql
dbt-ggsql build
```

That's it. No separate render scripts. No post-hooks. No BI tool.

---

<img src="docs/sample_visualizations.html" alt="sample output" width="0" height="0"/>

## how it works

Place `.ggsql` files in a `visualizations/` folder inside your dbt project. After `dbt build` runs, `dbt-ggsql` executes each query through the ggsql CLI and collects the Vega-Lite output. It writes:

- `output/charts/<name>.html` — one self-contained chart per file
- `output/visualizations.html` — a summary grid of all charts
- `visualizations.qmd` — a Quarto document embedding all charts as live ggsql cells

```
nba_dbt/
  models/            # dbt models (staging → mart)
  seeds/             # raw CSVs
  exports/           # parquet files (dbt post-hook writes these)
  visualizations/    # .ggsql files — one per chart
    shot_chart_knicks_cavs.ggsql
    player_comparison.ggsql
    efficiency_scoring.ggsql
    efficiency_3pt.ggsql
    …
  output/            # generated — gitignored
    charts/
    visualizations.html
```

Consecutive files that share a prefix render side-by-side in the summary grid: `efficiency_scoring.ggsql` and `efficiency_3pt.ggsql` become a paired row automatically.

## cli

```bash
dbt-ggsql build           # dbt build + all visualizations
dbt-ggsql viz             # visualizations only (skips dbt)
dbt-ggsql report          # regenerate summary HTML from existing charts
```

## quick start

```bash
git clone https://github.com/icarusz/dbtggsql-demo-extension-pkg
cd dbtggsql-demo-extension-pkg
uv sync --python 3.13
uv run dbt-ggsql build
open nba_dbt/output/visualizations.html
```

**requires:** [ggsql CLI](https://github.com/posit-dev/ggsql), Python 3.13, uv

## sample output

**[visualizations summary →](https://htmlpreview.github.io/?https://github.com/icarusz/dbtggsql-demo-extension-pkg/blob/main/docs/sample_visualizations.html)** — all charts from one `dbt-ggsql build` run: shot charts, efficiency comparisons, and player scatter plots.

**[player comparison →](https://htmlpreview.github.io/?https://github.com/icarusz/dbtggsql-demo-extension-pkg/blob/main/docs/sample_player_comparison.html)** — playoff scoring vs assists, labeled by player name.

**[shot chart: Knicks vs Cavs →](https://htmlpreview.github.io/?https://github.com/icarusz/dbtggsql-demo-extension-pkg/blob/main/docs/sample_shot_chart.html)** — individual chart output.

## related

**[dbtggsql-demo](https://github.com/icarusz/dbtggsql-demo)** — the original project, using Makefiles and the ggsql CLI with three output modes (individual charts, static bundle, full Quarto report).

**[dbtggsql-demo-modifieddbt](https://github.com/icarusz/dbtggsql-demo-modifieddbt)** — a fork of dbt-core that adds `visualization` as a native node type running inside `dbt build` itself.
