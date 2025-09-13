"""Typer CLI entrypoint for DiffGuard (skeleton)."""

from __future__ import annotations

import typer

app = typer.Typer(help="DiffGuard CLI - inspect analyses (skeleton)")


@app.command()
def list(limit: int = typer.Option(10, help="Max number of recent analyses")) -> None:  # pragma: no cover - placeholder
    """List recent analyses (placeholder)."""
    typer.echo(f"No analyses yet (skeleton). Limit={limit}")


@app.command()
def show(analysis_id: str) -> None:  # pragma: no cover - placeholder
    """Show a single analysis by id (placeholder)."""
    typer.echo(f"Analysis {analysis_id} not found (skeleton)")


if __name__ == "__main__":  # pragma: no cover - manual execution
    app()
