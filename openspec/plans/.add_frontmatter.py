#!/usr/bin/env python3
"""Add `status:` frontmatter to every openspec/plans/*.md file.

Statuses per the STATUS.md index:
- research: all plans except the 5 tangents
- deferred: the 5 tangents
"""
from __future__ import annotations

from pathlib import Path

PLANS_DIR = Path(__file__).resolve().parent

DEFERRED = {
    "tangent_1_micro_credentials.md",
    "tangent_2_generative_tutoring.md",
    "tangent_3_automated_assessment.md",
    "tangent_4_immersive_content.md",
    "tangent_5_policy_simulator.md",
}

# Per-plan metadata for the frontmatter
META = {
    "data_engineering_deep_dive.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/oideachais-pipeline/spec.md, openspec/specs/data-pipeline/spec.md, docs/02-data-platform/data-architecture.md]",
    },
    "deployment_and_ai_strategy.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/infrastructure/spec.md, docs/01-platform-architecture/]",
    },
    "deployment_stack_strategy.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/infrastructure-stacks/spec.md]",
    },
    "education_audit_plan.md": {
        "supersedes": "[]",
        "superseded_by": "[]",  # the live one
    },
    "exponential_improvement_roadmap.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/oideachais-pipeline/spec.md, openspec/specs/data-pipeline/spec.md, openspec/specs/agent-frameworks/spec.md, openspec/specs/assessment-extraction/spec.md]",
    },
    "final_exponential_strategy.md": {
        "supersedes": "[exponential_improvement_roadmap.md]",
        "superseded_by": "[docs/04-ai-ml/llm-stack-hierarchy.md]",
    },
    "gcp_ai_optimization_strategy.md": {
        "supersedes": "[]",
        "superseded_by": "[]",  # we run OCI, not GCP
    },
    "infrastructure_deep_dive.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/infrastructure/spec.md]",
    },
    "machine_learning_deep_dive.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/oideachais-pipeline/spec.md, openspec/specs/data-pipeline/spec.md]",
    },
    "package-updates.md": {
        "supersedes": "[]",
        "superseded_by": "[]",  # the only plan with substantive content
    },
    "tangent_1_micro_credentials.md": {
        "supersedes": "[]",
        "superseded_by": "[docs/00-deploy-plans/01-micro-credentials.md]",
    },
    "tangent_2_generative_tutoring.md": {
        "supersedes": "[]",
        "superseded_by": "[docs/00-deploy-plans/02-generative-tutoring.md]",
    },
    "tangent_3_automated_assessment.md": {
        "supersedes": "[]",
        "superseded_by": "[docs/00-deploy-plans/03-automated-assessment.md]",
    },
    "tangent_4_immersive_content.md": {
        "supersedes": "[]",
        "superseded_by": "[docs/00-deploy-plans/04-immersive-content.md]",
    },
    "tangent_5_policy_simulator.md": {
        "supersedes": "[]",
        "superseded_by": "[docs/00-deploy-plans/05-policy-simulator.md]",
    },
    "web_and_dashboards_deep_dive.md": {
        "supersedes": "[]",
        "superseded_by": "[openspec/specs/frontend-frameworks/spec.md, docs/05-web/frontend-topology.md]",
    },
}


def add_frontmatter(path: Path) -> bool:
    """Add frontmatter to `path`. Returns True if it changed."""
    name = path.name
    if name == "STATUS.md":
        return False  # already has its own
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        return False  # already has frontmatter
    status = "deferred" if name in DEFERRED else "research"
    meta = META.get(name, {"supersedes": "[]", "superseded_by": "[]"})
    title = name.replace("_", " ").replace(".md", "").title()
    frontmatter = (
        "---\n"
        f"title: '{title}'\n"
        f"status: {status}\n"
        f"supersedes: {meta['supersedes']}\n"
        f"superseded_by: {meta['superseded_by']}\n"
        f"last_touched: 2026-06-13\n"
        "---\n\n"
    )
    path.write_text(frontmatter + text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for plan in sorted(PLANS_DIR.glob("*.md")):
        if add_frontmatter(plan):
            changed += 1
            print(f"  + frontmatter: {plan.name}")
    print(f"added frontmatter to {changed} plans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
