"""T0/T1 existence checks for the ct-rpg docs skeleton.

The use case is active from T1: rpg-main.exs (the parent) and
rpg-preflight.exs (gate 0) landed together, so these checks gate.
They assert the docs surfaces every later ticket edits against.
"""

from pathlib import Path

CT_RPG = Path(__file__).resolve().parent.parent


def test_milestone_exists():
    assert (CT_RPG / "milestone.md").is_file()


def test_readme_exists():
    assert (CT_RPG / "README.md").is_file()


def test_runbook_exists():
    assert (CT_RPG / "runbook.md").is_file()


def test_tools_manifest_exists():
    assert (CT_RPG / "tools.json").is_file()


def test_parent_and_first_child_wraps_exist():
    """T1 lands the parent and the first child; the rest are T3-T5."""
    agents = CT_RPG / "agents"
    assert (agents / "rpg-main.exs").is_file()
    assert (agents / "rpg-preflight.exs").is_file()


def test_specs_are_present():
    """The extracted specs are the source of truth the wraps copy from."""
    specs = CT_RPG / "docs" / "specs"
    for name in (
        "runbook-gates.md",
        "etl-orchestrator.md",
        "etl-module-students.md",
        "parity-verifier.md",
        "api-verification.md",
    ):
        assert (specs / name).is_file(), name
