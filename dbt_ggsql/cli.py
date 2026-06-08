"""
cli.py — dbt-ggsql command-line interface.

Usage:
  dbt-ggsql build   [--profiles-dir DIR] [--project-dir DIR] [--output html|qmd|both]
  dbt-ggsql viz     [--project-dir DIR]
  dbt-ggsql report  [--project-dir DIR] [--output html|qmd|both]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

from .runner import run_visualizations
from .report import write_summary_html, write_qmd


OUTPUT_HELP = (
    "Output format for the report.  "
    "'html' writes a self-contained visualizations.html with pre-rendered SVG charts.  "
    "'qmd' writes a Quarto document with live ggsql cells and SQL visible via code-fold.  "
    "'both' produces both."
)


def _emit_reports(results, viz_dir, project_root, output):
    """Write the requested output format(s) and echo what was produced."""
    if output in ("html", "both"):
        html_path = write_summary_html(results, project_root)
        click.echo(f"✓  html    → {html_path}")
    if output in ("qmd", "both"):
        qmd_path = write_qmd(viz_dir, project_root)
        click.echo(f"✓  quarto  → {qmd_path}")


@click.group()
@click.version_option()
def cli():
    """dbt-ggsql: run ggsql visualizations as part of your dbt pipeline."""


@cli.command()
@click.option("--profiles-dir", default=".", show_default=True, help="dbt profiles directory")
@click.option("--project-dir",  default=".", show_default=True, help="dbt project directory")
@click.option("--skip-dbt",     is_flag=True, default=False,    help="skip dbt build, run visualizations only")
@click.option("--viz-dir",      default="visualizations",        help="directory containing .ggsql files")
@click.option("--output",       default="html", show_default=True,
              type=click.Choice(["html", "qmd", "both"], case_sensitive=False),
              help=OUTPUT_HELP)
def build(profiles_dir, project_dir, skip_dbt, viz_dir, output):
    """Run dbt build, then render all .ggsql visualizations."""
    project_root = str(Path(project_dir).resolve())

    if not skip_dbt:
        click.echo("▶  running dbt build...")
        result = subprocess.run(
            ["uv", "run", "dbt", "build",
             "--profiles-dir", ".",
             "--project-dir",  "."],
            cwd=project_root,
        )
        if result.returncode != 0:
            click.echo("✗  dbt build failed", err=True)
            sys.exit(result.returncode)
        click.echo("✓  dbt build complete")

    click.echo("▶  rendering visualizations...")
    results = run_visualizations(project_root, viz_dir=viz_dir)

    ok  = [r for r in results if r.success]
    err = [r for r in results if not r.success]

    for r in err:
        click.echo(f"  ✗  {r.name}: {r.error}", err=True)

    click.echo(f"✓  {len(ok)} charts → output/charts/")

    if ok:
        click.echo("▶  generating report...")
        _emit_reports(results, viz_dir, project_root, output)


@cli.command()
@click.option("--project-dir", default=".", show_default=True)
@click.option("--viz-dir",     default="visualizations")
def viz(project_dir, viz_dir):
    """Render .ggsql files to HTML charts (skip dbt build)."""
    project_root = str(Path(project_dir).resolve())
    click.echo("▶  rendering visualizations...")
    results = run_visualizations(project_root, viz_dir=viz_dir)
    ok = [r for r in results if r.success]
    click.echo(f"✓  {len(ok)} charts → output/charts/")


@cli.command()
@click.option("--project-dir", default=".", show_default=True)
@click.option("--viz-dir",     default="visualizations")
@click.option("--output",      default="html", show_default=True,
              type=click.Choice(["html", "qmd", "both"], case_sensitive=False),
              help=OUTPUT_HELP)
def report(project_dir, viz_dir, output):
    """Re-render visualizations and generate the requested output format."""
    project_root = str(Path(project_dir).resolve())
    click.echo("▶  rendering visualizations...")
    results = run_visualizations(project_root, viz_dir=viz_dir)
    ok = [r for r in results if r.success]
    click.echo(f"✓  {len(ok)} charts rendered")
    click.echo("▶  generating report...")
    _emit_reports(results, viz_dir, project_root, output)
