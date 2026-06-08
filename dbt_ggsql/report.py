"""
report.py — generates two outputs from a list of ChartResult objects:
  1. output/visualizations.html  — self-contained summary grid (SVGs inline, zero JS)
  2. visualizations.qmd          — Quarto document embedding all charts
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .runner import ChartResult


# ── SVG pre-rendering ─────────────────────────────────────────────────────────

def _spec_to_svg(vega_spec: str, is_paired: bool = False) -> str | None:
    """
    Render a Vega-Lite JSON spec to an SVG string using vl2svg.

    For facet specs (team × side charts), width/height are set on the inner
    view so each facet cell is sized correctly.  For simple specs, they sit
    at the top level.

    is_paired=True means the card shares a row with another card, so we use
    a narrower cell width to avoid overflow.
    """
    vl2svg = shutil.which("vl2svg")
    if vl2svg is None:
        return None

    try:
        spec = json.loads(vega_spec)
    except json.JSONDecodeError:
        return None

    # Decide target dimensions.  Paired cards each occupy ~half the viewport;
    # solo cards are wider.  For facet specs the numbers apply to each cell.
    if is_paired:
        cell_w, cell_h = 380, 260
    else:
        cell_w, cell_h = 680, 340

    # Facet / concat specs carry a nested "spec" for the individual view.
    inner = spec.get("spec") or spec.get("layer")
    if inner and isinstance(inner, dict):
        inner["width"] = cell_w
        inner["height"] = cell_h
    else:
        spec["width"] = cell_w
        spec["height"] = cell_h

    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(spec, tmp)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [vl2svg, tmp_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            svg = result.stdout.strip()
            # Widen the Vega clip rect to the full viewBox width so bars near
            # the right edge of the plot area are never clipped.
            vb_match = __import__("re").search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', svg)
            if vb_match:
                vb_w, vb_h = vb_match.group(1), vb_match.group(2)
                svg = __import__("re").sub(
                    r'(<clipPath[^>]*>)\s*<rect x="0" y="0" width="[^"]*" height="[^"]*"/>',
                    rf'\1<rect x="0" y="0" width="{vb_w}" height="{vb_h}"/>',
                    svg,
                )
            # Make SVG responsive: remove fixed width, let height scale naturally
            svg = svg.replace(' width="', ' data-orig-width="', 1)
            svg = svg.replace(' height="', ' style="width:100%;height:auto;" height="', 1)
            return svg
    except Exception:
        pass
    finally:
        os.unlink(tmp_path)

    return None


# ── visualizations.html ───────────────────────────────────────────────────────

_SUMMARY_HEAD = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>visualizations · ggsql + dbt</title>
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
    /* paired cards share a row and split the width 50/50 */
    .pair-row {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
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
    .vis-wrap { padding: 12px 8px 8px; }
    .vis-wrap svg { width: 100%; height: auto; display: block; }
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

_SUMMARY_CARD_SVG = """\
<div class="card">
  <div class="card-title">{name}</div>
  <div class="vis-wrap">{svg}</div>
</div>
"""

# Fallback card used when vl2svg is unavailable
_SUMMARY_CARD_FALLBACK = """\
<div class="card">
  <div class="card-title">{name}</div>
  <div class="vis-wrap" style="padding:1em;color:#64748b;font-size:.8rem;">
    chart not rendered — install vl2svg: npm install -g vega-cli
  </div>
</div>
"""

_SUMMARY_PAIR_OPEN = '<div class="pair-row">\n'
_SUMMARY_PAIR_CLOSE = '</div>\n'

_SUMMARY_TAIL = """\
</div>
<footer>built by dbt-ggsql · charts pre-rendered with vega-lite</footer>
</body>
</html>
"""


def _chart_prefix(name: str) -> str:
    """Return the shared prefix for pairing — everything before the last '_'."""
    parts = name.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else name


def _group_charts(results: list[ChartResult]) -> list[list[ChartResult]]:
    """
    Group consecutive charts that share a prefix into pairs.
    A group of exactly 2 with the same prefix renders as a side-by-side pair.
    Everything else renders as single cards.
    """
    groups: list[list[ChartResult]] = []
    i = 0
    while i < len(results):
        r = results[i]
        prefix = _chart_prefix(r.name)
        if (
            i + 1 < len(results)
            and _chart_prefix(results[i + 1].name) == prefix
            and prefix != r.name
        ):
            groups.append([r, results[i + 1]])
            i += 2
        else:
            groups.append([r])
            i += 1
    return groups


def _card_html(r: ChartResult, is_paired: bool) -> str:
    svg = _spec_to_svg(r.vega_spec, is_paired=is_paired)
    if svg:
        return _SUMMARY_CARD_SVG.format(name=r.name, svg=svg)
    return _SUMMARY_CARD_FALLBACK.format(name=r.name)


def write_summary_html(
    results: list[ChartResult],
    project_root: str,
    output_path: str = os.path.join("output", "visualizations.html"),
) -> str:
    """Write a self-contained summary HTML grid with pre-rendered SVG charts."""
    successful = [r for r in results if r.success]
    out_file = Path(project_root) / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    groups = _group_charts(successful)

    parts = [_SUMMARY_HEAD]
    for group in groups:
        if len(group) == 2:
            parts.append(_SUMMARY_PAIR_OPEN)
            for r in group:
                parts.append(_card_html(r, is_paired=True))
            parts.append(_SUMMARY_PAIR_CLOSE)
        else:
            parts.append(_card_html(group[0], is_paired=False))

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
