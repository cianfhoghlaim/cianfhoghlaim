---
title: 'Deploy Plan 05 — Cross-Border Policy Impact Simulator'
domain: deploy-plan
status: draft
description: 'Temporal-diff CrossNationCurriculumSpec across NCCA/CCEA/DfE/SQA/Welsh Gov, with Cognee knowledge-graph ripple-effect simulation and a Marimo dashboard for what-if policy exploration.'
read_when:
  - 'designing temporal/versioned curriculum data'
  - 'building what-if simulators over the knowledge graph'
  - 'extending BAML schemas for diff extraction'
supersedes: []
superseded_by: []
related_specs:
  - oideachais-pipeline
  - knowledge-graph
  - workflow-automation
related_apps:
  - sruth/oideachais/dagster_defs
  - sruth/meaisinfhoghlaim/agents/simulator
  - sruth/oideachais/notebooks
related_llm_stack:
  - 'BAML (diff extraction + ripple annotation)'
  - 'litellm (BAML→model routing)'
  - 'Cognee (knowledge graph + temporal queries)'
truth: sole
last_touched: 2026-06-13
---

# Deploy Plan 05 — Cross-Border Policy Impact Simulator

## 0. Why this plan

Replace the original Tangent 5 framing (which named the simulator
"Policy Impact Simulator" without anchoring to the existing data
platform) with a deploy plan grounded in the **DuckLake temporal
versioning** and **Cognee knowledge graph** that already exist. The
goal is a simulator that:

1. **Versions** every `CrossNationCurriculumSpec` row (8 nations, 7
   kinds — see Deploy Plan 01 §2.1) with strict monotonic timestamps
   and semantic versions.
2. **Diffs** the versions with BAML-extracted semantic embeddings +
   structural changes.
3. **Simulates ripple effects** on the prerequisite knowledge graph
   (Cognee).
4. **Visualises** the simulation in a Marimo dashboard with a
   what-if playground.

This is *pure data + analysis*. No political framing, no specific
endorsement.

## 1. Monorepo grounding

| Asset | Path | Use |
|:--|:--|:--|
| Quadrant | `sruth/oideachais/` | DLT sources, Dagster pipeline, DuckLake versioning |
| Quadrant | `sruth/meaisinfhoghlaim/` | LLM stack, simulator agent |
| Skill | `.agents/skills/dlt/SKILL.md` | Incremental loading, cursor-based |
| Skill | `.agents/skills/dagster/SKILL.md` | SDA + partitions + sensors |
| Skill | `.agents/skills/cognee/SKILL.md` | Temporal knowledge graph |
| Skill | `.agents/skills/baml/SKILL.md` | Diff extraction |
| Skill | `.agents/skills/marimo/SKILL.md` | Dashboard |

The 5-quadrant topology is in `docs/00-core/CLAUDE.md` §QUADRANT_MAP.

## 2. Versioned `CrossNationCurriculumSpec`

The cross-border equivalence work (Deploy Plan 01) produces
`EquivalenceAssertion` rows. We extend that schema with two temporal
fields:

```baml
class CrossNationCurriculumSpec {
  // ... existing fields from Deploy Plan 01 ...
  spec_version string                       // semver: "ROI-NC-2024-Q1"
  valid_from timestamp
  valid_to timestamp?                      // null = current
  supersedes string?                        // id of the prior spec
  change_kind ChangeKind                    // "initial" | "amendment" | "replacement"
  source_url string                         // canonical URL of the spec document
  source_published_at timestamp
}

enum ChangeKind {
  Initial
  Amendment                            // small edits
  Replacement                          // full new spec
  Deprecation                          // valid_to set, no replacement yet
}
```

Every DLT source appends a new row on update; nothing is mutated in
place. The DuckLake table
`motherduck.oideachais_equivalence.cross_nation_curriculum_spec` is
**append-only** with `(spec_version, valid_from)` as the temporal
primary key.

## 3. Diff extraction (BAML)

The diff between two consecutive spec versions is itself a BAML-typed
object:

```baml
class SpecDiff {
  from_version string
  to_version string
  outcome_diffs OutcomeDiff[]
  new_outcomes LearningOutcome[]            // first appearance
  removed_outcomes string[]                 // ids no longer present
  prerequisite_changes PrereqChange[]
  terminology_changes BilingualTermDiff[]
  summary_en string                         // BAML-generated plain-English
  ripple_risk_score float                   // 0..1 (BAML)
}

class OutcomeDiff {
  outcome_id string
  field string                              // "description" | "bloom_level" | "prerequisites" | "level"
  before string
  after string
  semantic_shift float                      // 1 - cosine similarity
}

class PrereqChange {
  outcome_id string
  added_prereqs string[]
  removed_prereqs string[]
  net_effect string                         // "tightens" | "loosens" | "shifts"
}

class BilingualTermDiff {
  term_en string
  before_target string?
  after_target string?
  source_before string?                     // "téarma.ie 2023"
  source_after string?                      // "téarma.ie 2024"
}
```

The diff extractor runs as a Dagster sensor: when a new
`CrossNationCurriculumSpec` lands, the sensor computes the diff vs
the prior version and emits a `SpecDiff` row to
`motherduck.oideachais_equivalence.spec_diff`.

## 4. Ripple-effect simulation (Cognee)

The Cognee knowledge graph (from Deploy Plan 02) holds:
- `LearningOutcome` nodes (with embeddings)
- `Prerequisite` edges (typed: "hard" | "soft" | "suggested")
- `BilingualTerm` nodes (linked to outcomes)

For each `SpecDiff`, the simulator:

1. **Updates** the affected nodes in the graph.
2. **Runs** a BFS/PageRank-style traversal from each changed outcome
   to find the **downstream** outcomes that depend on it.
3. **Computes** a ripple risk per downstream outcome:
   - 0.0 = no impact (the change is in a leaf concept)
   - 1.0 = critical impact (the change touches a KS4 / A-Level root)
4. **Annotates** each ripple with a BAML-generated
   "consequence description" in plain English.

The result is a `RippleSimulation` row in
`motherduck.oideachais_equivalence.ripple_simulation`.

## 5. What-if playground (Marimo dashboard)

The dashboard at `sruth/oideachais/notebooks/policy_simulator.py` exposes:

| Section | Controls | Output |
|:--|:--|:--|
| **Spec timeline** | Date range slider, nation filter | Timeline view of all `CrossNationCurriculumSpec` versions |
| **Diff inspector** | Spec pair selector | Side-by-side BAML-extracted diff |
| **What-if toggle** | "Add outcome X to KS3 Computing (UK)" toggle | Live re-run of ripple simulation |
| **Adoption heatmap** | Nation × subject grid | Color-coded volatility (number of `SpecDiff` rows / year) |
| **Cross-border lag** | Topic filter | Time delta between nations adopting the same topic |

The dashboard is published as a MotherDuck Dive per
`docs/05-web/frontend-topology.md` §5 and embedded in the policy team
workspace at `sruth/oideachais/web/routes/policy/index.tsx`.

## 6. Sensor + schedule wiring (Dagster)

```python
@sensor(job=policy_diff_job, minimum_interval_seconds=86400)
def spec_version_published_sensor(context):
    """Trigger a diff + ripple when a new spec lands in DuckLake."""
    new_specs = ducklake.scan("oideachais_equivalence.cross_nation_curriculum_spec") \
        .filter(pl.col("valid_from") > pl.col("max_seen_valid_from")) \
        .collect()
    for spec in new_specs.iter_rows(named=True):
        yield RunRequest(
            run_key=f"diff::{spec['spec_id']}::{spec['spec_version']}",
            run_config={...},
        )

@schedule(job=policy_volatility_job, cron_schedule="0 0 1 1 *")
def monthly_volatility_schedule():
    """Re-compute cross-border adoption lag monthly."""
    ...
```

The sensor is registered in
`sruth/oideachais/dagster_defs/sensors/policy_diff_sensor.py` (new file).

## 7. Phased action plan

| Phase | Scope | Exit criteria |
|:--|:--|:--|
| 0 | Append-only DuckLake table for `CrossNationCurriculumSpec` | DLT source for NCCA + DfE + CCEA backfilled with 5 years of history |
| 1 | BAML `SpecDiff` extractor | 90% precision on a 10-version gold set |
| 2 | Cognee ripple-simulation engine | Ripple detection matches 5 human expert reviews |
| 3 | Dagster sensor + monthly schedule | Daily diffs + monthly volatility recompute |
| 4 | Marimo dashboard | 3 ministry users complete a what-if analysis |
| 5 | Public release (gated) | The dashboard is accessible via Pocket ID OIDC |

## 8. Risks and mitigations

| Risk | Mitigation |
|:--|:--|
| Spec documents change format between versions | BAML extractor is per-source; a versioning change triggers a re-prompt cycle |
| Ripple simulation misleads policy makers | All ripples are marked `confidence`; the dashboard shows the confidence band |
| Source document removal (404) | Wayback Machine mirror stored in Iceberg (per `docs/02-data-platform/storage-mental-model.md`) |
| Cross-border lag is too coarse | We use the *first-detection date* per nation, not the official publication date |

## 9. Out of scope (deferred)

- Predicting future spec changes (LLM-based speculation) — v3
- Cross-jurisdictional causal inference (statistics) — v2
- Policy-team workflow automation (Vikunja integration) — v2

## 10. Cross-references

- `docs/00-core/CLAUDE.md` — 5-quadrant topology
- `docs/02-data-platform/storage-mental-model.md` — DuckLake + Iceberg
- `docs/02-data-platform/cross-domain-registry.md` — `sruth/oideachais/sources.yaml`
- `docs/03-agents/change-detection.md` — DLT incremental + ChangeDetection.io
- `docs/04-ai-ml/llm-stack-hierarchy.md` — BAML + litellm + Cognee
- `docs/05-web/frontend-topology.md` — Marimo Dive delivery
- `openspec/specs/oideachais-pipeline/spec.md`
- `openspec/specs/knowledge-graph/spec.md`
- `openspec/specs/workflow-automation/spec.md` — Vikunja + n8n
- `.agents/skills/dlt/SKILL.md`
- `.agents/skills/dagster/SKILL.md`
- `.agents/skills/cognee/SKILL.md`
- `.agents/skills/baml/SKILL.md`
- `.agents/skills/marimo/SKILL.md`
- `infrastructure/stacks/changedetection/` — sitemap sensor (deployed on `arm1-oci`)
