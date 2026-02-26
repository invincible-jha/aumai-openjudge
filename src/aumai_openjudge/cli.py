"""CLI entry point for aumai-openjudge."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """AumAI Openjudge CLI."""


if __name__ == "__main__":
    main()
