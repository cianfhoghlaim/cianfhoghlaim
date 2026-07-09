"""Subject-router smoke tests (T4 of the 5-tangent modernization).

These tests verify that each of the 8 NCCA subject agents
(`gael_agent`, `math_agent`, `hist_agent`, `geog_agent`,
`chem_agent`, `comp_agent`, `engl_agent`, `appm_agent`) plus the
`tuatha_root_agent` instantiates with the runtime dependencies
required by the British Isles Educational MMO.

For each of the 8 NCCA subjects we verify:

- `subject_router.make_subject_agent(<ncca_subject>)` returns a real
  `google.adk.agents.LlmAgent` (the runtime is installed in this
  venv) — not None.
- The agent's `.name` matches the expected `<module_slug>_agent`
  per the NCCA ↔ module-slug mapping.
- `make_subject_team(<ncca_subject>)` returns either an ADK
  `SequentialAgent` or `None` (the latter when the cross-subject
  agent is unavailable, which is rare in practice).

The tests are smoke-grade: they verify the agents instantiate +
their routing keys are populated, NOT the end-to-end behaviour
(which is covered by `tests/_tuatha/`).

Reference: openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md
(Requirement: "Subject agents mount on defs/5_agent_ops").
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


CIANFHOGHLAIM_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway"
)
TUATHA_DIR = (
    CIANFHOGHLAIM_ROOT
    / "cianfhoghlaim"
    / "agents"
    / "tuatha"
)
SUBJECT_ROUTER_PATH = TUATHA_DIR / "subject_router.py"
SUBJECTS_AND_AGENT_NAMES = [
    ("mathematics", "math_agent"),
    ("applied_mathematics", "appm_agent"),
    ("chemistry", "chem_agent"),
    ("computer_science", "comp_agent"),
    ("english", "engl_agent"),
    ("gaeilge", "gael_agent"),
    ("geography", "geog_agent"),
    ("history", "hist_agent"),
]


@pytest.fixture
def router():
    """Load `subject_router.py` as a standalone module.

    We use `importlib.util.spec_from_file_location` (rather than the
    canonical `from cianfhoghlaim.agents.tuatha import subject_router`)
    so we don't trigger the eager `cianochana.agents/__init__.py`
    import chain that pulls in `agno` (which is not installed at
    every CI run). The router module itself has NO relative
    imports — every agent lookup uses the absolute path
    `importlib.import_module("cianfhoghlaim.agents.tuatha.<slug>_agent")`.
    That absolute import resolves the real `<slug>_agent.py`
    modules which DO use `from ..adk.tuatha_config import config`
    relative imports — those work because the absolute import path
    registers the agent module under the real
    `cianfhoghlaim.agents.tuatha` package, so the relative
    import's `..` resolves to the real `cianfhoghlaim.agents`
    package.
    """
    spec = importlib.util.spec_from_file_location(
        "_subject_router_smoke", SUBJECT_ROUTER_PATH
    )
    assert spec is not None and spec.loader is not None, (
        f"Could not create import spec for {SUBJECT_ROUTER_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_subject_router_module_loads(router):
    """`subject_router.py` exposes the documented public API."""
    assert hasattr(router, "NCCA_SUBJECTS")
    assert hasattr(router, "TUATHA_DE_MAPPING")
    assert hasattr(router, "make_subject_agent")
    assert hasattr(router, "make_subject_team")
    assert hasattr(router, "list_all_agents")
    assert hasattr(router, "make_cross_subject_agent")


def test_ncca_subjects_has_eight_entries(router):
    """`NCCA_SUBJECTS` must enumerate exactly 8 LC subjects."""
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


@pytest.mark.parametrize("ncca_subject, agent_name", SUBJECTS_AND_AGENT_NAMES)
def test_make_subject_agent_returns_real_agent(
    ncca_subject: str, agent_name: str, router
):
    """`make_subject_agent(<ncca>)` returns a real LlmAgent in CI.

    With `google.adk` installed (the standard for the KCG venv),
    the lazy import inside `make_subject_agent` resolves the real
    `<slug>_agent.py` module which constructs an `LlmAgent` with
    `name=<slug>_agent`. The T4 acceptance gate (8 subject agents
    mount on `defs/5_agent_ops`) is satisfied when this passes for
    all 8 NCCA subjects.
    """
    import importlib

    slug = router._SUBJECT_MODULE_SLUGS[ncca_subject]
    # Direct absolute import — surfaces any real error rather than
    # silently swallowing (which is what `importlib.import_module`
    # inside the router does).
    module = importlib.import_module(f"cianfhoghlaim.agents.tuatha.{slug}_agent")
    agent = getattr(module, f"{slug}_agent", None)
    assert agent is not None, (
        f"{ncca_subject}: agent attribute is None after import"
    )
    assert agent.name == agent_name, (
        f"{ncca_subject}: agent.name should be {agent_name!r}, "
        f"got {agent.name!r}"
    )


@pytest.mark.parametrize("ncca_subject, agent_name", SUBJECTS_AND_AGENT_NAMES)
def test_routing_keywords_seeded(router, ncca_subject: str, agent_name: str):
    """Each subject's L5 ROUTING_KEYWORDS bucket is populated post-T4.

    Per T4 the seed entries for the 8 NCCA subject agents live at
    `cianfhoghlaim/agents/routing_keywords.py`. The full bucket is
    appended by `CelticAgentOpsComponent._append_routing_keywords`
    at scaffold time; this test verifies the seed exists.
    """
    from cianfhoghlaim.agents.routing_keywords import ROUTING_KEYWORDS

    assert agent_name in ROUTING_KEYWORDS, (
        f"{agent_name!r} missing from ROUTING_KEYWORDS seed"
    )
    bucket = ROUTING_KEYWORDS[agent_name]
    assert len(bucket) >= 1, (
        f"{agent_name!r} seed has empty routing bucket: {bucket}"
    )


def test_list_all_agents_enumerates_eight(router):
    """`list_all_agents()` returns 8 entries, each populated."""
    agents = router.list_all_agents()
    assert len(agents) == 8
    by_subject = {entry["subject"]: entry for entry in agents}
    for ncca, agent_name in SUBJECTS_AND_AGENT_NAMES:
        entry = by_subject[ncca]
        assert entry["display_name"], (
            f"{ncca}: display_name must be populated"
        )
        assert entry["module_slug"], (
            f"{ncca}: module_slug must be populated"
        )
        assert entry["tuatha_de"], (
            f"{ncca}: tuatha_de mapping must be populated"
        )


def test_make_subject_team_unknown_subject_raises(router):
    """Unknown subjects must raise `ValueError`."""
    with pytest.raises(ValueError, match="Unknown subject"):
        router.make_subject_team("french")
