"""T0 existence checks for the ct-bot docs skeleton.

T1 removed the `dormant` marker: the use case is active (main.exs landed),
so these checks gate again. They assert the docs surfaces every later
ticket edits against.
"""

from pathlib import Path

import pytest

CT_BOT = Path(__file__).resolve().parent.parent


def test_milestone_exists():
    assert (CT_BOT / "milestone.md").is_file()


def test_readme_exists():
    assert (CT_BOT / "README.md").is_file()


def test_agent_source_index_exists():
    """`docs/agents/README.md` indexes the six operator-supplied source filenames."""
    assert (CT_BOT / "docs" / "agents" / "README.md").is_file()
