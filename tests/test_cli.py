"""Tests for the aumai-openjudge CLI.

LEGAL DISCLAIMER: This test suite is for software testing purposes only.
The legal information does not constitute legal advice.
Consult a qualified legal professional for any legal matters.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from aumai_openjudge.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0


def test_cli_main_group_exists(runner: CliRunner) -> None:
    """The CLI group entry point must be importable and callable."""
    result = runner.invoke(main, [])
    # Exit code 0 (help shown) or 2 (usage error for no subcommand) both indicate the CLI exists
    assert result.exit_code in (0, 1, 2)
