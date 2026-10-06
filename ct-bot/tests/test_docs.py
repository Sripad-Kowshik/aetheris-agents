"""T0 existence checks for the ct-bot docs skeleton.

Dormant until T1 (`pytestmark` below): the use case is registered but has no
agent file, so these checks ride the deferred set rather than the gate. They
still collect and still import, per the `dormant` marker's contract.
"""

from pathlib import Path

import pytest

CT_BOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.dormant


def test_milestone_exists():
    assert (CT_BOT / "milestone.md").is_file()


def test_readme_exists():
    assert (CT_BOT / "README.md").is_file()


def test_agent_source_index_exists():
    """`docs/agents/README.md` indexes the six operator-supplied source filenames."""
    assert (CT_BOT / "docs" / "agents" / "README.md").is_file()
