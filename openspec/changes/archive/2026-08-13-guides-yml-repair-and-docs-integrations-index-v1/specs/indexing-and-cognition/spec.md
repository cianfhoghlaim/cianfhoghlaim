# indexing-and-cognition — Change 2 Delta (2026-08-13)

## ADDED Requirements

### Requirement: .cocoindex_code/guides.yml entries SHALL resolve to real on-disk paths

The system MUST keep every entry in
`.cocoindex_code/guides.yml` (loaded by `ccc` at search
time to surface concept-guide hits alongside semantic-search
results) pointing at paths that resolve on disk in the
repository.

A new validation gate `mise run lint:guides-yml`
(implemented by `scripts/lint_guides_yml.py`) MUST walk
every entry in the YAML file, extract the `files:` list,
and emit a JSON report to
`stedding/sync-reports/guides-yml-{date}.json` containing
the per-entry pass/fail status. The gate MUST exit 1 if
any entry contains a path that does not resolve on disk.

The linter MUST also handle directory paths (e.g.
`orchestration/defs/1_ingestion/` resolves to a directory,
not a file) without failing.

#### Scenario: A new guide entry is added with a stale path

- **GIVEN** an operator adds a new entry to
  `.cocoindex_code/guides.yml` that references
  `docs/04-ai-ml/ocr-htr.md` (a path that no longer exists
  post-v7 flattening)
- **WHEN** the operator runs `mise run lint:guides-yml`
- **THEN** the script MUST exit 1
- **AND** the JSON report MUST list the entry as failed
  with the specific missing path
- **AND** the operator MUST either fix the path or remove
  the entry before the change can be merged

#### Scenario: A stale guide entry survives a refactor

- **GIVEN** a `.cocoindex_code/guides.yml` entry references
  a path that has been moved or deleted (e.g. the
  `docs/01-cognee/README.md` paths that were absorbed into
  `.agents/skills/INDEXING_AND_COGNITION.md`)
- **WHEN** `ccc search` is run with a query that matches
  the entry's description
- **THEN** the user MUST NOT receive a [guide] hit that
  points at a non-existent file
- **AND** `mise run lint:guides-yml` MUST catch the stale
  path before the next commit
- **AND** the entry MUST be rewritten to point at the
  canonical new home

### Requirement: docs/INTEGRATIONS_INDEX.md SHALL map every legacy docs/0X-*/ topic to its new home

A `docs/INTEGRATIONS_INDEX.md` file MUST exist at the
`docs/` directory root and serve as the single
"where did `docs/0X-*/` go?" router. The file MUST map
every legacy `docs/0X-*/` topic (e.g. "Cognee knowledge
graph", "OCR/HTR", "Celtic language", "Frontend stack")
to its canonical new home (a `.agents/skills/<skill>/SKILL.md`
file, a per-area `AGENTS.md`, or an openspec spec).

The mapping MUST be a single table that is human-readable
AND parseable by agents. The file MUST NOT duplicate
content — it MUST be a pure index.

#### Scenario: New agent searches for a legacy topic

- **GIVEN** a new agent asks "where is the old
  `docs/01-cognee/README.md`?" or "how do I find OCR/HTR
  documentation?"
- **WHEN** the agent searches for "cognee" or "OCR HTR"
  or reads `docs/INTEGRATIONS_INDEX.md`
- **THEN** the agent MUST find the canonical new home
  (e.g. `.agents/skills/INDEXING_AND_COGNITION.md` or
  `.agents/skills/centralized-registry/SKILL.md` §11)
  within the first 5 search results or the first row of
  the mapping table
- **AND** the file MUST cross-reference both the legacy
  topic and the new home