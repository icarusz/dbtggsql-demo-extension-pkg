"""
runner.py — scans visualizations/ for .ggsql files, executes each through
the ggsql CLI, writes individual HTML charts, and returns specs for summary.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChartResult:
    name: str
    html_path: str
    vega_spec: str
    success: bool
    error: str = ""


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      min-height: 100vh;
      font-family: system-ui, sans-serif;
      padding: 32px 16px;
    }}
    .chart-wrap {{
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 12px #0000001a;
      padding: 24px;
      max-width: 900px;
      width: 100%;
    }}
    .chart-wrap svg {{ width: 100%; height: auto; display: block; }}
  </style>
</head>
<body>
  <div class="chart-wrap">{svg}</div>
</body>
</html>
"""


def _spec_to_svg_individual(vega_spec: str) -> str | None:
    """Pre-render a Vega-Lite spec to SVG for a standalone chart page."""
    vl2svg_bin = shutil.which("vl2svg")
    if vl2svg_bin is None:
        return None
    try:
        spec = json.loads(vega_spec)
    except json.JSONDecodeError:
        return None

    # Set fixed dimensions: use inner spec for facet layouts
    inner = spec.get("spec")
    if inner and isinstance(inner, dict):
        inner["width"] = 700
        inner["height"] = 480
    else:
        spec["width"] = 800
        spec["height"] = 560

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False, encoding="utf-8") as tmp:
        json.dump(spec, tmp)
        tmp_path = tmp.name

    try:
        result = subprocess.run([vl2svg_bin, tmp_path], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            svg = result.stdout.strip()
            # Expand clip rect to full viewBox so right-edge marks aren't hidden
            vb = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', svg)
            if vb:
                svg = re.sub(
                    r'(<clipPath[^>]*>)\s*<rect x="0" y="0" width="[^"]*" height="[^"]*"/>',
                    rf'\1<rect x="0" y="0" width="{vb.group(1)}" height="{vb.group(2)}"/>',
                    svg,
                )
            # Make responsive
            svg = svg.replace(' width="', ' data-orig-width="', 1)
            svg = svg.replace(' height="', ' style="width:100%;height:auto;" height="', 1)
            return svg
    except Exception:
        pass
    finally:
        os.unlink(tmp_path)
    return None


def run_visualizations(
    project_root: str,
    viz_dir: str = "visualizations",
    output_dir: str = os.path.join("output", "charts"),
) -> list[ChartResult]:
    """Run all .ggsql files in viz_dir and write individual HTML charts."""
    ggsql_bin = shutil.which("ggsql")
    if ggsql_bin is None:
        raise RuntimeError("ggsql CLI not found in PATH. Run: cargo install ggsql-cli")

    viz_path = Path(project_root) / viz_dir
    out_path = Path(project_root) / output_dir
    out_path.mkdir(parents=True, exist_ok=True)

    results: list[ChartResult] = []

    for ggsql_file in sorted(viz_path.glob("*.ggsql")):
        name = ggsql_file.stem
        print(f"  rendering {name}...")

        try:
            proc = subprocess.run(
                [ggsql_bin, "run", str(ggsql_file)],
                capture_output=True,
                text=True,
                cwd=project_root,
            )
        except Exception as exc:
            results.append(ChartResult(name=name, html_path="", vega_spec="", success=False, error=str(exc)))
            continue

        if proc.returncode != 0 or not proc.stdout.strip():
            err = proc.stderr.strip() or "no output"
            results.append(ChartResult(name=name, html_path="", vega_spec="", success=False, error=err))
            continue

        spec = proc.stdout.strip()
        svg = _spec_to_svg_individual(spec)
        if svg is None:
            # vl2svg unavailable — fall back to a plain error page
            svg = "<p style='color:#64748b;padding:1em'>vl2svg not found — install with: npm install -g vega-cli</p>"
        html = _HTML_TEMPLATE.format(title=name, svg=svg)
        out_file = out_path / f"{name}.html"
        out_file.write_text(html, encoding="utf-8")

        results.append(ChartResult(name=name, html_path=str(out_file), vega_spec=spec, success=True))

    return results
