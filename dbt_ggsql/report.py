"""
report.py — generates two outputs from a list of ChartResult objects:
  1. output/visualizations.html  — self-contained summary grid of all charts
  2. visualizations.qmd          — Quarto document embedding all charts
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .runner import ChartResult


# ── visualizations.html ───────────────────────────────────────────────────────

_SUMMARY_HEAD = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>visualizations · ggsql + dbt</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@6"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    :root {
      --teal:  #0A9396;
      --dteal: #005F73;
      --pteal: #DEF1EB;
      --black: #001219;
      --dbt:   #FF694B;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Nunito Sans', system-ui, sans-serif;
      background: #f8fafc;
      color: var(--black);
    }
    header {
      background: var(--black);
      color: var(--pteal);
      padding: 1.4em 2em;
      display: flex;
      align-items: baseline;
      gap: 1em;
    }
    header h1 { font-size: 1.3rem; font-weight: 700; }
    header span { font-size: 0.85rem; color: #94D2BD; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(520px, 1fr));
      gap: 24px;
      padding: 28px;
      max-width: 1400px;
      margin: 0 auto;
    }
    .card {
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px #0000000f;
      overflow: hidden;
    }
    .card-title {
      background: var(--teal);
      color: white;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 6px 14px;
      letter-spacing: 0.03em;
      font-family: monospace;
    }
    .vis-wrap { padding: 8px; }
    .vis-wrap div { width: 100%; height: 340px; }
    footer {
      text-align: center;
      padding: 2em;
      font-size: 0.8rem;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
      margin-top: 12px;
    }
  </style>
</head>
<body>
<header>
  <h1>visualizations</h1>
  <span>ggsql + dbt · posit hackathon 2026</span>
</header>
<div class="grid">
"""

_SUMMARY_CARD = """\
<div class="card">
  <div class="card-title">{name}</div>
  <div class="vis-wrap"><div id="vis-{idx}"></div></div>
</div>
"""

_SUMMARY_SCRIPT_OPEN = """\
</div>
<footer>built by dbt-ggsql · charts rendered with vega-lite</footer>
<script>
"""

_SUMMARY_SCRIPT_ENTRY = """\
(function() {{
  const spec = {spec};
  spec.width = "container";
  spec.height = 300;
  vegaEmbed('#vis-{idx}', spec, {{ actions: false, renderer: 'svg' }}).catch(console.error);
}})();
"""

_SUMMARY_TAIL = """\
</script>
</body>
</html>
"""


def write_summary_html(
    results: list[ChartResult],
    project_root: str,
    output_path: str = os.path.join("output", "visualizations.html"),
) -> str:
    """Write a self-contained summary HTML grid of all charts."""
    successful = [r for r in results if r.success]
    out_file = Path(project_root) / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    parts = [_SUMMARY_HEAD]
    for idx, r in enumerate(successful):
        parts.append(_SUMMARY_CARD.format(name=r.name, idx=idx))

    parts.append(_SUMMARY_SCRIPT_OPEN)
    for idx, r in enumerate(successful):
        parts.append(_SUMMARY_SCRIPT_ENTRY.format(spec=r.vega_spec, idx=idx))

    parts.append(_SUMMARY_TAIL)
    out_file.write_text("".join(parts), encoding="utf-8")
    return str(out_file)


# ── visualizations.qmd ────────────────────────────────────────────────────────

_QMD_HEADER = """\
---
title: "2026 NBA Finals · visualizations"
subtitle: "ggsql + dbt · posit hackathon 2026"
format:
  html:
    theme: flatly
    toc: true
    toc-title: "charts"
    embed-resources: true
    code-fold: true
    code-summary: "show query"
jupyter: ggsql
---

"""

_QMD_SECTION = """\
## {title}

```{{ggsql}}
{query}
```

"""


def write_qmd(
    viz_dir: str,
    project_root: str,
    qmd_path: str = "visualizations.qmd",
) -> str:
    """Generate a Quarto document with one ggsql cell per visualization file."""
    viz_path = Path(project_root) / viz_dir
    out_file = Path(project_root) / qmd_path

    sections = [_QMD_HEADER]
    for ggsql_file in sorted(viz_path.glob("*.ggsql")):
        name = ggsql_file.stem
        title = name.replace("_", " ")
        query = ggsql_file.read_text(encoding="utf-8").strip()
        sections.append(_QMD_SECTION.format(title=title, query=query))

    out_file.write_text("".join(sections), encoding="utf-8")
    return str(out_file)
