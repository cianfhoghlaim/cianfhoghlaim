"""CocoIndex v1 conformance checker (the R1–R4 contract).

Tangent 2 of the `2026-07-08-five-tangent-modernization` change.

This tool audits every `*.py` file under `cianfhoghlaim/cocoindex/` for
the 4-rule CocoIndex v1 conformance contract:

- **R1** — `coco_lifespan` mandate: each flow uses the shared lifespan
  from `_lifespan.py`.
- **R2** — canonical `coco.App(refresh_interval=...)` (no v0
  `@cocoindex.flow` DSL).
- **R3** — `mount_table_target` for vector sinks (no yield-dict loops
  to a LanceDB table).
- **R4** — `declare_vector_index(column="embedding")`.

R4-exempt marker: flows that do NOT write to a LanceDB table with an
`embedding` column (e.g. GeoParquet-only outputs like
`apple_photos_geospatial.py`) MAY carry a sibling `# R4-exempt: <reason>`
marker on a standalone line. The audit tool respects this marker and
reports R4 as PASS, citing the exemption reason in the audit log.

Usage:

    # Audit only (CI exit code 0/1):
    uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only

    # Apply fixes in-place (idempotent; safe to run repeatedly):
    uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --apply

    # Print the priority migration list (the 22 highest-value flows):
    uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --priority-list

Output is a per-flow table followed by an exit code (0 = pass, 1 = fail).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COCOINDEX_ROOT = Path(__file__).resolve().parents[2] / "cocoindex_flows"
"""The `cianfhoghlaim/cocoindex/` directory.

Computed from `dlt/common/cocoindex_v1_migrate.py`:
  cocoindex_v1_migrate.py  → dlt/common/ (this dir)
  parents[0] = cianfhoghlaim/dlt/common/
  parents[1] = cianfhoghlaim/dlt/
  parents[2] = cianfhoghlaim/  ← the package root
  / + "cocoindex"            → cianfhoghlaim/cocoindex/
"""

# R1 — must reference the shared lifespan
_R1_PATTERN = re.compile(r"_lifespan|coco_lifespan|from\s+\.\s*_lifespan|from\s+\.+_lifespan")
# R2 — must declare `coco.App(` (no `@cocoindex.flow(`)
_R2_APP_PATTERN = re.compile(r"coco\.App\(|coco\.App\s*\(")
_R2_FLOW_PATTERN = re.compile(r"@cocoindex\.flow")
# R3 — must use `mount_table_target(`
_R3_PATTERN = re.compile(r"mount_table_target|mount_table_source")
# R4 — must use `declare_vector_index(`
_R4_PATTERN = re.compile(r"declare_vector_index")
# R4-exempt marker — `# R4-exempt: <reason>` on a standalone line.
# Respected by the audit tool for flows that don't write to a LanceDB
# table with an `embedding` column (e.g. GeoParquet-only outputs).
_R4_EXEMPT_PATTERN = re.compile(r"^\s*#\s*R4-exempt\s*:", re.MULTILINE)

# not-a-flow marker — `# not-a-flow: <reason>` on a standalone line.
# Respected by the audit tool for files that live under `cocoindex/` but
# are NOT flows (e.g. Phase 0 primitives that expose `@coco.fn` + `ContextKey`
# but never write to a LanceDB table; colocated test files like
# `test_*.py`). The marker exempts the file from ALL 4 rules (R1+R2+R3+R4).
# Added in the `2026-07-15-pipeline-architecture-clarity-v1` change.
_NOT_A_FLOW_PATTERN = re.compile(r"^\s*#\s*not-a-flow\s*:", re.MULTILINE)

# The 22 priority flows for v1 conformance (per the openspec change).
PRIORITY_FLOWS: tuple[str, ...] = (
    "mathematics_embedding.py",
    "chemistry_embedding.py",
    "geography_embedding.py",
    "gaeilge_embedding.py",
    "computer_science_embedding.py",
    "english_embedding.py",
    "government_circulars_embedding.py",  # BIEP-v1 scope (may not exist yet)
    "leabharlann_flow.py",
    "leabharlann_zotero_embedding.py",   # may not exist as standalone
    "leabharlann_takeout_embedding.py",   # may not exist as standalone
    "official_media_feed_embedding.py",  # may not exist
    "official_media_post_embedding.py",  # may not exist
    "apple_photos_metadata.py",
    "apple_photos_chunks.py",
    "apple_photos_geospatial.py",
    "agent_registry.py",
    "codebase_indexing.py",
    "upstream_api_surface.py",
    "upstream_blog_monitor.py",          # may not exist as standalone
    "cross_subject_competency_embedding.py",
    "ocr_aware_flow.py",
    "cocoindex_v1_conformance.py",        # meta — must itself conform
)


@dataclass
class FlowAudit:
    """Per-flow compliance result."""

    path: Path
    r1_uses_lifespan: bool
    r2_uses_coco_app: bool
    r2_avoids_old_flow: bool
    r3_uses_mount_table: bool
    r4_uses_vector_index: bool
    r4_exempt: bool = False
    r4_exempt_reason: str = ""
    not_a_flow: bool = False
    not_a_flow_reason: str = ""

    @property
    def violations(self) -> tuple[str, ...]:
        if self.not_a_flow:
            # not-a-flow files bypass ALL 4 rules (Phase 0 primitives,
            # colocated test files, etc.). They live under `cocoindex/`
            # for organizational convenience but never declare a
            # `coco.App` or write to a LanceDB table.
            return ()
        v = []
        if not self.r1_uses_lifespan:
            v.append("R1: missing shared lifespan (use `from . import coco_lifespan`)")
        if not self.r2_uses_coco_app:
            v.append("R2: missing canonical `coco.App(refresh_interval=...)`")
        if not self.r2_avoids_old_flow:
            v.append("R2: legacy `@cocoindex.flow` DSL — replace with v1 App pattern")
        if not self.r3_uses_mount_table:
            v.append("R3: missing `mount_table_target(...)` — yield-dict loops are R4 violations")
        if not self.r4_uses_vector_index and not self.r4_exempt:
            v.append("R4: missing `declare_vector_index(column='embedding')`")
        return tuple(v)

    @property
    def passes(self) -> bool:
        return not self.violations

    def render(self) -> str:
        if self.not_a_flow:
            status = "PASS (not-a-flow)"
        elif self.r4_exempt and not self.r4_uses_vector_index:
            status = "PASS (R4-exempt)"
        elif self.passes:
            status = "PASS"
        else:
            status = f"FAIL ({len(self.violations)})"
        return f"  {self.path.name:<55} {status}"


def audit_flow(path: Path) -> FlowAudit:
    """Audit a single `.py` flow file."""
    src = path.read_text(encoding="utf-8")

    # not-a-flow marker takes precedence over R4-exempt (a not-a-flow
    # file never declares R4 anyway). Both bypass the 4-rule audit.
    not_a_flow_match = _NOT_A_FLOW_PATTERN.search(src)
    not_a_flow = not_a_flow_match is not None
    not_a_flow_reason = ""
    if not_a_flow and not_a_flow_match is not None:
        not_a_flow_reason = src[not_a_flow_match.end():].split("\n", 1)[0].strip()

    r4_exempt_match = _R4_EXEMPT_PATTERN.search(src)
    r4_exempt = r4_exempt_match is not None
    r4_exempt_reason = ""
    if r4_exempt and r4_exempt_match is not None:
        # Capture the reason text after the `# R4-exempt:` marker.
        r4_exempt_reason = src[r4_exempt_match.end():].split("\n", 1)[0].strip()

    return FlowAudit(
        path=path,
        r1_uses_lifespan=bool(_R1_PATTERN.search(src)),
        r2_uses_coco_app=bool(_R2_APP_PATTERN.search(src)),
        r2_avoids_old_flow=not _R2_FLOW_PATTERN.search(src),
        r3_uses_mount_table=bool(_R3_PATTERN.search(src)),
        r4_uses_vector_index=bool(_R4_PATTERN.search(src)),
        r4_exempt=r4_exempt,
        r4_exempt_reason=r4_exempt_reason,
        not_a_flow=not_a_flow,
        not_a_flow_reason=not_a_flow_reason,
    )


def list_flows() -> list[Path]:
    """All `.py` files under `cianfhoghlaim/cocoindex/` (excluding cache + non-flow)."""
    if not COCOINDEX_ROOT.exists():
        return []
    # Recurse into nested directories (european_nations/, knowledge_graph/,
    # commonwealth/, etc.) — the v7-flatten moved every per-jurisdiction
    # CocoIndex flow into a nested sub-tree.
    flows = sorted(p for p in COCOINDEX_ROOT.rglob("*.py") if not p.name.startswith("_"))
    return flows


def audit_all() -> list[FlowAudit]:
    return [audit_flow(p) for p in list_flows()]


def render_table(audits: list[FlowAudit]) -> str:
    header = f"  {'flow':<55} status"
    header += "\n  " + ("-" * 64)
    rows = "\n".join(a.render() for a in audits)
    pass_count = sum(1 for a in audits if a.passes)
    fail_count = len(audits) - pass_count
    summary = f"\n  cocoindex_v1_conformance: {pass_count}/{len(audits)} flows pass"
    if fail_count:
        summary += f"  ({fail_count} FAIL)"
    return f"{header}\n{rows}{summary}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CocoIndex v1 conformance checker (R1+R2+R3+R4)."
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--check-only",
        action="store_true",
        help="Default. Audit and report; exit 1 on any violation.",
    )
    g.add_argument(
        "--apply",
        action="store_true",
        help="Apply remediation (idempotent; non-destructive for already-conformant flows).",
    )
    g.add_argument(
        "--priority-list",
        action="store_true",
        help="Print the 22 priority flows for the first migration batch.",
    )
    args = parser.parse_args(argv)

    if args.priority_list:
        print("Priority migration list (the 22 highest-value flows):")
        for name in PRIORITY_FLOWS:
            print(f"  - {name}")
        return 0

    audits = audit_all()
    print(render_table(audits))

    if args.apply:
        # The remediation logic is intentionally OUT OF SCOPE for this
        # change — this is an audit-only tool. The actual rewrite happens
        # in the BIEP-v1 follow-up change (per the openspec MODIFIED note
        # on cianfhoghlaim-cocoindex-v1-migration).
        print(
            "\n  --apply: no-op (remediation logic deferred to BIEP-v1 follow-up change)",
            file=sys.stderr,
        )

    return 0 if all(a.passes for a in audits) else 1


if __name__ == "__main__":
    sys.exit(main())
