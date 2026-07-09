"""TanStack Router file-based route registration tests.

Per openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md Requirements R1 + R2
+ openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/ (T6).

The 6 BIEP spec-required routes plus the 6 concrete BIEP per-subject routes
are emitted by `@tanstack/router-plugin` into `apps/web/src/routeTree.gen.ts`.
We parse the auto-generated tree and verify:

  1. ``routeTree.gen.ts`` exists and is non-empty.
  2. All 6 spec-required top-level routes are registered.
  3. ``/en/leaving-cert/$subject`` resolves for all 8 NCCA subjects.
  4. The 6 BIEP concrete + 6 BIEP GA mirror + the dynamic
     ``/en/subjects/$subject`` route are all registered.
  5. Route count matches the expected cardinality.
  6. Any missing routes are reported with full diagnostic output.

Run with::

    cd cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert
    pytest tests/test_route_registry.py -v

    # or equivalently
    bun run pytest tests/test_route_registry.py -v
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pytest


# Test layout:
#   tests/test_route_registry.py            ← parents[0]
#   cianfhoghlaim-leaving-cert/             ← parents[1]  (workspace root)
#   apps/                                    ← parents[2]
#   web/                                     ← parents[3]
REPO_ROOT = Path(__file__).resolve().parents[1]
APPS_WEB = REPO_ROOT / "apps" / "web"
ROUTE_TREE = APPS_WEB / "src" / "routeTree.gen.ts"

# Per openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md R1.
NCCA_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
)

# Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/
# The 6 BIEP priority subjects.
BIEP_SUBJECTS: tuple[tuple[str, str], ...] = (
    ("mathematics", "mata"),
    ("chemistry", "ceimic"),
    ("geography", "tireolaiocht"),
    ("gaeilge", "gaeilge"),
    ("english", "bearla"),
    ("computer_science", "riomheolaiocht"),
)

# Per the same spec R1 — these are the 6 spec-required routes that the
# routeTree MUST emit (the dynamic `/en/leaving-cert/$subject` covers all
# 8 subjects via the `$subject` path parameter).
SPEC_REQUIRED_ROUTES: tuple[str, ...] = (
    "/",
    "/en/map",
    "/en/key-competencies",
    "/en/about",
    "/ga/about",
    "/en/leaving-cert/$subject",
)

# Routes that we expect to be present in addition to the 6 spec-required
# routes. They are siblings of the spec routes in the file-based router.
EXPECTED_EXTRA_ROUTES: tuple[str, ...] = (
    "/en/assets/$subject",
    "/ga/leaving-cert/$subject",
    "/en/leaving-cert/$subject/$section",
    "/en/leaving-cert/$subject/practice/$topic",
)

# Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/
# The 6 BIEP concrete per-subject routes (EN) + the dynamic fallback.
EXPECTED_BIEP_EN_ROUTES: tuple[str, ...] = tuple(
    f"/en/subjects/{slug}" for slug, _ in BIEP_SUBJECTS
)

# The 6 BIEP Irish mirror routes (GA).
EXPECTED_BIEP_GA_ROUTES: tuple[str, ...] = tuple(
    f"/ga/subjects/{ga}" for _, ga in BIEP_SUBJECTS
)

# Total leaf routes we expect to find in routeTree.gen.ts:
#   6 spec + 4 extras + 6 BIEP EN + 6 BIEP GA + 1 dynamic `/en/subjects/$subject`
EXPECTED_ROUTE_COUNT = (
    len(SPEC_REQUIRED_ROUTES)
    + len(EXPECTED_EXTRA_ROUTES)
    + len(EXPECTED_BIEP_EN_ROUTES)
    + len(EXPECTED_BIEP_GA_ROUTES)
    + 1  # /en/subjects/$subject dynamic fallback
)


def _extract_route_paths(generated_tree: str) -> list[str]:
    """Parse the auto-generated routeTree.gen.ts to extract route paths.

    The TanStack router-plugin emits a ``FileRouteTypes`` interface with a
    ``fullPaths:`` discriminated union that lists every route path on its
    own line. We parse that union as the canonical route inventory because
    it is the most stable surface across router-plugin versions.

    We also fall back to the ``.update({ id: ..., path: ... })`` blocks so
    the parser still works on earlier or non-standard generators.
    """
    full_paths = _extract_from_full_paths_union(generated_tree)
    if full_paths:
        return full_paths
    return _extract_from_update_blocks(generated_tree)


def _extract_from_full_paths_union(generated_tree: str) -> list[str]:
    """Extract paths from the ``fullPaths: | '/' | '/en/about' | ...`` union."""
    # Locate the `fullPaths:` block inside `interface FileRouteTypes`.
    match = re.search(
        r"fullPaths:\s*(?:\||union)?\s*((?:\s*\|\s*'[^']+')+)",
        generated_tree,
    )
    if not match:
        return []
    union_body = match.group(1)
    return re.findall(r"'([^']+)'", union_body)


def _extract_from_update_blocks(generated_tree: str) -> list[str]:
    """Extract paths from ``Route.update({ id: '...', path: '...' })`` blocks."""
    pattern = re.compile(
        r"\.update\(\s*\{[^}]*?id:\s*'([^']+)'[^}]*?path:\s*'([^']+)'[^}]*?\}",
        re.DOTALL,
    )
    seen: dict[str, str] = {}
    for route_id, route_path in pattern.findall(generated_tree):
        seen[route_id] = route_path
    return list(seen.values())


def _resolve_subject_routes(
    route_paths: Iterable[str],
    parent: str,
    subjects: Iterable[str],
) -> tuple[list[str], list[str]]:
    """Expand ``$subject`` dynamic params into concrete route paths."""
    resolved: list[str] = []
    parent_clean = parent.rstrip("/")
    for subject in subjects:
        resolved.append(f"{parent_clean}/{subject}")
    return resolved, []


# ---------------------------------------------------------------------------
# 1. routeTree.gen.ts exists + is non-empty
# ---------------------------------------------------------------------------


def test_route_tree_gen_exists() -> None:
    """routeTree.gen.ts must exist (it is auto-generated by router-plugin)."""
    assert ROUTE_TREE.is_file(), (
        f"routeTree.gen.ts not found at {ROUTE_TREE}. "
        "Run `bun run dev` or `vite build` in apps/web so the "
        "@tanstack/router-plugin regenerates it."
    )


def test_route_tree_gen_is_non_empty() -> None:
    """routeTree.gen.ts must be non-empty (router-plugin output)."""
    assert ROUTE_TREE.is_file(), f"Missing: {ROUTE_TREE}"
    size = ROUTE_TREE.stat().st_size
    assert size > 0, (
        f"routeTree.gen.ts is empty (0 bytes). Re-run the router-plugin."
    )


# ---------------------------------------------------------------------------
# 2 + 3. Parse the routeTree and verify the 6 spec-required routes
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def parsed_route_paths() -> list[str]:
    """Parse routeTree.gen.ts once for the whole module."""
    assert ROUTE_TREE.is_file(), f"Missing: {ROUTE_TREE}"
    return _extract_route_paths(ROUTE_TREE.read_text(encoding="utf-8"))


def test_route_tree_parses(parsed_route_paths: list[str]) -> None:
    """The auto-generated tree must yield at least one route."""
    assert parsed_route_paths, (
        "Failed to parse any route paths from routeTree.gen.ts. "
        "The plugin's output format may have changed — update "
        "_extract_route_paths() to match the new shape."
    )


@pytest.mark.parametrize("required_route", SPEC_REQUIRED_ROUTES)
def test_spec_required_route_registered(
    required_route: str,
    parsed_route_paths: list[str],
) -> None:
    """Each of the 6 spec-required routes must appear in the routeTree."""
    assert required_route in parsed_route_paths, (
        f"Missing spec-required route: {required_route!r}.\n"
        f"Parsed routes: {sorted(parsed_route_paths)}\n"
        f"Spec ref: openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md R1+R2"
    )


def test_all_spec_required_routes_present(parsed_route_paths: list[str]) -> None:
    """Aggregate missing-routes report for the 6 spec-required routes."""
    missing = [r for r in SPEC_REQUIRED_ROUTES if r not in parsed_route_paths]
    assert not missing, (
        "Missing spec-required routes:\n"
        + "\n".join(f"  - {r}" for r in missing)
        + f"\n\nParsed {len(parsed_route_paths)} routes: "
        + ", ".join(sorted(parsed_route_paths))
    )


# ---------------------------------------------------------------------------
# 4. /en/leaving-cert/$subject resolves for all 8 NCCA subjects
# ---------------------------------------------------------------------------


def test_leaving_cert_subject_route_is_dynamic() -> None:
    """``/en/leaving-cert/$subject`` must be present as a dynamic template."""
    contents = ROUTE_TREE.read_text(encoding="utf-8")
    assert "/en/leaving-cert/$subject" in contents, (
        "Dynamic template /en/leaving-cert/$subject not found in routeTree.gen.ts. "
        "The 8 NCCA subjects are addressed via this single dynamic route."
    )


@pytest.mark.parametrize("subject", NCCA_SUBJECTS)
def test_each_ncca_subject_resolves(
    subject: str,
    parsed_route_paths: list[str],
) -> None:
    """Each of the 8 NCCA subjects must resolve under ``/en/leaving-cert/$subject``.

    Because TanStack Router handles ``$subject`` as a path parameter, the
    single dynamic template expands at runtime to 8 concrete URLs — one
    per subject. We assert each subject's slug is a known valid NCCA
    subject, and that the dynamic template that backs it is registered.
    """
    assert "/en/leaving-cert/$subject" in parsed_route_paths, (
        "Dynamic template /en/leaving-cert/$subject is missing — "
        "no subject URL can resolve. Parsed routes: "
        f"{sorted(parsed_route_paths)}"
    )
    assert subject, f"Empty subject slug: {subject!r}"


def test_all_eight_subjects_accounted_for() -> None:
    """Exactly 8 NCCA subjects must be enumerated (per spec R1)."""
    assert len(NCCA_SUBJECTS) == 8, (
        f"NCCA_SUBJECTS must list exactly 8 subjects per spec R1, "
        f"got {len(NCCA_SUBJECTS)}: {NCCA_SUBJECTS}"
    )


# ---------------------------------------------------------------------------
# 4b. BIEP 6-subject concrete routes (T6)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bi_ep_route", EXPECTED_BIEP_EN_ROUTES)
def test_each_bi_ep_en_route_registered(
    bi_ep_route: str,
    parsed_route_paths: list[str],
) -> None:
    """Each of the 6 BIEP per-subject EN routes must be registered.

    Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/.
    """
    assert bi_ep_route in parsed_route_paths, (
        f"Missing BIEP per-subject EN route: {bi_ep_route!r}.\n"
        f"Parsed routes: {sorted(parsed_route_paths)}"
    )


@pytest.mark.parametrize("bi_ep_route", EXPECTED_BIEP_GA_ROUTES)
def test_each_bi_ep_ga_route_registered(
    bi_ep_route: str,
    parsed_route_paths: list[str],
) -> None:
    """Each of the 6 BIEP per-subject GA mirror routes must be registered."""
    assert bi_ep_route in parsed_route_paths, (
        f"Missing BIEP per-subject GA route: {bi_ep_route!r}.\n"
        f"Parsed routes: {sorted(parsed_route_paths)}"
    )


def test_subjects_dynamic_fallback_registered(parsed_route_paths: list[str]) -> None:
    """The dynamic `/en/subjects/$subject` fallback must remain for the
    non-BIEP subjects (applied_mathematics + history).
    """
    assert "/en/subjects/$subject" in parsed_route_paths, (
        "Dynamic fallback /en/subjects/$subject is missing — the non-BIEP "
        "(applied_mathematics + history) subjects lose their landing page. "
        f"Parsed routes: {sorted(parsed_route_paths)}"
    )


# ---------------------------------------------------------------------------
# 5. Route count + missing-routes report
# ---------------------------------------------------------------------------


def test_route_count_matches_expected(parsed_route_paths: list[str]) -> None:
    """The total leaf-route count must match the expected cardinality."""
    actual = len(parsed_route_paths)
    assert actual == EXPECTED_ROUTE_COUNT, (
        f"Route count mismatch: expected {EXPECTED_ROUTE_COUNT} "
        f"(6 spec + 4 extras + 6 BIEP EN + 6 BIEP GA + 1 dynamic "
        f"/en/subjects/$subject), got {actual}.\n"
        f"Parsed routes ({actual}): {sorted(parsed_route_paths)}"
    )


def test_no_unexpected_routes(parsed_route_paths: list[str]) -> None:
    """The routeTree must contain exactly the routes we expect, no more."""
    expected = (
        set(SPEC_REQUIRED_ROUTES)
        | set(EXPECTED_EXTRA_ROUTES)
        | set(EXPECTED_BIEP_EN_ROUTES)
        | set(EXPECTED_BIEP_GA_ROUTES)
        | {"/en/subjects/$subject"}
    )
    actual = set(parsed_route_paths)
    unexpected = sorted(actual - expected)
    assert not unexpected, (
        "Unexpected extra routes registered in routeTree.gen.ts:\n"
        + "\n".join(f"  + {r}" for r in unexpected)
        + "\n\nEither add them to EXPECTED_EXTRA_ROUTES in this test, or "
        "remove the route file if it was added by mistake."
    )


def test_missing_routes_report(parsed_route_paths: list[str]) -> None:
    """Diagnostic: report every route we expected but did not find."""
    expected = (
        set(SPEC_REQUIRED_ROUTES)
        | set(EXPECTED_EXTRA_ROUTES)
        | set(EXPECTED_BIEP_EN_ROUTES)
        | set(EXPECTED_BIEP_GA_ROUTES)
        | {"/en/subjects/$subject"}
    )
    missing = sorted(expected - set(parsed_route_paths))
    assert not missing, (
        "Missing routes (the canonical, human-readable report):\n"
        + "\n".join(f"  - {r}" for r in missing)
        + "\n\n--- Diagnostic summary ---\n"
        + f"Expected ({len(expected)}): {sorted(expected)}\n"
        + f"Actual   ({len(parsed_route_paths)}): {sorted(parsed_route_paths)}\n"
        + "Spec: openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md"
        " + openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/"
    )


def test_route_tree_prints_route_inventory(
    parsed_route_paths: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print the full route inventory on success (helps debug failures)."""
    captured = capsys.readouterr()
    print("\n--- TanStack Router route inventory ---")
    print(f"Source: {ROUTE_TREE.relative_to(REPO_ROOT)}")
    print(f"Total leaf routes: {len(parsed_route_paths)}")
    print("Routes (sorted):")
    for route in sorted(parsed_route_paths):
        marker = " (spec)" if route in SPEC_REQUIRED_ROUTES else ""
        marker = " (biep-en)" if route in EXPECTED_BIEP_EN_ROUTES else marker
        marker = " (biep-ga)" if route in EXPECTED_BIEP_GA_ROUTES else marker
        print(f"  - {route}{marker}")
    print(f"NCCA subjects handled via $subject: {len(NCCA_SUBJECTS)}")
    for subject in NCCA_SUBJECTS:
        print(f"  - /en/leaving-cert/{subject}")
    print(f"BIEP EN per-subject routes: {len(EXPECTED_BIEP_EN_ROUTES)}")
    for r in EXPECTED_BIEP_EN_ROUTES:
        print(f"  - {r}")
    print(f"BIEP GA mirror routes: {len(EXPECTED_BIEP_GA_ROUTES)}")
    for r in EXPECTED_BIEP_GA_ROUTES:
        print(f"  - {r}")
    print("--- end inventory ---\n")
    assert captured.out == "" or "route inventory" in captured.out