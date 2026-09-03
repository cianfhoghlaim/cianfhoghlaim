# 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1

## Why

The `.cocoindex_code/guides.yml` file (loaded by `ccc` at
search time to surface concept-guide hits alongside
semantic-search results) contains **26 entries**. Of those,
**18 reference at least one dead path** — paths that were
renamed or deleted during the v4 → v7 flattening cycles.
The current state (verified 2026-08-13):

| Dead path prefix | Dead paths referenced | New home |
|:--|--:|:--|
| `docs/01-cognee/` | 7 | `.agents/skills/cognee/SKILL.md` + `.agents/skills/INDEXING_AND_COGNITION.md` |
| `docs/01-platform-architecture/` | 6 | `.agents/skills/secrets-management/SKILL.md` + `.agents/skills/komodo/SKILL.md` + `.agents/skills/pangolin/SKILL.md` + `bonneagar/AGENTS.md` |
| `docs/02-data-platform/` | 3 | `dlt_sources/DATA_PLATFORM_ROUTER.md` (new in Change 1) + `dlt_sources/AGENTS.md` + `orchestration/AGENTS.md` + `motherduck/README.md` |
| `docs/03-agents/` | 4 | `.agents/skills/agent-fleet-orchestration/SKILL.md` + `.agents/skills/google-adk/SKILL.md` + `agents/AGENTS.md` |
| `docs/04-ai-ml/` | 7 | `.agents/skills/centralized-registry/SKILL.md` (§11 OCR/VLM, from Change 1) + `meaisinfhoghlaim/README.md` |
| `docs/05-web/` | 3 | `.agents/skills/agentic-frontend-frameworks/SKILL.md` + `web/apps/AGENTS.md` |
| `docs/06-product/` | 4 | `openspec/specs/british-isles-education-pipeline/spec.md` + `agents/meaisinfhoghlaim/AGENTS.md` |
| `docs/02-architecture/` | 3 | `agents/meaisinfhoghlaim/AGENTS.md` + `agents/tuatha/AGENTS.md` |
| `docs/05-celtic-language/` | 5 | `openspec/specs/celtic-language-pipeline/spec.md` |
| `docs/02-audit/` | 5 | `docs/audits/` + `docs/audit/` |
| `docs/01-patterns/` | 6 | per-area `.agents/skills/<skill>/SKILL.md` files |
| `docs/03-pipelines/` | 8 | `orchestration/AGENTS.md` + `dlt_sources/DATA_PLATFORM_ROUTER.md` |
| `docs/07-standards/` | 2 | `AGENTS.md` (root) + `.agents/skills/dignified-python/SKILL.md` |
| `docs/08-examples/` | 8 | `openspec/changes/` + `.agents/skills/` |
| `docs/07-skills/` | 9 | `.agents/skills/<skill>/SKILL.md` (61 real skills — no longer needs a `docs/07-skills/` mirror) |
| `doc/hackathons/` | 3 | `docs/research/` + `docs/legacy/cianfhoghlaim-pkg-readme.md` |
| `docs/CLAUDE.md`, `docs/PROJECT_SPEC.md`, `docs/CONSTRAINTS.md`, `docs/AGENTS.md` | 4 | root-level `AGENTS.md` + `openspec/AGENTS.md` |

Plus 7 additional missing paths in entries 17-26 (the
"openspec archive search", "dagster-asset-graph",
"baml-function-search", "stack-catalog-search",
"dlt-source-search", "agent-fleet-search",
"notebook-search" entries) — paths that were correct at
the time of authoring but have since been renamed
(e.g. `agents/tuatha/agents/math_agent.py` →
`agents/meaisinfhoghlaim/educational/`; `notebooks/26_baml_sync_dashboard.py` → `notebooks/26_aistear_dashboard.py`).

**Net effect today:** roughly 50% of the CCC concept-guide
hits point at dead paths, so CCC search returns stale
documentation that no longer exists.

## What Changes

### A. Rewrite `.cocoindex_code/guides.yml` (all 26 entries)

**MODIFIED** `.cocoindex_code/guides.yml` — every entry's
`files:` list is replaced with paths that actually exist on
disk. The 14 entries that already point at real files are
polished (description + tags + domain updated to reflect
the current repo surface). The 12 entries that pointed at
the dead `docs/0X-*/` directories are redirected to the
canonical new homes.

New domain taxonomy (replaces the old `0X-` numbered
domains with the post-v7 surface):

| Domain | Replaces |
|:--|:--|
| `00-openspec` | (unchanged) |
| `00-core` | `00-core` |
| `01-cognee` | `01-cognee` (now via INDEXING_AND_COGNITION.md) |
| `01-platform-architecture` | `01-platform-architecture` (now via bonneagar/AGENTS.md) |
| `01-data-platform` | `02-data-platform` (now via DATA_PLATFORM_ROUTER.md) |
| `02-agents` | `03-agents` (now via agent-fleet-orchestration) |
| `02-ai-ml` | `04-ai-ml` (now via centralized-registry §11) |
| `02-web` | `05-web` (now via agentic-frontend-frameworks) |
| `03-celtic` | `05-celtic-language` (now via celtic-language-pipeline spec) |
| `04-product` | `06-product` (now via british-isles-education-pipeline spec) |
| `05-iac` | `06-iac` (unchanged) |
| `05-audit` | `02-audit` (now via docs/audit + docs/audits) |
| `05-patterns` | `01-patterns` (now via per-area skills) |
| `06-standards` | `07-standards` (now via root AGENTS.md) |
| `07-examples` | `08-examples` (now via openspec/changes/) |
| `08-baml` | `00-baml` (unchanged) |
| `08-dlt` | `00-dlt` (unchanged) |
| `08-agents` | `00-agents` (unchanged) |
| `08-notebooks` | `00-notebooks` (unchanged) |
| `09-hackathons` | `09-hackathons` (now via docs/research/) |

### B. Create `docs/INTEGRATIONS_INDEX.md`

**NEW** `docs/INTEGRATIONS_INDEX.md` — the top-level
"where did `docs/0X-*/` go?" router. Single file that maps
every legacy `docs/0X-*/` topic to its new home (skill /
AGENTS.md / openspec spec). Pure index — no content
duplication. ~200 lines.

Sections:
1. **The 5 dead `docs/0X-*/` directories** — list + status
2. **The 4 surviving `docs/` subdirectories** — `audit`,
   `audits`, `legacy`, `plans`, `research`, etc.
3. **Topic-by-topic mapping table** — for each legacy
   topic (e.g. "cognee knowledge graph", "OCR/HTR",
   "Celtic language", "frontend stack") → new home
4. **For agents** — quick routing instructions

### C. Add `mise run lint:guides-yml` validation gate

**MODIFIED** `mise.toml` — add a new task:

```toml
[tasks."lint:guides-yml"]
description = "Validate every path in .cocoindex_code/guides.yml resolves on disk. Exits 1 if any path is missing; writes JSON report to stedding/sync-reports/guides-yml-{date}.json. Per the 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1 change."
run = "uv run python scripts/lint_guides_yml.py"
```

**NEW** `scripts/lint_guides_yml.py` — the linter script.
Walks every entry in `.cocoindex_code/guides.yml`,
extracts the `files:` list, and checks each path resolves
on disk (or matches an existing directory). Emits a JSON
report + exits 1 if any path is missing.

### D. Spec delta to `indexing-and-cognition`

**ADDED Requirement** in
`openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/specs/indexing-and-cognition/spec.md`.
See sibling `specs/indexing-and-cognition/spec.md` in
this change.

## Dependencies

`Blocked by: 2026-08-13-skill-consolidation-and-extension-v1`
(needs the `dlt_sources/DATA_PLATFORM_ROUTER.md` path for
the `02-data-platform` guides.yml rewrite).

`Blocks`:
- `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1`
  (Change 3) — needs Change 2's stable guides.yml before
  re-baselining count claims in INDEXING_AND_COGNITION.md.

`Affected repos: cianfhoghlaim` (single-repo change)

## Out of scope (intentionally)

- The 55 deprecated skills in `.agents/skills_backup/` —
  left alone per the user's instruction.
- The `sruth/` directory leftovers — preserved as
  historical pattern references per the user's instruction.
- `ccc` skill deletion — still needed for the CLI shortcuts.
- Re-architecting the CCC indexing pipeline itself — this
  change only repairs the `guides.yml` content, not the
  CCC indexing engine.

## Verification

```bash
# 1. New validation gate passes
mise run lint:guides-yml
# Expected: "All 26 guides have valid paths"

# 2. openspec validation
openspec validate 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1 --strict
# Expected: "Change is valid"

# 3. CCC search verification (sample)
bun run ccc:search "Cognee knowledge graph"
bun run ccc:search "OCR VLM pipeline"
bun run ccc:search "data platform"
bun run ccc:search "stack catalog"
# Expected: All return real, indexed files

# 4. Spot-check guides.yml content
grep -c "^  - " .cocoindex_code/guides.yml
# Expected: 26 entries
grep -c "MISSING\|docs/01-cognee\|docs/01-platform" .cocoindex_code/guides.yml
# Expected: 0

# 5. INTEGRATIONS_INDEX.md exists
test -f docs/INTEGRATIONS_INDEX.md && echo "OK"

# 6. Drift lint (no new drift)
mise run lint:drift-docs --dry-run
# Expected: same 7 pre-existing violations, no new ones

# 7. Skill metadata lint
mise run lint:skills
# Expected: 61/61 pass
```