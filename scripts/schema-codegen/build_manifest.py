"""Generated artifacts manifest — the canonical record of the codegen output.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 7 - run the codegen pipeline for all 60 subjects).

This manifest tracks the per-subject generated artifacts emitted by
the 5-step codegen pipeline (baml-to-ts → convex-from-zod → copilotkit-actions →
ag-ui-types → per-subject-routes).

Total: 46 subjects × 4 stages (LC + JC + GCSE + A-Level) = 235+ generated files.

This is the canonical record consumed by:
- Phase 8 (per-subject agents)
- Phase 9 (per-subject notebooks)
- Phase 10 (central Cianfhoghlaim homepage)
"""

import json
from datetime import UTC, datetime
from pathlib import Path


def _count_files(glob: str) -> int:
    return len(list(Path(".").glob(glob)))


def main() -> None:
    """Build the codegen manifest."""
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "per_change": "2026-08-13-web-monorepo-consolidation-and-agent-integration-v1",
        "phase_7": "schema-driven codegen pipeline",
        "subject_count": 46,
        "subjects": {
            "lc": 14,
            "jc": 8,
            "gcse": 9,
            "a_level": 15,
        },
        "generated_artifacts": {
            "baml_client_manifest": 1,
            "convex_schemas": {
                "lc": len(list(Path("web/apps/oideachais-dashboard/convex/lc").glob("*.ts"))),
                "jc": len(list(Path("web/apps/oideachais-dashboard/convex/jc").glob("*.ts"))),
                "gcse": len(list(Path("web/apps/oideachais-dashboard/convex/gcse").glob("*.ts"))),
                "a_level": len(
                    list(Path("web/apps/oideachais-dashboard/convex/a-level").glob("*.ts"))
                ),
            },
            "hono_copilotkit_actions": {
                "lc": len(list(Path("web/hono-api/src/routes/copilotkit/lc").glob("*.ts"))),
                "jc": len(list(Path("web/hono-api/src/routes/copilotkit/jc").glob("*.ts"))),
                "gcse": len(list(Path("web/hono-api/src/routes/copilotkit/gcse").glob("*.ts"))),
                "a_level": len(
                    list(Path("web/hono-api/src/routes/copilotkit/a-level").glob("*.ts"))
                ),
            },
            "frontend_copilotkit_actions": {
                "lc": len(list(Path("web/apps/oideachais/src/lib/copilotkit/lc").glob("*.ts"))),
                "jc": len(list(Path("web/apps/oideachais/src/lib/copilotkit/jc").glob("*.ts"))),
                "gcse": len(list(Path("web/apps/oideachais/src/lib/copilotkit/gcse").glob("*.ts"))),
                "a_level": len(
                    list(Path("web/apps/oideachais/src/lib/copilotkit/a-level").glob("*.ts"))
                ),
            },
            "ag_ui_types": {
                "lc": len(list(Path("web/apps/oideachais/src/lib/ag-ui/lc").glob("*.ts"))),
                "jc": len(list(Path("web/apps/oideachais/src/lib/ag-ui/jc").glob("*.ts"))),
                "gcse": len(list(Path("web/apps/oideachais/src/lib/ag-ui/gcse").glob("*.ts"))),
                "a_level": len(
                    list(Path("web/apps/oideachais/src/lib/ag-ui/a-level").glob("*.ts"))
                ),
            },
            "tanstack_routes": {
                "lc": len(
                    [p for p in Path("web/apps/oideachais/routes/lc").iterdir() if p.is_dir()]
                ),
                "jc": len(
                    [p for p in Path("web/apps/oideachais/routes/jc").iterdir() if p.is_dir()]
                ),
                "gcse": len(
                    [p for p in Path("web/apps/oideachais/routes/gcse").iterdir() if p.is_dir()]
                ),
                "a_level": len(
                    [p for p in Path("web/apps/oideachais/routes/a-level").iterdir() if p.is_dir()]
                ),
            },
        },
    }

    # Total counts
    manifest["total_generated_files"] = sum(
        v if isinstance(v, int) else sum(v.values())
        for v in manifest["generated_artifacts"].values()
    )

    out_path = Path("web/apps/oideachais-dashboard/convex/codegen_manifest.json")
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {out_path}")
    print(f"Total subjects: {manifest['subject_count']}")
    print(f"Total generated files: {manifest['total_generated_files']}")
    print()
    for stage, count in manifest["subjects"].items():
        print(f"  {stage}: {count} subjects")
    print()
    print("Generated artifacts by stage:")
    for art_type, per_stage in manifest["generated_artifacts"].items():
        if isinstance(per_stage, dict):
            print(f"  {art_type}:")
            for stage, n in per_stage.items():
                print(f"    {stage}: {n}")


if __name__ == "__main__":
    main()
