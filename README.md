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

Place `.ggsql` files in a `visualizations/` folder inside your dbt project. After `dbt build` runs, `dbt-ggsql` executes each query through the ggsql CLI and collects the Vega-Lite output. The output format is configurable:

| `--output` | what you get |
|---|---|
| `html` *(default)* | `output/visualizations.html` — self-contained SVG grid, works in any browser or static viewer |
| `qmd` | `visualizations.qmd` — Quarto document with live ggsql cells and SQL visible via code-fold |
| `both` | both files |

Individual charts always write to `output/charts/<name>.html`.

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
dbt-ggsql build                        # dbt build + visualizations → html (default)
dbt-ggsql build --output qmd           # dbt build + visualizations → quarto doc
dbt-ggsql build --output both          # dbt build + visualizations → html + quarto

dbt-ggsql viz                          # visualizations only (skip dbt build)
dbt-ggsql report                       # re-render and regenerate html (default)
dbt-ggsql report --output qmd          # re-render and regenerate quarto doc
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

**[visualizations.html →](https://htmlpreview.github.io/?https://github.com/icarusz/dbtggsql-demo-extension-pkg/blob/main/docs/sample_visualizations.html)** (`--output html`) — self-contained SVG grid: shot charts, efficiency comparisons, and player scatter plots. No JavaScript, works in any static viewer.

**[visualizations.qmd →](https://github.com/icarusz/dbtggsql-demo-extension-pkg/blob/main/nba_dbt/visualizations.qmd)** (`--output qmd`) — the Quarto source with one live ggsql cell per chart. SQL is visible via code-fold; render locally with `quarto render` using the ggsql kernel.

## related

**[dbtggsql-demo](https://github.com/icarusz/dbtggsql-demo)** — the original project, using Makefiles and the ggsql CLI with three output modes (individual charts, static bundle, full Quarto report).

**[dbtggsql-demo-modifieddbt](https://github.com/icarusz/dbtggsql-demo-modifieddbt)** — a fork of dbt-core that adds `visualization` as a native node type running inside `dbt build` itself.
