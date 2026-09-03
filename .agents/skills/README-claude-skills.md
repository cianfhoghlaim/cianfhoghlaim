# `.claude/skills/`

Two kinds of skills live here:

1. **31 vendored dltHub AI Workbench skills** (`add-table`, `create-rest-api-pipeline`, `explore-data`, etc.) — checked in directly, not symlinks. These come from the `dlthub-ai-workbench` toolkit.
2. **39 symlinks into `.agents/skills/`** — this project's own 66 technology skills, curated to the subset matching the live stack, added 2026-08-19 so Claude Code can discover them (it does not read `.agents/skills/` on its own).

`.agents/skills/` (66 dirs) stays the single source of truth — nothing was copied, only linked. To expose another skill to Claude Code:

```bash
ln -s ../../.agents/skills/<name> .claude/skills/<name>
```

**Not linked**: `_template` (not a real skill); `dlthub-router`, `improve-skills`, `setup-secrets` (name collisions with the vendored dltHub toolkit skills already at this level — the vendored ones are canonical for dlt pipeline work); the `*-sync` layer skills (`agents-sync`, `baml-schema-sync`, `dagster-asset-sync`, `dlt-sync`, `notebooks-sync`, `stacks-sync`, `change-detection`, `knowledge-sync-loop` — internal drift-detection tooling, not something Claude typically needs mid-task); niche/narrow ones (`ag-ui`, `apple-photos-ingestion`, `babylonjs`, `crawl4ai`, `firecrawl-cli`, `huggingface`, `modal`, `pydantic`, `risingwave`, `schema-codegen`, `unsloth`); `copilotkit` (a 10-sub-skill vendor bundle with no single top-level `SKILL.md` — link a specific sub-skill under `.agents/skills/copilotkit/skills/<name>/` if you need one).

If you need one of the excluded skills, symlink it the same way.
