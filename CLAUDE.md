@AGENTS.md

## New in 2026-08-23-uog-personal-archive-tertiary-modules-v1 (UoG personal archive → tertiary subject pipeline)

Lifts `leabharlann/ollscoil_na_gaillimhe/` + transcript PDFs to
feature parity with the leaving-cycle subject pipeline via a new
DLT source, BAML schema, 4 CocoIndex v1 Apps, 10 typed Cognee edges,
6 Dagster assets, an 8-tab Marimo notebook, Convex + CopilotKit +
Genie + ADK, plus tests + observability + thesis figures.

**Pipeline at a glance:**

```
leabharlann/ollscoil_na_gaillimhe/          DLT filesystem scan
  mata/                                     (auto-detect module_code
  software_development/                      + artefact_kind + provenance
  irish/                                     from folder path + filename)
  past/                                   → _classify_file()
                                           → 8 dlt.resources
                                             + HTR ensemble for handwriting
cian_mac_an_déisigh_uí_liatháin/           → 7 BAML functions
  achievement/*transcript*.pdf               (artefact/assignment/question/topic/
                                             reading-list/code-cell/transcript)
                                           → 9 DuckLake tables
                                             + rollup (1 row / module)
                                           → 4 CocoIndex v1 Apps
                                             (artefacts/questions/topics/lecture-notes)
                                           → 10 Cognee typed edges
                                             (incl. cross-module Topic-RELATED_TO-Topic)
                                           → 6 Dagster assets
                                             (stage0_audit → duckdb_sink)
                                           → 8-tab Marimo notebook
                                             + CS4423 worked-example sidebar
                                           → Convex chat + CopilotKit + Genie + ADK
```

**Configurable via 9 env vars** in `.env.example`:

| Var | Default |
|---|---|
| `UNIVERSITY_PERSONAL_ARCHIVE_PATH` | `leabharlann/ollscoil_na_gaillimhe` |
| `UNIVERSITY_REGISTRY_URL` | `https://www.universityofgalway.ie` |
| `UNIVERSITY_NAME` | `University of Galway` |
| `UNIVERSITY_INSTITUTION_ID` | `ie-university-galway` |
| `UNIVERSITY_PROGRAMME_CODE_REGEX` | `[A-Za-z]{2,3}\d{3,4}` |
| `UNIVERSITY_TRANSCRIPT_FILE_PATTERNS` | `*transcript*.pdf` |
| `UNIVERSITY_ASSIGNMENT_FILE_PATTERN` | `*assignment*.pdf` |
| `UNIVERSITY_LECTURE_NOTES_DIR_PATTERN` | `*Lectures*` |
| `DUCKLAKE_DESTINATION` | `local` |

**Quickstart:**

```bash
# Run the personal-archive pipeline end-to-end
mise run dagster:launch uog_personal_archive_stage0_audit
mise run dagster:launch uog_personal_archive_stage1_collect
mise run dagster:launch uog_personal_archive_baml_extract
mise run dagster:launch uog_personal_archive_typed_join
mise run dagster:launch uog_personal_archive_embed_lance
mise run dagster:launch uog_personal_archive_duckdb_sink

# Open the 8-tab Marimo notebook
marimo edit notebooks/15_personal_archive.py

# Run the test suite (12 tests, all passing)
uv run pytest tests/personal_archive/ -v

# Validate the openspec change
uv run openspec validate 2026-08-23-uog-personal-archive-tertiary-modules-v1 --strict
```

## Claude Code specifics

- **`.claude/` is gitignored** — it's a per-developer `dlthub ai` toolkit
  artifact, regenerated on each fresh clone (see the comment above the
  `/.claude/` rule in `.gitignore`). Nothing under it persists via git.
- This repo's own 66 technology skills live in `.agents/skills/`
  (tracked). Run `bash scripts/wire-claude-skills.sh` once per clone to
  symlink a curated ~39-skill subset into `.claude/skills/` so Claude
  Code can discover them — see `.agents/skills/README-claude-skills.md`
  for the curation rationale and how to add more. Safe to re-run after
  any `.claude/` regeneration.
- `.claude/rules/*.md` (the 10 vendored dltHub toolkit workflow rules)
  have `paths:` frontmatter added locally so they only load when
  working in `dlt_sources/`/`dlthub-ai-workbench/`, not every session.
  **This does not persist** — the tracked source is
  `dlthub-ai-workbench/workbench/<toolkit>/rules/workflow.md` (a
  vendored upstream package), and re-installing a toolkit will
  overwrite the local copy without the frontmatter. Patching the
  vendored templates themselves was judged out of scope (risks
  diverging from upstream on re-sync) — re-apply the `paths:` block
  after any `dlthub ai toolkit install` if you want the scoping back.
- Prefer `mise run ccc:search "<query>"` over `grep`/`find` for
  code search — see the `ccc` skill.
