"""
runner.py — scans visualizations/ for .ggsql files, executes each through
the ggsql CLI, writes individual HTML charts, and returns specs for summary.
"""

from __future__ import annotations

import os
import shutil
import subprocess
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
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@6"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      font-family: system-ui, sans-serif;
    }}
    #vis {{
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 12px #0000001a;
      padding: 24px;
      width: 860px;
      height: 620px;
    }}
  </style>
</head>
<body>
  <div id="vis"></div>
  <script>
    const spec = {spec};
    spec.width = 800;
    spec.height = 560;
    vegaEmbed('#vis', spec, {{ actions: false, renderer: 'svg' }}).catch(console.error);
  </script>
</body>
</html>
"""


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
        html = _HTML_TEMPLATE.format(title=name, spec=spec)
        out_file = out_path / f"{name}.html"
        out_file.write_text(html, encoding="utf-8")

        results.append(ChartResult(name=name, html_path=str(out_file), vega_spec=spec, success=True))

    return results
