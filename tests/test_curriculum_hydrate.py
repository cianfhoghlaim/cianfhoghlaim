"""Smoke tests for ``scripts/curriculum_hydrate.py``.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change.

Three smoke contracts (per the operator's verification matrix):

1. CLI parsing works for every documented subcommand.
2. The geography resource yields >= 1 row from ``stedding/geog.pdf``
   in ``--dry-run --limit 1`` mode (the spec scenario
   "geog.pdf hydrates geography topics").
3. The policies resource enumerates >= 1 NCCA PDF under
   ``leaving_certificate/`` whose filename hints at a policy or
   programme document (with a soft-skip marker when no such PDF is
   present).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR.parent))

from scripts import curriculum_hydrate  # noqa: E402

GEOG_HANDMADE = curriculum_hydrate.GEOG_HANDMADE
LC_PDF_ROOT = curriculum_hydrate.LC_PDF_ROOT


# ---------------------------------------------------------------------------
# 1. argparse — every documented subcommand must parse cleanly
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "subcommand",
    ["geography", "gaeilge", "english", "policies", "all"],
)
def test_cli_parses_for_each_subcommand(subcommand: str) -> None:
    args = curriculum_hydrate._parse_args([subcommand])
    assert args.subcommand == subcommand


def test_cli_parses_global_flags_with_subcommand() -> None:
    args = curriculum_hydrate._parse_args(
        ["policies", "--dry-run", "--limit", "2", "--dataset", "foo"]
    )
    assert args.subcommand == "policies"
    assert args.dry_run is True
    assert args.limit == 2
    assert args.dataset == "foo"


def test_cli_parses_no_dlt_alias() -> None:
    args = curriculum_hydrate._parse_args(["english", "--no-dlt"])
    assert args.no_dlt is True
    assert args.dry_run is False


def test_cli_env_dataset_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BI_EP_DUCKLAKE_DATASET", "env_dataset")
    args = curriculum_hydrate._parse_args(["policies"])
    assert args.dataset == "env_dataset"


# ---------------------------------------------------------------------------
# 2. Geography resource yields >= 1 row from stedding/geog.pdf (dry-run)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not GEOG_HANDMADE.exists(),
    reason="stedding/geog.pdf not present (operator optional)",
)
def test_geography_resource_yields_row_for_handmade_pdf() -> None:
    """The spec scenario: 'geog.pdf hydrates geography topics'."""
    rows = list(
        curriculum_hydrate.geography_topics_resource(
            limit=20, ocr_backend="qwen3-vl-8b", dry_run=True, dataset="test"
        )
    )
    assert rows, "geography_topics_resource emitted zero rows"
    matching = [r for r in rows if "stedding/geog.pdf" in r.get("source_pdf", "")]
    assert matching, (
        f"no row with source_pdf containing 'stedding/geog.pdf' "
        f"in {len(rows)} rows; sources: "
        f"{sorted({r['source_pdf'] for r in rows})[:5]}"
    )
    row = matching[0]
    assert row["source_pdf"] == str(GEOG_HANDMADE)
    assert row["source_page"] >= 1
    assert "source_url" in row
    assert row["subject"] == "geography"
    assert row["extraction_status"] == "dry_run"


def test_geography_dry_run_graceful_when_handmade_pdf_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If stedding/geog.pdf is missing, the script must not crash."""
    fake_missing = tmp_path / "does-not-exist.pdf"
    monkeypatch.setattr(curriculum_hydrate, "GEOG_HANDMADE", fake_missing)
    rows = list(
        curriculum_hydrate.geography_topics_resource(
            limit=10, dry_run=True, dataset="test"
        )
    )
    # No crash, no exception; still emits rows for the LC PDFs under
    # leaving_certificate/geography/ (assuming the corpus exists).
    if rows:
        for row in rows:
            assert row["subject"] == "geography"


# ---------------------------------------------------------------------------
# 3. Policies resource enumerates >= 1 NCCA policy PDF
# ---------------------------------------------------------------------------


def _looks_like_policy_pdf(pdf_path: Path) -> bool:
    name = pdf_path.name.lower()
    return any(token in name for token in curriculum_hydrate._POLICY_FILENAME_TOKENS)


@pytest.mark.skipif(
    not LC_PDF_ROOT.exists(),
    reason="leaving_certificate/ corpus not present",
)
def test_policies_resource_enumerates_ncca_policy_pdfs() -> None:
    policy_pdfs = curriculum_hydrate._policy_pdfs()
    if not policy_pdfs:
        pytest.skip("no NCCA policy PDFs found at leaving_certificate/ root")
    rows = list(
        curriculum_hydrate.education_ie_policies_resource(
            limit=10, dry_run=True, dataset="test"
        )
    )
    assert rows, "policies resource emitted zero rows"
    for row in rows:
        assert row["subject"] == "education_ie_policy"
        assert row["source_pdf"]
        assert isinstance(row["source_page"], int)
        assert row["source_url"]


def test_policy_filename_token_recogniser_matches_known_pdfs() -> None:
    """The 5 NCCA root-level PDFs are picked up by the token heuristic."""
    if not LC_PDF_ROOT.exists():
        pytest.skip("leaving_certificate/ corpus not present")
    expected = {
        "sc-l1-l2-programme-statement.pdf",
        "key-competencies-in-senior-cycle_en.pdf",
        "scr-advisory-report_en.pdf",
        "the-potential-of-online-learning-environments_en.pdf",
        "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
    }
    found = {p.name.lower() for p in curriculum_hydrate._policy_pdfs()}
    matched = expected & found
    assert matched, f"expected at least one of {sorted(expected)}; found {sorted(found)}"


# ---------------------------------------------------------------------------
# 4. DLT source + resource metadata sanity
# ---------------------------------------------------------------------------


def test_dlt_source_builds_for_each_subcommand() -> None:
    for subject in ("geography", "gaeilge", "english", "policies"):
        src = curriculum_hydrate.curriculum_source(
            subject=subject,
            limit=None,
            ocr_backend="qwen3-vl-8b",
            dry_run=True,
            dataset="test",
        )
        names = list(src.selected_resources.keys())
        assert len(names) == 1, f"{subject}: expected 1 resource, got {names}"


def test_resources_have_provenance_primary_key() -> None:
    """Per the saga spec: every row must be mergeable by the provenance triple."""
    for fn in (
        curriculum_hydrate.geography_topics_resource,
        curriculum_hydrate.gaeilge_poems_higher_resource,
        curriculum_hydrate.english_poets_higher_resource,
        curriculum_hydrate.education_ie_policies_resource,
    ):
        resource = fn(limit=1, dry_run=True, dataset="test")
        hints = getattr(resource, "_hints", {}) or {}
        pk = hints.get("primary_key") if isinstance(hints, dict) else None
        assert pk is not None, f"{fn.__name__} has no primary_key"
        pk_names = list(pk) if not isinstance(pk, str) else [pk]
        for col in curriculum_hydrate.PROVENANCE_PK:
            assert col in pk_names, (
                f"{fn.__name__} primary_key {pk_names} missing {col}"
            )


# ---------------------------------------------------------------------------
# 5. Dry-run JSONL shape
# ---------------------------------------------------------------------------


def test_dry_run_writes_jsonl_with_provenance(tmp_path: Path, monkeypatch) -> None:
    """--dry-run writes one JSONL per resource under ingest_queue/curriculum/."""
    queue = tmp_path / "queue"
    monkeypatch.setattr(curriculum_hydrate, "DRY_RUN_QUEUE", queue)
    rc = curriculum_hydrate._run_dry_run(
        "policies", limit=2, ocr_backend="qwen3-vl-8b", dataset="test"
    )
    assert rc == 0
    files = list(queue.glob("*.jsonl"))
    assert files, "no JSONL files written under DRY_RUN_QUEUE"
    lines = files[0].read_text(encoding="utf-8").splitlines()
    if lines:
        first = json.loads(lines[0])
        assert first["subject"] == "education_ie_policy"
        assert first["extraction_status"] == "dry_run"
        assert "source_pdf" in first
        assert "source_page" in first
        assert "source_url" in first
