# Cross-repo sync: 2026-09-23-consolidate-uog-tertiary-pipeline-v1

This change touches **3 repos**: `cianfhoghlaim` (the umbrella
archive) + `ciandlithe` (the removal change) + `github.com/cianfhoghlaim/ollscoil-na-gaillimhe` (deletion via the GitHub API).

## Files touched

### `cianfhoghlaim/` (this repo — receives everything)

| Path | Change |
|:--|:--|
| `dlt_sources/british_isles/ireland/university/` → `tertiary/` | rename |
| `baml_src/british_isles/ireland/education/university/` → `baml_src/british_isles/ireland/tertiary/` | rename |
| `dlt_sources/british_isles/ireland/tertiary/uog/` (15 files) | NEW (14 DLT sources + 1 base + 1 `__init__.py`) |
| `baml_src/british_isles/ireland/tertiary/` (8 files) | NEW (1 refactored + 3 from KCG + 4 new) |
| `cocoindex_flows/british_isles/ireland/tertiary/uog/` (10 files) | NEW |
| `agents/meaisinfhoghlaim/educational/students_union/` (14 files) | NEW (moved from ciandlithe) |
| `agents/uoa_portal/` (6 files) | NEW |
| `bonneagar/stacks/{regexam-nuig,canvas-nuig,uo-portal-vault}/` (3 × 6 = 18 files) | NEW |
| `notebooks/_shared/tertiary/` (25 files) | NEW |
| `orchestration/defs/1_ingestion/tertiary/uog/` (14 files) | NEW |
| `orchestration/defs/2_materials/tertiary/uog/` (14 files) | NEW |
| `orchestration/defs/3_model_lifecycle/tertiary/uog/` (3 files) | NEW |
| `orchestration/defs/4_asset_generation/tertiary/uog/` (10 files) | NEW |
| `orchestration/defs/5_agent_ops/tertiary/uog/` (5 files) | NEW |
| `openspec/specs/cianfhoghlaim-tertiary-pipeline/spec.md` | NEW |
| `openspec/specs/retire-kcg-sister-repo/spec.md` | NEW |
| `openspec/specs/extract-students-union-from-ciandlithe/spec.md` | NEW |
| `dlt_sources/common/site_crawler.py` | MODIFIED (+4 ScrapePolicy rows) |
| `mise.toml` | MODIFIED (+5 namespace aliases) |
| `agents/agent_registry.py` | MODIFIED (register SU root as 13th specialist) |
| `openspec/AGENTS.md` | MODIFIED (priority specs table) |
| `openspec/specs/british-isles-education-pipeline-v3/spec.md:698` | MODIFIED (stage taxonomy rename) |
| `openspec/specs/cianfhoghlaim-university-deep-extraction/spec.md` | MODIFIED (DEPRECATED notice) |
| `orchestration/defs/4_budget/firecrawl_budget_asset.py` | MODIFIED (+4 budget rows) |
| `orchestration/partitions.py` | MODIFIED (+1 partition) |
| `meaisinfhoghlaim/models/model_registry.py` | MODIFIED (+2 models) |
| `meaisinfhoghlaim/models/registry.py` | MODIFIED (OCRAwareSelection rule) |
| `baml_src/_shared/provider_router.py` | MODIFIED (+uoa_portal BAML client) |
| `baml_src/clients.baml` | MODIFIED (+2 clients) |
| `scripts/cognee_ingest_uoa_portal.py` | NEW |
| `scripts/osint_allowlists/ireland_tertiary.yaml` | NEW (from KCG) |
| `scripts/lint_osint_allowlists.py` | MODIFIED (extended for all 8 jurisdictions) |
| `tests/tertiary/test_uog_smoke.py` | NEW (from KCG) |
| `tests/agents/students_union/test_smoke.py` | NEW (from ciandlithe) |
| `.agents/skills/uoa-tertiary-pipeline/SKILL.md` | NEW |
| `agents/meaisinfhoghlaim/AGENTS.md` | MODIFIED (per-area routing) |
| `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` | MODIFIED (+2 actions) |
| `opencode.json` | MODIFIED (+2 agents registered) |

### `ciandlithe/` (sister repo — deletes the SU package)

Open `openspec/changes/<YYYY-MM-DD>-remove-students-union-from-ciandlithe-v1/` (separate openspec change in ciandlithe) which deletes:

- `agents/adk/students_union/` (entire dir)
- `notebooks/students_union_adk_case_studies.py`
- `notebooks/students_union_kcg_integration.py`
- `openspec/specs/ciandlithe-adk-students-union/spec.md`
- `mise.toml` lines ~330-336 (3 SU-related mise tasks)
- Updates to `README.md` + `AGENTS.md` + `LICENSE.md` (remove SU references)

### `github.com/cianfhoghlaim/ollscoil-na-gaillimhe` (deletion via GitHub API)

```bash
gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe --yes
# Expected: returns 204
```

After the deletion, the local mirror at `~/dev/kings_college_galway/` is also removed:

```bash
rm -rf ~/dev/kings_college_galway
ls ~/dev/kings_college_galway
# Expected: No such file or directory
```

## Order of operations

Per the openspec/AGENTS.md convention at line 281, the 3 repos MUST be committed/archived in this order:

```
1. cianfhoghlaim:    commit + archive the umbrella change (creates the receiving locations)
2. ciandlithe:       commit + archive the removal change (deletes the SU code from ciandlithe)
3. GitHub API:       gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe (retires the KCG sister)
4. Local:            rm -rf ~/dev/kings_college_galway
```

The ciandlithe removal change is opened AFTER the cianfhoghlaim umbrella
change is archived (so the receiving locations exist) but committed
in the SAME git push window (so the cross-repo import paths in
ciandlithe's downstream code resolve to the cianfhoghlaim location).

## Soft dependencies

- `pipeline-sister-repo-handoff` (the umbrella sister-handoff change)
  — provides the cross-repo orchestration mirror
- `pipeline-naming-taxonomy` — establishes the `university/` →
  `tertiary/` rename law
- `centralized-schema-registry` — establishes the BAML-is-source-of-
  truth contract that the 4-tier schema consolidation follows

## Verification (pre-archive)

```bash
cd ~/dev/cianfhoghlaim
git grep kings_college_galway    # 0 matches
git grep ollscoil-na-gaillimhe   # 0 matches
git grep "uog_pipeline_base"     # 0 matches
git grep students_union          # only in updated README/AGENTS/LICENSE pointers
openspec validate 2026-09-23-consolidate-uog-tertiary-pipeline-v1 --strict   # exit 0
```
