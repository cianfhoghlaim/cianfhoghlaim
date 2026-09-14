"""Smoke test for Phase 16: `buildSubjectActionHandler`.

Per Plan 16-29 recovery. The dispatcher is a TypeScript module
(``web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts``) — it
cannot be imported from Python directly. This test verifies:

  1. The file exists at the canonical path.
  2. It exports the ``buildSubjectActionHandler`` function.
  3. The function has the expected (subject, stage, action,
     durationWeeks, language) signature.
  4. It spawns Python via ``Bun.spawn``.
  5. It calls ``agents/adk/subjects/lc/planner.py``.

Per the safety rules, this test is SAFE to apply — it does not
invoke the dispatcher, just inspects its source.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER_PATH = (
    REPO_ROOT
    / "web" / "hono-api" / "src" / "routes" / "copilotkit" / "lc" / "_study_plan_stub.ts"
)
PLANNER_RELATIVE_PATH = "agents/adk/subjects/lc/planner.py"


def _read_source() -> str:
    assert DISPATCHER_PATH.exists(), (
        f"Phase 16 foundation: dispatcher missing at {DISPATCHER_PATH}. "
        "Was _study_plan_stub.ts reverted?"
    )
    return DISPATCHER_PATH.read_text()


def test_dispatcher_file_exists() -> None:
    """The Phase 16 dispatcher exists at the canonical path."""
    assert DISPATCHER_PATH.is_file(), (
        f"Phase 16 foundation: {DISPATCHER_PATH} is not a file"
    )


def test_build_subject_action_handler_exported() -> None:
    """The ``buildSubjectActionHandler`` function is exported."""
    src = _read_source()
    # Match either a top-level export function declaration or a named export
    pattern = (
        r"export\s+function\s+buildSubjectActionHandler\b"
    )
    assert re.search(pattern, src), (
        "Phase 16 foundation: `buildSubjectActionHandler` not declared "
        "as `export function buildSubjectActionHandler(...)`."
    )


def test_build_subject_action_handler_signature() -> None:
    """The function signature includes (subject, stage, action, durationWeeks, language)."""
    src = _read_source()
    pattern = (
        r"export\s+function\s+buildSubjectActionHandler\s*\(\s*"
        r"\s*subject\s*:\s*string\s*,"
        r"\s*stage\s*:\s*string\s*,"
        r"\s*action\s*:\s*string\s*,"
        r"\s*durationWeeks\s*:\s*number\s*,"
        r"\s*language\s*:\s*string\s*,"
    )
    assert re.search(pattern, src, re.MULTILINE | re.DOTALL), (
        "Phase 16 foundation: `buildSubjectActionHandler` signature does "
        "not match (subject, stage, action, durationWeeks, language)."
    )


def test_dispatcher_uses_bun_spawn() -> None:
    """The dispatcher delegates to the Python planner via Bun.spawn."""
    src = _read_source()
    assert "Bun.spawn" in src, (
        "Phase 16 foundation: dispatcher must call `Bun.spawn` to invoke "
        "the Python per-subject agent."
    )
    assert PLANNER_RELATIVE_PATH in src, (
        f"Phase 16 foundation: dispatcher must reference the canonical "
        f"planner at `{PLANNER_RELATIVE_PATH}`."
    )


def test_dispatcher_has_stub_fallback() -> None:
    """The dispatcher falls back to a stub when Python is unavailable."""
    src = _read_source()
    # Look for the canonical stub-mode indicator
    assert "stub" in src.lower(), (
        "Phase 16 foundation: dispatcher must include a stub fallback for "
        "environments where Python or the planner is unavailable."
    )


def test_dispatcher_returns_structured_result() -> None:
    """The handler returns an `ActionHandlerResult`-shaped dict."""
    src = _read_source()
    # The canonical fields every ActionHandlerResult must include.
    for field_name in ("from_python", "subject", "stage", "action", "response"):
        assert field_name in src, (
            f"Phase 16 foundation: ActionHandlerResult missing `{field_name}`"
        )


def test_build_subject_sub_app_exported() -> None:
    """The Phase 17.4 `buildSubjectSubApp` factory is also exported."""
    src = _read_source()
    pattern = r"export\s+function\s+buildSubjectSubApp\b"
    assert re.search(pattern, src), (
        "Phase 17.4 foundation: `buildSubjectSubApp` not declared "
        "as `export function buildSubjectSubApp(...)`."
    )


def test_build_subject_sub_app_signature() -> None:
    """`buildSubjectSubApp(subject, displayName, stage, durationWeeks, language)`."""
    src = _read_source()
    pattern = (
        r"export\s+function\s+buildSubjectSubApp\s*\(\s*"
        r"\s*subject\s*:\s*string\s*,"
        r"\s*displayName\s*:\s*string\s*,"
        r"\s*stage\s*:\s*string\s*,"
        r"\s*durationWeeks\s*:\s*number\s*,"
        r"\s*language\s*:\s*string\s*,"
    )
    assert re.search(pattern, src, re.MULTILINE | re.DOTALL), (
        "Phase 17.4 foundation: `buildSubjectSubApp` signature does not "
        "match (subject, displayName, stage, durationWeeks, language)."
    )


def test_sub_app_has_seven_biep_tabs() -> None:
    """The sub-app exposes the canonical 7-tab BIEP layout."""
    src = _read_source()
    assert "DEFAULT_BIEP_TABS" in src, (
        "Phase 17.4 foundation: DEFAULT_BIEP_TABS not exported."
    )
    # Find the array literal opening: `= [` after `DEFAULT_BIEP_TABS`.
    idx = src.find("DEFAULT_BIEP_TABS")
    list_start_marker = src.find("= [", idx)
    assert list_start_marker != -1, (
        "Phase 17.4 foundation: DEFAULT_BIEP_TABS list `= [` not found "
        "(the type annotation `BiepTabSpec[]` confused the matcher)."
    )
    list_start = list_start_marker + len("= ")
    # Walk from the opening `[` to the matching closing `]`.
    depth = 0
    list_end = -1
    for i in range(list_start, len(src)):
        if src[i] == "[":
            depth += 1
        elif src[i] == "]":
            depth -= 1
            if depth == 0:
                list_end = i
                break
    assert list_end != -1, (
        "Phase 17.4 foundation: DEFAULT_BIEP_TABS list end not found."
    )
    body = src[list_start:list_end]
    tab_count = len(re.findall(r"\{\s*id\s*:", body))
    assert tab_count == 7, (
        f"Phase 17.4 foundation: expected 7 BIEP tabs, found {tab_count}."
    )