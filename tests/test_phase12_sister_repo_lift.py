"""Phase 12 sister-repo lift tests.

Per the 2026-09-XX-sister-repo-lift-v1 change (Phase 12 of the
cianfhoghlaim-nua v6 era plan). Validates that:

- All 6 lift-patch files exist in ``openspec/sister-lifts/``
- All 22 referenced source files in cianfhoghlaim exist
- Each lift-patch has a per-PR checklist with at least 3 items
- The customisation matrix in the proposal mentions all 6
  sisters

The Phase 12 deliverable is the lift-patch planning docs, NOT
the actual code transfer (which happens in per-sister-repo
PRs authored by the sister repo maintainers). These tests
therefore check the lift-patch structure (existence + content
shape + source-file references), not the lifted code.

Run with:
    uv run pytest tests/test_phase12_sister_repo_lift.py -v
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# The 6 sister repos + their lift-patch filenames.
LIFT_PATCHES = (
    ("bonneagar", "bonneagar-iac-gcp-mirror-lift-v1.md"),
    ("tuatha", "tuatha-adk-pipecat-lift-v1.md"),
    ("ciancheiltis", "ciancheiltis-celtic-baml-lift-v1.md"),
    ("ciandlithe", "ciandlithe-legal-baml-lift-v1.md"),
    ("cianchosaint", "cianchosaint-defence-baml-lift-v1.md"),
    ("gemini_hackathon", "gemini-hackathon-oss-substrate-lift-v1.md"),
)

# All 22 source files referenced across the 6 lift patches (relative
# to the cianfhoghlaim repo root).
SOURCE_FILES = (
    # bonneagar (B.1 + B.3 + B.4; B.2 is already in bonneagar; B.5 stays behind)
    "baml_src/british_isles/_shared/study_plan.baml",
    "web/packages/db/convex/schema.ts",
    "meaisinfhoghlaim/certificate/pipeline.py",
    # tuatha (T.1-T.5)
    "agents/adk/voice_agent.py",
    "agents/api/_oideachais_api/services/pipecat_client.py",
    "agents/api/_oideachais_api/services/tts_router.py",
    "agents/adk/subjects/lc/planner.py",
    "agents/adk/subjects/lc/chemistry.py",
    # ciancheiltis (C.1-C.5)
    "baml_src/celtic/sources.baml",
    "baml_src/british_isles/_cross/vernacular_languages.baml",
    "baml_src/celtic/morphology.baml",
    "baml_src/celtic/grammar_patterns.baml",
    "baml_src/celtic/gaois/duchas.baml",
    # ciandlithe (L.1-L.5)
    "baml_src/british_isles/ireland/education/law/courts.baml",
    "baml_src/british_isles/ireland/education/law/judgements.baml",
    "baml_src/british_isles/ireland/education/law/shared_legal_enums.baml",
    "baml_src/british_isles/ireland/education/law/piab.baml",
    "baml_src/british_isles/ireland/education/law/court_rules.baml",
    # cianchosaint (D.1-D.5)
    "baml_src/british_isles/ireland/education/law/legal_aid.baml",
    "baml_src/british_isles/ireland/education/_shared/eiraic_treasures.baml",
    "cocoindex_flows/_shared/_docling_grid_segmenter.py",
    # gemini_hackathon (G.1-G.5)
    "baml_src/british_isles/uk_ncce/learning_graph.baml",
    "baml_src/british_isles/uk_ncce/equivalencies.baml",
    "baml_src/british_isles/ireland/education/certification.baml",
    "cocoindex_flows/uk_ncce/learning_graphs_app.py",
)


def _read_lift_patch(sister_key: str, filename: str) -> str:
    """Read a lift-patch file from openspec/sister-lifts/."""
    return (_REPO_ROOT / "openspec" / "sister-lifts" / filename).read_text()


def _read_proposal() -> str:
    """Read the Phase 12 proposal."""
    return (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-XX-sister-repo-lift-v1"
        / "proposal.md"
    ).read_text()


# --- §1: All 6 lift-patch files exist ---------------------------------------


def test_phase12_sister_lifts_directory_exists() -> None:
    """openspec/sister-lifts/ is created and is a directory."""
    path = _REPO_ROOT / "openspec" / "sister-lifts"
    assert path.exists(), (
        "Phase 12 §1 regression: openspec/sister-lifts/ does not exist."
    )
    assert path.is_dir(), (
        "Phase 12 §1 regression: openspec/sister-lifts/ is not a directory."
    )


@pytest.mark.parametrize("sister_key,filename", list(LIFT_PATCHES))
def test_phase12_lift_patch_file_exists(
    sister_key: str, filename: str
) -> None:
    """Each of the 6 lift-patch files exists in openspec/sister-lifts/."""
    path = _REPO_ROOT / "openspec" / "sister-lifts" / filename
    assert path.exists(), (
        f"Phase 12 §1.{LIFT_PATCHES.index((sister_key, filename)) + 1} "
        f"regression: {filename} does not exist in openspec/sister-lifts/."
    )
    # And it has non-trivial content (≥ 2 KB).
    assert path.stat().st_size >= 2048, (
        f"Phase 12 §1.{LIFT_PATCHES.index((sister_key, filename)) + 1} "
        f"regression: {filename} is too small ({path.stat().st_size} bytes); "
        "a lift-patch must include the source/destination/transformation/checklist sections."
    )


# --- §2: All 22 source files in cianfhoghlaim exist ------------------------


@pytest.mark.parametrize("rel_path", list(SOURCE_FILES))
def test_phase12_source_file_exists(rel_path: str) -> None:
    """Each source file referenced in the lift patches exists."""
    path = _REPO_ROOT / rel_path
    assert path.exists(), (
        f"Phase 12 §2 regression: {rel_path} (referenced in the lift "
        "patches) does not exist in cianfhoghlaim."
    )
    assert path.is_file(), (
        f"Phase 12 §2 regression: {rel_path} exists but is not a file."
    )


# --- §3: Each lift-patch has a per-PR checklist with ≥ 3 items --------------


def _count_pr_checklist_items(body: str) -> list[int]:
    """Return the number of checklist items per PR section.

    A PR section starts with "### PR #N" (or "## PR #N") and ends
    at the next "## " heading. Checklist items are lines starting
    with "- [ ]" or "- [x]".
    """
    # Split on "### PR #N" headings (case-insensitive).
    pr_sections = re.split(r"(?m)^#{2,4}\s+PR\s*#\d+", body)
    # The first split is the content BEFORE the first PR heading; skip it.
    counts: list[int] = []
    for section in pr_sections[1:]:
        # Stop at the next "## " heading (end of PR section).
        nxt = re.search(r"(?m)^#{2,4}\s+", section)
        if nxt:
            section = section[: nxt.start()]
        # Count checklist items.
        items = re.findall(r"(?m)^-\s*\[\s*[xX ]\s*\]", section)
        counts.append(len(items))
    return counts


@pytest.mark.parametrize("sister_key,filename", list(LIFT_PATCHES))
def test_phase12_lift_patch_has_pr_checklist(
    sister_key: str, filename: str
) -> None:
    """Each lift-patch has ≥ 3 PRs, each PR has ≥ 3 checklist items."""
    body = _read_lift_patch(sister_key, filename)
    counts = _count_pr_checklist_items(body)
    assert len(counts) >= 3, (
        f"Phase 12 §3 regression: {filename} has only {len(counts)} PR "
        "sections; the lift-patch contract requires ≥ 3 PRs per sister."
    )
    for i, n in enumerate(counts, start=1):
        assert n >= 3, (
            f"Phase 12 §3 regression: {filename} PR #{i} has only {n} "
            "checklist items; the lift-patch contract requires ≥ 3 items "
            "per PR."
        )


# --- §4: The customisation matrix mentions all 6 sisters --------------------


@pytest.mark.parametrize("sister_key,filename", list(LIFT_PATCHES))
def test_phase12_customisation_matrix_mentions_sister(
    sister_key: str, filename: str
) -> None:
    """The customisation matrix in proposal.md mentions the sister."""
    proposal = _read_proposal()
    assert sister_key in proposal, (
        f"Phase 12 §4 regression: '{sister_key}' is not mentioned in "
        "the proposal.md customisation matrix. Add a row for "
        f"{sister_key} to §2.x."
    )


def test_phase12_customisation_matrix_covers_all_6_sisters() -> None:
    """The customisation matrix explicitly covers all 6 sisters."""
    proposal = _read_proposal()
    # Look for the "## §2 — The customisation matrix" section header.
    assert "customisation matrix" in proposal.lower(), (
        "Phase 12 §4 regression: 'customisation matrix' is not mentioned "
        "in proposal.md."
    )
    # Each sister appears at least once in a §2.x section header.
    section_2 = proposal.split("§3", 1)[0]
    for sister_key, _ in LIFT_PATCHES:
        assert sister_key in section_2, (
            f"Phase 12 §4 regression: '{sister_key}' is not in the §2 "
            "customisation matrix section of proposal.md."
        )


# --- §5: The proposal + tasks + spec delta exist ---------------------------


def test_phase12_proposal_exists() -> None:
    """The Phase 12 proposal is authored."""
    path = (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-XX-sister-repo-lift-v1"
        / "proposal.md"
    )
    assert path.exists(), (
        "Phase 12 §5 regression: proposal.md is missing at "
        "openspec/changes/2026-09-XX-sister-repo-lift-v1/proposal.md."
    )


def test_phase12_tasks_exists() -> None:
    """The Phase 12 tasks checklist is authored."""
    path = (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-XX-sister-repo-lift-v1"
        / "tasks.md"
    )
    assert path.exists(), (
        "Phase 12 §5 regression: tasks.md is missing at "
        "openspec/changes/2026-09-XX-sister-repo-lift-v1/tasks.md."
    )


def test_phase12_spec_delta_exists() -> None:
    """The Phase 12 spec delta is authored."""
    path = (
        _REPO_ROOT
        / "openspec"
        / "changes"
        / "2026-09-XX-sister-repo-lift-v1"
        / "specs"
        / "sister-repo-customisation"
        / "spec.md"
    )
    assert path.exists(), (
        "Phase 12 §5 regression: spec.md is missing at "
        "openspec/changes/2026-09-XX-sister-repo-lift-v1/"
        "specs/sister-repo-customisation/spec.md."
    )


# --- §6: Each lift-patch has the 5 required sections ------------------------


@pytest.mark.parametrize("sister_key,filename", list(LIFT_PATCHES))
def test_phase12_lift_patch_has_5_required_sections(
    sister_key: str, filename: str
) -> None:
    """Each lift-patch has the 5 required sections per the lift-patch contract."""
    body = _read_lift_patch(sister_key, filename)
    required_sections = (
        "Source files",
        "Destination files",
        "Transformation rules",
        "Per-PR step-by-step checklist",
        "What stays behind",
    )
    for section in required_sections:
        assert section in body, (
            f"Phase 12 §6 regression: {filename} is missing the "
            f"required '{section}' section. The lift-patch contract "
            "requires all 5 sections."
        )


# --- §7: Each lift-patch names the sister repo explicitly -------------------


@pytest.mark.parametrize("sister_key,filename", list(LIFT_PATCHES))
def test_phase12_lift_patch_names_sister_in_one_line_summary(
    sister_key: str, filename: str
) -> None:
    """Each lift-patch has a 1-line summary naming the sister."""
    body = _read_lift_patch(sister_key, filename)
    # The 1-line summary is the blockquote block at the top of the file.
    # Assert that the sister_key appears within the first 1 KB.
    assert sister_key in body[:1024], (
        f"Phase 12 §7 regression: {filename} does not name "
        f"'{sister_key}' in the 1-line summary (first 1 KB)."
    )
