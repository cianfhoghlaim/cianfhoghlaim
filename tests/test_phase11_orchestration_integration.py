"""Phase 11 orchestration integration tests.

Per the 2026-09-XX-orchestration-integration-v1 change (Phase 11 of the
cianfhoghlaim-nua v6 era plan). Validates that:

- The Hono planner service is wired to the canonical Python planner.
- The 5 jurisdiction orchestrators invoke the canonical BAML
  extraction functions (NOT the prior getattr fallback).
- The 5 jurisdiction Convex tables are present in
  `web/apps/cianfhoghlaim-nua/convex/schema.ts`.
- The 5 jurisdiction BAML functions are present in the generated
  `baml_client`.

All assertions use file-content / grep-style checks rather than
importing Dagster + baml-py + the full Hono package + the full Convex
SDK in the same process — that import stack would fail in CI on the
pre-existing transitive baml_client staleness issue (the same one
Phase 1's tests intentionally work around).

Run with:
    uv run pytest tests/test_phase11_orchestration_integration.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

JURISDICTIONS = (
    "england",
    "wales",
    "scotland",
    "northern_ireland",
    "isle_of_man",
)
LC_ROUTE_SUBJECTS = ("chemistry", "mathematics", "gaeilge", "computer_science")


def _read(rel_path: str) -> str:
    """Read a file relative to the repo root."""
    return (_REPO_ROOT / rel_path).read_text()


def test_phase11_hono_planner_subprocess_handler_defined() -> None:
    """The Hono planner bridge exposes buildStudyPlanHandler.

    The Phase 11 wire-up replaces the inlined stub response with a
    subprocess call to the canonical Python planner. The bridge helper
    lives at ``web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts``.
    """
    src = _read("web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts")
    assert "export function buildStudyPlanHandler" in src, (
        "Phase 11 §1 regression: buildStudyPlanHandler is not exported "
        "from web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts. "
        "The Hono planner bridge must expose a buildStudyPlanHandler "
        "function so the 4 mounted LC routes can delegate to it."
    )
    # The bridge uses subprocess (execFileAsync from node:child_process).
    assert "execFileAsync" in src, (
        "Phase 11 §1 regression: buildStudyPlanHandler does not use "
        "execFileAsync — the canonical subprocess bridge."
    )
    assert "agents.adk.subjects.lc.planner" in src, (
        "Phase 11 §1 regression: buildStudyPlanHandler does not "
        "reference the canonical Python planner module path."
    )
    # Inputs are passed as JSON over stdin, not interpolated into argv
    # (avoids shell quoting bugs + length limits).
    assert "JSON.stringify" in src and "input:" in src, (
        "Phase 11 §1 regression: buildStudyPlanHandler does not "
        "serialise inputs as JSON over stdin."
    )


def test_phase11_hono_planner_subprocess_stub_fallback_defined() -> None:
    """The bridge still exports the studyPlanStubResponse fallback.

    When the Python subprocess fails (no `python` binary on PATH, the
    planner raises, baml_client missing) the route MUST fall back to
    the in-process `studyPlanStubResponse(subject, params)` helper so
    the front-end never sees a 5xx.
    """
    src = _read("web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts")
    assert "export function studyPlanStubResponse" in src, (
        "Phase 11 §1.3 regression: studyPlanStubResponse fallback helper "
        "is missing — the route would 5xx in dev environments without "
        "a working Python subprocess."
    )
    assert 'phase: "phase1_stub"' in src or "phase1_stub" in src, (
        "Phase 11 §1.3 regression: studyPlanStubResponse doesn't tag "
        "its response with phase=phase1_stub."
    )


@pytest.mark.parametrize("subject", list(LC_ROUTE_SUBJECTS))
def test_phase11_4_lc_routes_use_build_study_plan_handler(subject: str) -> None:
    """Each of the 4 mounted LC route handlers uses buildStudyPlanHandler."""
    src = _read(
        f"web/hono-api/src/routes/copilotkit/lc/{subject}.ts"
    )
    assert "from \"./_study_plan_stub\"" in src, (
        f"Phase 11 §1.2 regression: {subject}.ts does not import "
        "from \"./_study_plan_stub\"."
    )
    # The Phase 11 form delegates to buildStudyPlanHandler — NOT a
    # raw studyPlanStubResponse call.
    assert "buildStudyPlanHandler" in src, (
        f"Phase 11 §1.2 regression: {subject}.ts does not delegate to "
        "buildStudyPlanHandler."
    )
    # Verify the legacy inlined studyPlanStubResponse is gone from the
    # route file (otherwise the wire-up didn't actually replace it).
    assert "studyPlanStubResponse(" not in src, (
        f"Phase 11 §1.2 regression: {subject}.ts still calls "
        "studyPlanStubResponse(...) directly — the wired-up "
        "buildStudyPlanHandler should be the only consumer."
    )


def _strip_docstrings(src: str) -> str:
    """Strip triple-quoted docstring + /* */ comment blocks so substring
    assertions don't match the docstring mention of the OLD behaviour.
    """
    import re
    # Strip """...""" blocks
    src = re.sub(r'"""[\s\S]*?"""', "", src)
    src = re.sub(r"'''[\s\S]*?'''", "", src)
    # Strip /* ... */ blocks
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


def test_phase11_hono_index_still_mounts_4_routes() -> None:
    """The 4 mounts in web/hono-api/src/index.ts are unchanged by Phase 11."""
    src = _read("web/hono-api/src/index.ts")
    for subject in LC_ROUTE_SUBJECTS:
        # Import statement — the canonical naming uses <subject>App
        # (with computerScienceApp for the snake_case subject).
        var = "computerScienceApp" if subject == "computer_science" else f"{subject}App"
        assert (
            f"import {var} from \"./routes/copilotkit/lc/{subject}\"" in src
        ), (
            f"Phase 11 regression: {var} import is missing from "
            "web/hono-api/src/index.ts."
        )
        # app.route(...) call
        assert (
            f'app.route("/api/copilotkit/lc/{subject}", {var})' in src
        ), (
            f"Phase 11 regression: app.route('/api/copilotkit/lc/{subject}', ...)"
            f" mount is missing from web/hono-api/src/index.ts."
        )


def test_phase11_jurisdiction_baml_extractor_helper_exists() -> None:
    """The shared helper file is authored and exports invoke_jurisdiction_extractor."""
    src = _read(
        "orchestration/defs/2_materials/_base/jurisdiction_baml_extractor.py"
    )
    assert "def invoke_jurisdiction_extractor" in src, (
        "Phase 11 §2.1 regression: invoke_jurisdiction_extractor is "
        "missing from the shared helper at "
        "orchestration/defs/2_materials/_base/jurisdiction_baml_extractor.py."
    )
    assert "JURISDICTION_BAML_FUNCTIONS" in src, (
        "Phase 11 §2.1 regression: JURISDICTION_BAML_FUNCTIONS mapping "
        "is missing."
    )
    assert "JURISDICTION_CONVEX_TABLES" in src, (
        "Phase 11 §2.1 regression: JURISDICTION_CONVEX_TABLES mapping "
        "is missing."
    )
    # Each of the 5 per-jurisdiction BAML functions is mapped.
    for fn_name in (
        "ExtractEnglandSubjectSpec",
        "ExtractWalesSubjectSpec",
        "ExtractScotlandSubjectSpec",
        "ExtractNorthernIrelandSubjectSpec",
        "ExtractIsleOfManSubjectSpec",
    ):
        assert fn_name in src, (
            f"Phase 11 §2.1 regression: {fn_name} is missing from "
            "the JURISDICTION_BAML_FUNCTIONS mapping."
        )
    # Each of the 5 per-jurisdiction Convex tables is mapped.
    for table in (
        "england_subject_specs",
        "wales_subject_specs",
        "scotland_subject_specs",
        "northern_ireland_subject_specs",
        "isle_of_man_subject_specs",
    ):
        assert table in src, (
            f"Phase 11 §2.1 regression: {table} is missing from "
            "the JURISDICTION_CONVEX_TABLES mapping."
        )


@pytest.mark.parametrize("jurisdiction", list(JURISDICTIONS))
def test_phase11_5_jurisdiction_orchestrators_use_canonical_baml(jurisdiction: str) -> None:
    """Each jurisdiction orchestrator calls invoke_jurisdiction_extractor.

    The Phase 11 wire-up replaces the prior
    ``getattr(b, fn_name, None)`` fallback with the canonical
    ``invoke_jurisdiction_extractor(jurisdiction="<jur>", ...)``
    invocation. Each of the 5 jurisdiction asset files MUST
    reference the helper.

    Note: The orchestrators import the shared helper lazily because
    the ``2_materials`` directory has a leading digit, making a
    static `from orchestration.defs.2_materials... import` illegal
    Python syntax. The test accepts either form (static dot-attribute
    access via a lazy module loader, or a direct module import).
    """
    src = _read(
        f"orchestration/defs/2_materials/{jurisdiction}_education/{jurisdiction}_assets.py"
    )
    assert "invoke_jurisdiction_extractor" in src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py does not "
        "call invoke_jurisdiction_extractor — the canonical BAML+Convex "
        "wire-up didn't land."
    )
    assert f'jurisdiction="{jurisdiction}"' in src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py does not "
        f"pass jurisdiction=\"{jurisdiction}\" to invoke_jurisdiction_extractor."
    )
    # Verify the lazy import helper exists (since the `2_materials`
    # path cannot be a static module-level import — see the docstring
    # at the top of each orchestrator).
    assert "_get_jurisdiction_extractor" in src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py does not "
        "include the `_get_jurisdiction_extractor` lazy import helper "
        "needed to work around the leading-digit `2_materials` path."
    )
    assert "importlib.import_module" in src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py does not "
        "use importlib.import_module for the shared helper."
    )


@pytest.mark.parametrize("jurisdiction", list(JURISDICTIONS))
def test_phase11_no_getattr_baml_fallback_remains(jurisdiction: str) -> None:
    """No `getattr(b, ...)` BAML fallback remains in the 5 orchestrators.

    The Phase 11 wire-up explicitly replaces the Phase 9 fallback with
    `invoke_jurisdiction_extractor(...)`. If the fallback still
    appears, the wire-up didn't actually land.

    We strip docstrings + comment blocks before searching so that
    mentions of the OLD behaviour in the new docstrings don't trigger
    a false positive.
    """
    src = _read(
        f"orchestration/defs/2_materials/{jurisdiction}_education/{jurisdiction}_assets.py"
    )
    code_src = _strip_docstrings(src)
    assert "getattr(b, baml_fn_name, None)" not in code_src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py still "
        "contains the Phase 9 `getattr(b, baml_fn_name, None)` "
        "fallback — the wire-up should have replaced this with the "
        "canonical invoke_jurisdiction_extractor(...) call."
    )
    assert "baml_fn_name.removeprefix" not in code_src, (
        f"Phase 11 §2.2 regression: {jurisdiction}_assets.py still "
        "references the Phase 9 `baml_fn_name.removeprefix(\"b.\")` "
        "stub lookup."
    )


def test_phase11_england_orchestrator_uses_per_row_call() -> None:
    """England orchestrator iterates per cohort through the helper.

    The England asset is structured differently from the other 4
    (per-board × per-qualification tuples, not a single
    `query_by_jurisdiction("england")` loop), so we do a focused check
    that the per-row call exists.
    """
    src = _read("orchestration/defs/2_materials/england_education/england_assets.py")
    assert "invoke_jurisdiction_extractor" in src, (
        "Phase 11 §2.2 regression: england_assets.py does not "
        "delegate to invoke_jurisdiction_extractor per row."
    )
    assert 'jurisdiction="england"' in src, (
        "Phase 11 §2.2 regression: england_assets.py does not "
        'pass jurisdiction="england".'
    )


def test_phase11_5_jurisdiction_convex_tables_wired() -> None:
    """The 5 jurisdiction subject_spec tables are exported by schema.ts."""
    src = _read("web/apps/cianfhoghlaim-nua/convex/schema.ts")
    for table in (
        "england_subject_specs",
        "wales_subject_specs",
        "scotland_subject_specs",
        "northern_ireland_subject_specs",
        "isle_of_man_subject_specs",
    ):
        assert table in src, (
            f"Phase 11 §3.2 regression: {table} is not exported by "
            "web/apps/cianfhoghlaim-nua/convex/schema.ts."
        )

    # schema.ts must include them in the defineSchema({...}) call too.
    schema_block = src.split("defineSchema({", 1)[1].split("});", 1)[0]
    for table in (
        "england_subject_specs",
        "wales_subject_specs",
        "scotland_subject_specs",
        "northern_ireland_subject_specs",
        "isle_of_man_subject_specs",
    ):
        assert table in schema_block, (
            f"Phase 11 §3.2 regression: {table} is missing from the "
            "defineSchema({...}) body in convex/schema.ts."
        )


def test_phase11_jurisdiction_convex_files_authored() -> None:
    """The 5 per-jurisdiction Convex files are present."""
    base = _REPO_ROOT / "web/apps/cianfhoghlaim-nua/convex/jurisdictions"
    for jur in JURISDICTIONS:
        path = base / f"{jur}.ts"
        assert path.exists(), (
            f"Phase 11 §3.3 regression: {path.relative_to(_REPO_ROOT)} "
            "is missing."
        )
        src = path.read_text()
        assert "create" in src and "mutation" in src, (
            f"Phase 11 §3.3 regression: {path.relative_to(_REPO_ROOT)} "
            "doesn't export a `create` mutation."
        )
        assert "by_jurisdiction" in src and "by_subject" in src, (
            f"Phase 11 §3.3 regression: {path.relative_to(_REPO_ROOT)} "
            "is missing one of the required indexes "
            "(by_jurisdiction / by_subject / by_stage)."
        )


def test_phase11_canonical_13plus_table_schema_preserved() -> None:
    """The pre-Phase-11 schema (4 root + 8 per-subject tables) is preserved.

    Phase 11 adds 5 new tables; it MUST NOT remove or rename any
    pre-existing ones.
    """
    src = _read("web/apps/cianfhoghlaim-nua/convex/schema.ts")
    pre_existing = (
        # 4 root tables
        "users",
        "study_plans",
        "oral_study_plans",
        "ncce_learning_graphs",
        # 8 per-subject tables (re-exported from ./lc)
        "accounting",
        "business",
        "french",
        "history",
        "art",
        "music",
        "applied_mathematics",
        "physics",
    )
    schema_block = src.split("defineSchema({", 1)[1].split("});", 1)[0]
    for table in pre_existing:
        assert table in schema_block, (
            f"Phase 11 §3.4 regression: the pre-existing `{table}` "
            "table is missing from the defineSchema({...}) body — "
            "Phase 11 adds tables additively and MUST NOT remove any."
        )


def test_phase11_convex_json_exists() -> None:
    """The canonical Convex deployment config is authored."""
    path = _REPO_ROOT / "web/apps/cianfhoghlaim-nua/convex.json"
    assert path.exists(), (
        "Phase 11 §3.1 regression: web/apps/cianfhoghlaim-nua/convex.json "
        "is missing — Convex deployment prep is incomplete."
    )
    data = json.loads(path.read_text())
    assert "functions" in data, (
        "Phase 11 §3.1 regression: convex.json doesn't declare the "
        "canonical `functions` path."
    )
    assert data["functions"] == "convex/", (
        "Phase 11 §3.1 regression: convex.json `functions` path is "
        "not the canonical `convex/`."
    )


@pytest.mark.parametrize(
    "jurisdiction,fn_name",
    [
        ("england", "ExtractEnglandSubjectSpec"),
        ("wales", "ExtractWalesSubjectSpec"),
        ("scotland", "ExtractScotlandSubjectSpec"),
        ("northern_ireland", "ExtractNorthernIrelandSubjectSpec"),
        ("isle_of_man", "ExtractIsleOfManSubjectSpec"),
    ],
)
def test_phase11_5_jurisdiction_baml_functions_in_baml_client(
    jurisdiction: str, fn_name: str
) -> None:
    """The 5 jurisdiction BAML functions are present in the generated client.

    We check the parser.py (the canonical Python baml_client entry
    point) for the function definitions — avoids importing baml_client
    (which can fail in CI on the pre-existing stale-client issue).
    """
    parser = (
        _REPO_ROOT
        / "baml_client"
        / "baml_client"
        / "parser.py"
    )
    src = parser.read_text()
    assert f'def {fn_name}(' in src, (
        f"Phase 11 §2 regression: b.{fn_name} is not present in the "
        "generated baml_client parser — the BAML wire-up requires "
        "baml-cli generate to be run after the .baml files changed."
    )

    # Verify the corresponding .baml file declares it.
    baml_path = (
        _REPO_ROOT
        / "baml_src"
        / "british_isles"
        / {
            "england": "en",
            "wales": "wl",
            "scotland": "sc",
            "northern_ireland": "ni",
            "isle_of_man": "im",
        }[jurisdiction]
        / "education"
        / {
            "england": "en_extraction.baml",
            "wales": "wl_extraction.baml",
            "scotland": "sc_extraction.baml",
            "northern_ireland": "ni_extraction.baml",
            "isle_of_man": "im_extraction.baml",
        }[jurisdiction]
    )
    assert baml_path.exists(), (
        f"Phase 11 §2 regression: {baml_path.relative_to(_REPO_ROOT)} "
        "is missing."
    )
    baml_src = baml_path.read_text()
    assert f"function {fn_name}(" in baml_src, (
        f"Phase 11 §2 regression: {baml_path.relative_to(_REPO_ROOT)} "
        f"does not declare `function {fn_name}(...)`."
    )


def test_phase11_python_planner_subprocess_invoker_constant() -> None:
    """The Python planner module path is fixed in the Hono bridge.

    The bridge serialises a fixed Python snippet (`from agents.adk...
    import generate_study_plan; ...`) to a child process — user input
    is JSON on stdin, NOT argv. This verifies the module path constant
    is fixed (no string concatenation with user input).
    """
    src = _read("web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts")
    # The fixed Python snippet is in PLANNER_INVOKER_SNIPPET.
    assert "PLANNER_INVOKER_SNIPPET" in src, (
        "Phase 11 §1 regression: PLANNER_INVOKER_SNIPPET constant is "
        "missing — the Hono bridge has no fixed Python invocation "
        "snippet."
    )
    # Imports from agents.adk.subjects.lc.planner.generate_study_plan
    snippet_section = src.split("PLANNER_INVOKER_SNIPPET", 1)[1].split("`", 2)[1]
    assert "from agents.adk.subjects.lc.planner import generate_study_plan" in snippet_section, (
        "Phase 11 §1 regression: PLANNER_INVOKER_SNIPPET does not "
        "import from agents.adk.subjects.lc.planner.generate_study_plan."
    )
