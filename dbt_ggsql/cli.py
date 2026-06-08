"""
cli.py — dbt-ggsql command-line interface.

Usage:
  dbt-ggsql build   [--profiles-dir DIR] [--project-dir DIR] [--skip-dbt]
  dbt-ggsql viz     [--project-dir DIR]
  dbt-ggsql report  [--project-dir DIR]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

from .runner import run_visualizations
from .report import write_summary_html, write_qmd


@click.group()
@click.version_option()
def cli():
    """dbt-ggsql: run ggsql visualizations as part of your dbt pipeline."""


@cli.command()
@click.option("--profiles-dir", default=".", show_default=True, help="dbt profiles directory")
@click.option("--project-dir",  default=".", show_default=True, help="dbt project directory")
@click.option("--skip-dbt",     is_flag=True, default=False,    help="skip dbt build, run visualizations only")
@click.option("--viz-dir",      default="visualizations",        help="directory containing .ggsql files")
def build(profiles_dir, project_dir, skip_dbt, viz_dir):
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
        click.echo("▶  generating summary...")
        html_path = write_summary_html(results, project_root)
        qmd_path  = write_qmd(viz_dir, project_root)
        click.echo(f"✓  summary   → {html_path}")
        click.echo(f"✓  quarto    → {qmd_path}")


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
def report(project_dir, viz_dir):
    """Generate visualizations.html summary and visualizations.qmd."""
    project_root = str(Path(project_dir).resolve())
    click.echo("▶  rendering for report...")
    results = run_visualizations(project_root, viz_dir=viz_dir)
    html_path = write_summary_html(results, project_root)
    qmd_path  = write_qmd(viz_dir, project_root)
    click.echo(f"✓  summary → {html_path}")
    click.echo(f"✓  quarto  → {qmd_path}")
