"""Tests for `cianfhoghlaim.agents.tuatha.subject_router`.

Verifies the lazy-import contract that `subject_router.py` exposes.
The router must **never** raise at import time, even when
`google.adk`, `langfuse`, `letta`, `baml_client`, etc. are missing
from the venv — that is the whole reason the underlying agent
modules are lazy-imported.

For each of the 8 NCCA subjects we verify:
  - `make_subject_agent(subject)` returns **either** a real
    `google.adk.agents.LlmAgent` (when the runtime is installed)
    **or** `None` (when the runtime is unavailable). It must never
    raise.
  - The Tuatha Dé deity in `TUATHA_DE_MAPPING` is mapped correctly.
  - `list_all_agents()` enumerates exactly 8 entries with the
    expected Brown Ajah ↔ Tuatha Dé mapping.

The tests also exercise `make_subject_team` (returns an ADK
`SequentialAgent` or `None`) and `make_cross_subject_agent`.

NB: this test loads `subject_router.py` via `importlib.util`
(`spec_from_file_location`), **not** via `from cianfhoghlaim.agents
.tuatha.subject_router import …`. Going through the `cianochana
.agents` package would trigger `cianochana/agents/__init__.py`
which eagerly imports `.agno`, and the test environment lacks a
compatible `agno` version at import time. The router's lazy-import
contract means we don't need to bring up the parent package —
loading the module file is sufficient.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


CIANFHOGHLAIM_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway"
)
SUBJECT_ROUTER_PATH = (
    CIANFHOGHLAIM_ROOT
    / "cianfhoghlaim"
    / "agents"
    / "tuatha"
    / "subject_router.py"
)


@pytest.fixture
def router():
    """Load `subject_router.py` as a standalone module.

    Returns a fresh module object each test so import-caches are
    cleared (the module has no internal state but the import
    contract is the thing under test).
    """
    spec = importlib.util.spec_from_file_location(
        "_subject_router_under_test", SUBJECT_ROUTER_PATH
    )
    assert spec is not None and spec.loader is not None, (
        f"Could not create import spec for {SUBJECT_ROUTER_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    # Mark it as a package-attribute-less standalone so `from .x` fails
    # cleanly if anything tries it, but absolute imports inside
    # `make_subject_agent` continue to resolve.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


SUBJECTS_AND_DEITIES = [
    ("mathematics", "The Dagda"),
    ("applied_mathematics", "Lugh"),
    ("chemistry", "Dian Cecht"),
    ("computer_science", "—"),
    ("english", "Brigid"),
    ("gaeilge", "Ogma"),
    ("geography", "Manannán mac Lir"),
    ("history", "The Morrígan"),
]


def test_router_imports_cleanly(router):
    """`subject_router.py` must import cleanly even without `google.adk`.

    Asserts the module exposes the documented public API surface
    — `NCCA_SUBJECTS`, `TUATHA_DE_MAPPING`, `make_subject_agent`,
    `make_subject_team`, `list_all_agents`, `make_cross_subject_agent`.
    """
    assert hasattr(router, "NCCA_SUBJECTS")
    assert hasattr(router, "TUATHA_DE_MAPPING")
    assert hasattr(router, "make_subject_agent")
    assert hasattr(router, "make_subject_team")
    assert hasattr(router, "list_all_agents")
    assert hasattr(router, "make_cross_subject_agent")


def test_ncca_subjects_has_eight_entries(router):
    """`NCCA_SUBJECTS` must enumerate exactly 8 Leaving Certificate subjects."""
    assert len(router.NCCA_SUBJECTS) == 8
    assert set(router.NCCA_SUBJECTS) == {
        "mathematics",
        "applied_mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "gaeilge",
        "computer_science",
    }


@pytest.mark.parametrize("subject,deity", SUBJECTS_AND_DEITIES)
def test_make_subject_agent_lazy_imports(subject, deity, router):
    """`make_subject_agent(subject)` must lazy-import the 8 real agents.

    Either returns a `google.adk.agents.LlmAgent` instance (when the
    runtime is installed) or `None` (when the runtime is unavailable).
    Must never raise — this is the central contract of the router.
    Also asserts the Brown Ajah ↔ Tuatha Dé mapping is correct.
    """
    agent = router.make_subject_agent(subject)
    if agent is not None:
        assert hasattr(agent, "name"), (
            f"{subject}: returned non-LlmAgent object without a `.name`"
        )
        assert hasattr(agent, "model"), (
            f"{subject}: returned non-LlmAgent object without a `.model`"
        )

    deity_in_mapping, lore = router.TUATHA_DE_MAPPING[subject]
    assert deity_in_mapping == deity, (
        f"{subject}: expected {deity!r}, got {deity_in_mapping!r}"
    )
    assert lore, f"{subject}: lore must be non-empty"


def test_make_subject_agent_unknown_subject_raises(router):
    """Unknown subjects must raise `ValueError`."""
    with pytest.raises(ValueError, match="Unknown subject"):
        router.make_subject_agent("french")


def test_make_subject_team_returns_adk_team_or_none(router):
    """`make_subject_team` returns a `SequentialAgent` or `None`.

    Either returns an ADK composite (with `sub_agents` populated)
    or `None` if the ADK runtime is unavailable or the subject's
    agent could not be loaded. Must never raise.
    """
    team = router.make_subject_team("mathematics")
    if team is not None:
        assert hasattr(team, "sub_agents")
        assert len(team.sub_agents) >= 1, (
            "team must contain at least the subject specialist"
        )


def test_make_subject_team_unknown_subject_raises(router):
    """`make_subject_team` validates subject up front (raises ValueError)."""
    with pytest.raises(ValueError, match="Unknown subject"):
        router.make_subject_team("french")


def test_list_all_agents_enumerates_eight_with_mapping(router):
    """`list_all_agents()` returns 8 entries, each with the Brown Ajah ↔ Tuatha Dé mapping."""
    agents = router.list_all_agents()
    assert len(agents) == 8

    by_subject = {entry["subject"]: entry for entry in agents}
    for subject, expected_deity in SUBJECTS_AND_DEITIES:
        entry = by_subject[subject]
        assert entry["tuatha_de"] == expected_deity, (
            f"{subject}: expected deity {expected_deity!r}, "
            f"got {entry['tuatha_de']!r}"
        )
        assert entry["display_name"], (
            f"{subject}: display_name must be populated"
        )
        assert entry["module_slug"], (
            f"{subject}: module_slug must be populated"
        )
        assert entry["lore"], (
            f"{subject}: lore must be populated"
        )
        # `agent` may be None (runtime unavailable) but must exist as a key
        assert "agent" in entry


def test_make_cross_subject_agent_is_callable(router):
    """`make_cross_subject_agent` either returns the cross-subject
    `LlmAgent` or `None` — never raises."""
    agent = router.make_cross_subject_agent()
    if agent is not None:
        assert hasattr(agent, "name")
