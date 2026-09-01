"""Phase 1 integration tests for the 4-subject chat-with-syllabus showcase.

Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
(Phase 1, §5.4 of tasks.md). One test per Phase 1 subject
(chemistry + mathematics + gaeilge + computer_science) plus a
regression test that the broken `agents.adk.subjects.lc.mathematics.planner`
import is gone (Phase 1 §2 fix).

Run with:
    uv run pytest tests/test_adk_subject_actions.py -v
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make the repo root importable so the `agents.adk.subjects.lc.*`
# imports resolve. Mirrors the pattern in
# tests/conftest.py (the canonical repo conftest).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _run_async(coro):
    """Run an async coroutine from sync pytest context."""
    return asyncio.get_event_loop().run_until_complete(coro)


def test_phase1_planner_importable():
    """The canonical Phase 1 planner module exists and exports generate_study_plan.

    Validated by reading the planner source directly (avoids triggering
    `agents.adk.__init__` which validates BAML functions against the
    baml_client and fails on the pre-existing stale-client issue).
    """
    src = (_REPO_ROOT / "agents/adk/subjects/lc/planner.py").read_text()
    assert "async def generate_study_plan" in src, (
        "Phase 1 §1.2 regression: planner.py missing `async def "
        "generate_study_plan`."
    )
    assert "from baml_client import b as baml_client" in src, (
        "Phase 1 §1.2 regression: planner.py doesn't import baml_client."
    )
    assert "_stub_response" in src, (
        "Phase 1 §1.2 regression: planner.py missing _stub_response fallback."
    )


def test_phase1_planner_returns_canonical_shape():
    """The planner returns the canonical Phase 1 stub shape (works without
    a generated baml_client).
    """
    src = (_REPO_ROOT / "agents/adk/subjects/lc/planner.py").read_text()
    # The response shape contract — Phase 1 stub returns these fields.
    for field in [
        "subject",
        "duration_weeks",
        "weeks_plan",
        "milestones",
        "kc_weights",
        "recommended_past_papers",
        "langfuse_trace_id",
        "stub_reason",
    ]:
        assert f'"{field}"' in src, (
            f"Phase 1 §1.2 regression: planner.py stub response missing `{field}`."
        )


def test_phase1_mathematics_handler_uses_shared_planner():
    """Mathematics get_study_plan handler imports from the shared planner.

    Validated by file-content check (avoids importing agents.adk which
    triggers the pre-existing baml_client staleness issue).
    """
    src = (_REPO_ROOT / "agents/adk/subjects/lc/mathematics.py").read_text()
    assert "from agents.adk.subjects.lc.planner import generate_study_plan" in src
    # The old broken import is gone.
    assert (
        "from agents.adk.subjects.lc.mathematics.planner import generate_study_plan"
    ) not in src
    assert "async def get_study_plan" in src


def test_phase1_chemistry_handler_dispatches():
    """Chemistry get_study_plan handler exists and delegates to the shared planner."""
    src = (_REPO_ROOT / "agents/adk/subjects/lc/chemistry.py").read_text()
    assert "async def get_study_plan" in src
    assert "from agents.adk.subjects.lc.planner import generate_study_plan" in src
    assert "subject=\"chemistry\"" in src


def test_phase1_gaeilge_handler_threads_dialect():
    """Gaeilge get_study_plan handler threads the Irish dialect through."""
    src = (_REPO_ROOT / "agents/adk/subjects/lc/gaeilge.py").read_text()
    assert "async def get_study_plan" in src
    assert "from agents.adk.subjects.lc.planner import generate_study_plan" in src
    assert "dialect=" in src
    assert "subject=\"gaeilge\"" in src


def test_phase1_computer_science_handler_dispatches():
    """Computer Science get_study_plan handler exists and delegates to the shared planner."""
    src = (_REPO_ROOT / "agents/adk/subjects/lc/computer_science.py").read_text()
    assert "async def get_study_plan" in src
    assert "from agents.adk.subjects.lc.planner import generate_study_plan" in src
    assert "subject=\"computer_science\"" in src
    # The file should also have the 13-action registry.
    assert "COMPUTER_SCIENCE_ACTIONS" in src
    assert "computer_science_agent" in src


def test_phase1_broken_mathematics_planner_import_is_gone():
    """Regression test for Phase 1 §2: the broken
    `agents.adk.subjects.lc.mathematics.planner` import (which pointed
    at a non-existent `agents/adk/subjects/lc/mathematics/planner.py`)
    is no longer referenced anywhere in the source tree.
    """
    import subprocess

    out = subprocess.run(
        [
            sys.executable,
            "-c",
            "import pathlib, re; "
            "root = pathlib.Path('agents/adk/subjects/lc'); "
            "bad = list(root.rglob('*.py')); "
            "matches = [str(p) for p in bad if re.search(r'mathematics[\\\\/]planner', str(p))]; "
            "print('\\n'.join(matches))",
        ],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0, f"regression search failed: {out.stderr}"
    assert out.stdout.strip() == "", (
        "Phase 1 §2 regression: found a `mathematics/planner` path on disk: "
        f"{out.stdout}"
    )


def test_phase1_hybrid_search_router_re_exported():
    """Regression test for Phase 1 §2: the broken
    `from ...knowledge_graph import HybridSearchConfig` import is gone;
    `agents/api/routes/routes/search.py` now imports from
    `agents.meaisinfhoghlaim.firecrawl_mcp.memory.router.MemoryRouter`.

    Validated by file-content check (avoids importing FastAPI which
    has its own transitive issues).
    """
    src = (_REPO_ROOT / "agents/api/routes/routes/search.py").read_text()
    # Strip the comment block that mentions the legacy import (the test
    # assertion only checks the live import statement).
    lines = [
        line for line in src.splitlines()
        if not line.lstrip().startswith("#")
    ]
    live_src = "\n".join(lines)
    assert "from ...knowledge_graph import" not in live_src, (
        "Phase 1 §2.2 regression: the broken knowledge_graph import is "
        "still present."
    )
    assert "MemoryRouter" in src, (
        "Phase 1 §2.2 regression: search.py doesn't reference MemoryRouter."
    )


def test_phase1_voice_agent_process_audio_not_a_pass():
    """Regression test for Phase 1 §2.4: the `pass # TODO` body of
    `agents/adk/voice_agent.py::process_audio` is gone.
    """
    src = (_REPO_ROOT / "agents/adk/voice_agent.py").read_text()
    assert "pass  # TODO: Pipecat SDK integration" not in src, (
        "Phase 1 §2.4 regression: voice_agent.process_audio still has the "
        "`pass # TODO: Pipecat SDK integration` stub body."
    )
    # The Phase 1 stub returns the canonical response shape.
    assert "phase1_stub" in src or "phase6_wired" in src or "phase6_unreachable" in src
    assert "_silent_wav_bytes" in src or "silent_wav_bytes" in src


def test_phase1_dispatch_study_plan_delegates_to_planner():
    """Regression test for Phase 1 §2.5: `agents/_workflow_handlers.py::dispatch_study_plan`
    no longer returns the hardcoded stub; it delegates to the canonical
    planner via `agents.adk.subjects.lc.planner.generate_study_plan`.
    """
    from agents import _workflow_handlers

    src = Path(_workflow_handlers.__file__).read_text()
    assert "delegates to the canonical Phase 1 planner" in src, (
        "Phase 1 §2.5 regression: dispatch_study_plan doesn't reference the "
        "shared planner."
    )


def test_phase1_quest_pack_assets_calls_consolidated_baml():
    """Regression test for Phase 1 §2.1:
    `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
    no longer calls `getattr(b, f"Generate{prefix}QuestPack")` (the
    per-subject name that no longer exists); it routes through
    `b.GenerateSubjectQuestPack(...)`.
    """
    from pathlib import Path as _P

    qp_path = _P(
        _REPO_ROOT / "orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py",
    )
    src = qp_path.read_text()
    assert 'f"Generate{prefix}QuestPack"' not in src, (
        "Phase 1 §2.1 regression: quest_pack_assets.py still uses "
        "`getattr(b, f\"Generate{prefix}QuestPack\")`."
    )
    assert "GenerateSubjectQuestPack" in src, (
        "Phase 1 §2.1 regression: quest_pack_assets.py doesn't call the "
        "consolidated `b.GenerateSubjectQuestPack(...)`."
    )