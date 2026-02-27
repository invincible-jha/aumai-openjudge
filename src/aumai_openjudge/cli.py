"""CLI entry point for aumai-openjudge."""

from __future__ import annotations

import sys

import click

from .models import LEGAL_DISCLAIMER

LEGAL_DISCLAIMER_CLI = (
    "This tool does NOT provide legal advice."
    " Case analysis is based on keyword matching and may be incomplete or inaccurate."
    " Always consult a qualified legal professional."
)


@click.group()
@click.version_option()
def main() -> None:
    """AumAI Openjudge CLI."""


@main.command("serve")
@click.option("--port", default=8000, help="Port to serve on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def serve(port: int, host: str) -> None:
    """Start the Openjudge API server."""
    click.echo(f"\nDISCLAIMER: {LEGAL_DISCLAIMER}\n")
    try:
        import uvicorn
    except ImportError:
        click.echo("Error: uvicorn is required. Install with: pip install uvicorn", err=True)
        sys.exit(1)
    uvicorn.run("aumai_openjudge.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
