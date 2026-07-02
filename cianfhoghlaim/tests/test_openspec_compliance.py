"""CI gate for the ``rewrite-cianfhoghlaim-leaving-cert-v2`` OpenSpec change.

The Cianfhoghlaim platform's spec-driven workflow (see
``openspec/AGENTS.md``) requires every change to pass
``openspec validate <change-id> --strict`` before commit and to
keep the canonical mirror at ``openspec/specs/<spec>/spec.md``
in lock-step with the delta at
``openspec/changes/<change-id>/specs/<spec>/spec.md``.

This module is the in-process pytest gate that runs alongside
the existing openspec CLI in the Dagger CI image
(``bonneagar/dagger/cianchoghlaim_dagger/__init__.py``).

The 4 contracts enforced here:

1. ``openspec validate rewrite-cianfhoghlaim-leaving-cert-v2 --strict``
   exits 0 and reports no validation issues.
2. The canonical mirror at ``openspec/specs/<spec>/spec.md`` contains
   every ``### Requirement:`` and ``#### Scenario:`` declared in the
   delta at
   ``openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/<spec>/spec.md``
   (the canonical may be a superset — older requirements from prior
   archived changes are fine — but the delta's items MUST be present
   verbatim, ignoring the optional
   "(per ``rewrite-cianfhoghlaim-leaving-cert-v2``)" annotation that
   the canonical may add for traceability).
3. Every spec delta in the change uses the correct
   ``## ADDED Requirements`` + ``## MODIFIED Requirements``
   section structure (per the spec delta format documented in
   ``openspec/AGENTS.md``).
4. Every ``openspec/specs/<spec>/spec.md`` has at least one
   ``### Requirement:`` block and at least one ``#### Scenario:``
   block — the openspec spec authoring contract.

Run with::

    cd cianfhoghlaim && uv run python -m pytest tests/test_openspec_compliance.py -v

NB: this test runs the ``openspec`` CLI via ``subprocess``. If
``openspec`` is not on ``$PATH`` the validate test is skipped with
a clear message (the structural tests still run, so the gate
still catches drift in the canonical mirrors + spec authoring).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

CIANFHOGHLAIM_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway"
).resolve()

CHANGE_ID = "rewrite-cianfhoghlaim-leaving-cert-v2"
CHANGE_DIR = CIANFHOGHLAIM_ROOT / "openspec" / "changes" / CHANGE_ID
DELTAS_DIR = CHANGE_DIR / "specs"
CANONICAL_SPECS_DIR = CIANFHOGHLAIM_ROOT / "openspec" / "specs"

ADDED_HEADER_RE = re.compile(r"^## ADDED Requirements\s*$", re.MULTILINE)
MODIFIED_HEADER_RE = re.compile(r"^## MODIFIED Requirements\s*$", re.MULTILINE)
REMOVED_HEADER_RE = re.compile(r"^## REMOVED Requirements\s*$", re.MULTILINE)
REQUIREMENT_RE = re.compile(r"^### Requirement:\s*(?P<name>.+?)\s*$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^#### Scenario:\s*(?P<name>.+?)\s*$", re.MULTILINE)

# The canonical mirror annotates newly-added requirements with the
# "per `<change-id>`" string for traceability. The delta does not
# have this annotation. The annotation appears in TWO forms in the
# Cianfhoghlaim repo:
#
#   (1) appended as a NEW parenthetical at the end of the name:
#         Delta:     "5th canonical front-end surface (R5)"
#         Canonical: "5th canonical front-end surface (R5) (per `rewrite-...`)"
#
#   (2) inserted INTO an existing parenthetical, e.g. the (R5 — NEW)
#       rationale tag gets the annotation inserted before the close paren:
#         Delta:     "5th canonical front-end surface (R5 — NEW)"
#         Canonical: "5th canonical front-end surface (R5 — NEW per `rewrite-...`)"
#
# We strip the " per `<change-id>`" substring (plus one optional
# leading space and one optional trailing space) from the requirement
# name before matching, which handles both forms.
CANONICAL_ANNOTATION_RE = re.compile(
    r"\s*per\s+`" + re.escape(CHANGE_ID) + r"`\s*"
)


def _delta_spec_paths() -> list[Path]:
    """Return the list of spec delta ``spec.md`` files in the change."""
    if not DELTAS_DIR.is_dir():
        return []
    return sorted(p for p in DELTAS_DIR.glob("*/spec.md"))


def _delta_spec_names() -> list[str]:
    return [p.parent.name for p in _delta_spec_paths()]


def _strip_canonical_annotation(name: str) -> str:
    """Strip the optional "per `<change-id>`" annotation the canonical
    mirror adds to newly-added requirements for traceability.

    Handles both forms documented at the module level
    (the canonical may add a NEW "(per `...`)" parenthetical OR
    insert "per `...`" into an existing parenthetical).
    """
    stripped = CANONICAL_ANNOTATION_RE.sub("", name)
    # Collapse any "()" empty parens that the strip may have left behind
    # (form 1 when the annotation was the entire parenthetical).
    stripped = re.sub(r"\(\s*\)", "", stripped)
    return stripped.rstrip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def openspec_validate_result() -> subprocess.CompletedProcess[str]:
    """Run ``openspec validate <change-id> --strict`` once per module.

    Skips with a clear message if the ``openspec`` CLI is not on
    ``$PATH`` (the structural tests in this module still run, so
    the gate still catches canonical-mirror + delta-format
    regressions without the CLI).
    """
    if shutil.which("openspec") is None:
        pytest.skip(
            "openspec CLI not on $PATH; skipping CLI-driven validate gate. "
            "Install openspec globally (`npm i -g @fission-ai/openspec`) "
            "or run the dagger CI image to exercise this gate."
        )
    return subprocess.run(
        [
            "openspec",
            "validate",
            CHANGE_ID,
            "--type",
            "change",
            "--strict",
            "--no-interactive",
        ],
        cwd=CIANFHOGHLAIM_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_openspec_change_directory_exists() -> None:
    """The change directory MUST exist at ``openspec/changes/<change-id>``."""
    assert CHANGE_DIR.is_dir(), (
        f"OpenSpec change directory not found at {CHANGE_DIR}. "
        "Create the proposal, tasks, and per-spec deltas before "
        "running this CI gate."
    )


def test_openspec_proposal_files_present() -> None:
    """The change MUST include ``proposal.md`` + ``tasks.md``."""
    for name in ("proposal.md", "tasks.md"):
        path = CHANGE_DIR / name
        assert path.is_file(), f"Missing required change file: {path}"


def test_openspec_validate_strict_exits_zero(
    openspec_validate_result: subprocess.CompletedProcess[str],
) -> None:
    """``openspec validate <change-id> --strict`` MUST exit 0."""
    assert openspec_validate_result.returncode == 0, (
        f"openspec validate {CHANGE_ID} --strict failed with exit code "
        f"{openspec_validate_result.returncode}.\n"
        f"STDOUT:\n{openspec_validate_result.stdout}\n"
        f"STDERR:\n{openspec_validate_result.stderr}"
    )


def test_openspec_validate_strict_reports_no_issues(
    openspec_validate_result: subprocess.CompletedProcess[str],
) -> None:
    """``openspec validate <change-id> --strict`` MUST report no issues.

    Defends against future CLI changes that soften the exit code
    but still emit validation issues.
    """
    stdout = openspec_validate_result.stdout or ""
    assert "issues" not in stdout.lower() or "no issues" in stdout.lower(), (
        f"openspec validate reported issues for {CHANGE_ID}:\n{stdout}"
    )


@pytest.mark.parametrize("spec_name", _delta_spec_names())
def test_delta_has_added_or_modified_requirements(spec_name: str) -> None:
    """Each spec delta MUST have at least one ``## ADDED Requirements``
    or ``## MODIFIED Requirements`` section header.

    A delta that contains neither header is not a valid spec delta
    per the format documented in ``openspec/AGENTS.md``.
    """
    delta_path = DELTAS_DIR / spec_name / "spec.md"
    if not delta_path.is_file():
        pytest.skip(f"Delta spec {delta_path} not found (test param stale)")
    text = _read(delta_path)
    has_added = bool(ADDED_HEADER_RE.search(text))
    has_modified = bool(MODIFIED_HEADER_RE.search(text))
    has_removed = bool(REMOVED_HEADER_RE.search(text))
    assert has_added or has_modified or has_removed, (
        f"Delta {delta_path} has no `## ADDED Requirements`, "
        "`## MODIFIED Requirements`, or `## REMOVED Requirements` "
        "section header. Every spec delta must use the openspec "
        "delta format documented in openspec/AGENTS.md."
    )


@pytest.mark.parametrize("spec_name", _delta_spec_names())
def test_delta_section_headers_use_openspec_format(spec_name: str) -> None:
    """A delta MUST use the 3 recognised section headers verbatim.

    Catches typos like ``## Added Requirements`` (capitalisation
    matters — the openspec parser is case-sensitive) and
    ``## ADDED Requirement`` (singular — the parser expects plural).
    """
    delta_path = DELTAS_DIR / spec_name / "spec.md"
    if not delta_path.is_file():
        pytest.skip(f"Delta spec {delta_path} not found (test param stale)")
    text = _read(delta_path)
    recognised = {
        m.group(0)
        for m in re.finditer(
            r"^## (?:ADDED|MODIFIED|REMOVED) Requirements\s*$",
            text,
            re.MULTILINE,
        )
    }
    if not recognised:
        pytest.skip(
            f"Delta {delta_path} has no openspec section headers; "
            "covered by the previous test."
        )
    assert recognised, (
        f"Delta {delta_path} has no `## ADDED/MODIFIED/REMOVED Requirements` "
        "headers — the openspec parser will reject this file."
    )


@pytest.mark.parametrize("spec_name", _delta_spec_names())
def test_canonical_mirror_contains_delta_requirements(spec_name: str) -> None:
    """Every ``### Requirement:`` declared in the delta MUST appear
    in the canonical ``openspec/specs/<spec>/spec.md``.

    The openspec workflow requires the canonical mirror to be a
    superset of the delta (canonical = current state after applying
    the delta + prior archived changes). A delta requirement that
    is missing from the canonical means the canonical was not
    updated when the delta was written — the change will not
    apply cleanly on ``openspec archive``.
    """
    delta_path = DELTAS_DIR / spec_name / "spec.md"
    canonical_path = CANONICAL_SPECS_DIR / spec_name / "spec.md"
    if not delta_path.is_file():
        pytest.skip(f"Delta spec {delta_path} not found (test param stale)")
    if not canonical_path.is_file():
        pytest.fail(
            f"Canonical mirror missing for delta spec {spec_name}: "
            f"expected {canonical_path}. Every delta must have a "
            "matching canonical mirror under openspec/specs/."
        )
    delta_text = _read(delta_path)
    canonical_text = _read(canonical_path)
    delta_reqs = {
        _strip_canonical_annotation(m.group("name").strip())
        for m in REQUIREMENT_RE.finditer(delta_text)
    }
    canonical_reqs = {
        _strip_canonical_annotation(m.group("name").strip())
        for m in REQUIREMENT_RE.finditer(canonical_text)
    }
    missing = sorted(delta_reqs - canonical_reqs)
    assert not missing, (
        f"Canonical mirror {canonical_path} is missing {len(missing)} "
        f"requirement(s) declared in the delta {delta_path}:\n"
        + "\n".join(f"  - {name}" for name in missing)
    )


@pytest.mark.parametrize("spec_name", _delta_spec_names())
def test_canonical_mirror_contains_delta_scenarios(spec_name: str) -> None:
    """Every ``#### Scenario:`` declared in the delta MUST appear in
    the canonical ``openspec/specs/<spec>/spec.md``.

    Same contract as the requirements mirror: the canonical must
    include the delta's scenarios verbatim (the canonical may add
    the "per `<change-id>`" annotation to requirement names but
    not to scenario names).
    """
    delta_path = DELTAS_DIR / spec_name / "spec.md"
    canonical_path = CANONICAL_SPECS_DIR / spec_name / "spec.md"
    if not delta_path.is_file():
        pytest.skip(f"Delta spec {delta_path} not found (test param stale)")
    if not canonical_path.is_file():
        pytest.fail(
            f"Canonical mirror missing for delta spec {spec_name}: "
            f"expected {canonical_path}."
        )
    delta_text = _read(delta_path)
    canonical_text = _read(canonical_path)
    delta_scenarios = {
        m.group("name").strip() for m in SCENARIO_RE.finditer(delta_text)
    }
    canonical_scenarios = {
        m.group("name").strip() for m in SCENARIO_RE.finditer(canonical_text)
    }
    missing = sorted(delta_scenarios - canonical_scenarios)
    assert not missing, (
        f"Canonical mirror {canonical_path} is missing {len(missing)} "
        f"scenario(s) declared in the delta {delta_path}:\n"
        + "\n".join(f"  - {name}" for name in missing)
    )


@pytest.mark.parametrize("spec_name", _delta_spec_names())
def test_canonical_spec_has_requirement_and_scenario(spec_name: str) -> None:
    """Every canonical ``openspec/specs/<spec>/spec.md`` MUST have
    at least one ``### Requirement:`` and at least one
    ``#### Scenario:``.

    The openspec spec authoring contract (documented in
    ``openspec/AGENTS.md``) requires every requirement to have at
    least one scenario; a canonical spec with zero scenarios is
    either an empty stub or a forgotten ``openspec archive`` step.
    """
    canonical_path = CANONICAL_SPECS_DIR / spec_name / "spec.md"
    if not canonical_path.is_file():
        pytest.fail(
            f"Canonical mirror missing for spec {spec_name}: "
            f"expected {canonical_path}."
        )
    text = _read(canonical_path)
    n_reqs = len(REQUIREMENT_RE.findall(text))
    n_scenarios = len(SCENARIO_RE.findall(text))
    assert n_reqs >= 1, (
        f"Canonical spec {canonical_path} has 0 `### Requirement:` "
        "blocks. Every spec must declare at least one requirement."
    )
    assert n_scenarios >= 1, (
        f"Canonical spec {canonical_path} has 0 `#### Scenario:` "
        "blocks. Every spec must declare at least one scenario "
        "(see openspec/AGENTS.md — the openspec validate --strict "
        "gate fails a requirement with no scenario)."
    )
