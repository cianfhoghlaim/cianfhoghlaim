---
title: docs-v2 Migration Guide
status: living-document
description: How merged files are structured; how to read them; current state
---

# docs-v2 Migration Guide

`docs-v2/` is a per-topic merged mirror of `docs/`. Every file in `docs-v2/`
follows the same structure so that the **original sources remain attributable**
and **no information is lost**.

## Current state (as of 2026-06-13)

| Metric | Value |
|:--|:--|
| `docs/` source files | 11,776 |
| `docs-v2/` target files | 6,970 (66 .md + 6,504 non-md + 400 misc) |
| Reduction | 41% fewer files |
| `docs/` size | 503 MB |
| `docs-v2/` size | 446 MB |
| `docs-v2/` is in `.gitignore` | yes (regenerated, not tracked) |

## What lives where

- **`docs-v2/00_index.md`** — regenerated routing table
- **`docs-v2/01-platform-architecture/...`** through **`09-cognee/`** — 9 canonical domains; each contains topic-clustered merged `.md` files
- **`docs-v2/10-loose-files/`** — 9 loose top-level files
- **`docs-v2/11-scripts/`** — `.py`, `.ts`, `.js`, `.sh` source code
- **`docs-v2/12-configs/`** — `.yaml`, `.toml`, `.json` config files
- **`docs-v2/13-images/`** — `.png`, `.jpg`, `.svg` images
- **`docs-v2/.migration/`** — coverage.json, manifests, validation, search samples
- **`docs-v2/MIGRATION.md`** — this file
- **`docs-v2/changelog.md`** — per-commit coverage statistics

## Section structure (each merged .md)

```markdown
---
title: <topic>
domain: <NN-domain>
status: living-document
description: <one-line summary>
merged_on: YYYY-MM-DD
merged_from_count: N
supersedes: [ <list of source file paths> ]
---

# <Topic Title>

This file consolidates N source files about <topic> from across docs/.

## From: docs/<domain>/<file>.md (canonical)
<full content with frontmatter stripped>

## From: docs/<leftover-dir>/<file>.md (leftover)
<full content>

## From: docs/archive/<old-snapshot>/<file>.md (archive)
<full content>

## Cross-References
<links to related topics>
```

## Source provenance

Each `## From:` section is labelled with the source's provenance:

- **(canonical)** — from the original 7-domain tree (`docs/00-meta/` through `docs/08-misc/`)
- **(leftover dir)** — from a topic-grouped consolidation dir (`docs/dlt/`, `docs/baml/`, etc.)
- **(archive)** — from `docs/archive/2026-06-06-*/` (older or experimental versions; removed by user, see commit history)

## How to navigate

1. Start at `00_index.md` for the routing table
2. Each domain has its own directory
3. Within a domain, files are grouped by topic
4. Each file's frontmatter has `merged_from_count` to gauge breadth
5. Each `## From:` section is self-contained — read the parts you need
6. To drill into a specific source, follow the path in the section header
7. For live code/config, the source path resolves to git-tracked files in `docs/`

## How to add new docs

- New `.md` files in `docs/`: place in the appropriate `docs/<domain>/<topic>/` dir
  as a new section, or create a new topic
- Re-run `uv run scripts/migrate-docs-v2.py` to refresh `docs-v2/`
- New non-`.md` files: place in `docs-v2/11-scripts/`, `12-configs/`, or `13-images/`
  (will be picked up automatically on the next migration run)
- Update `00_index.md` to reflect the change (auto-regenerated each run)

## How to regenerate

```bash
uv run scripts/migrate-docs-v2.py            # full migration
uv run scripts/gen-per-domain-manifests.py   # per-domain JSON manifests
uv run scripts/validate-docs-v2.py           # verify integrity
```

The script is **idempotent**: it regenerates `docs-v2/` from `docs/` each run.
Zero errors expected; any failures are logged to `docs-v2/.migration/errors.log`.

## Coverage statistics

See `docs-v2/changelog.md` for the latest per-domain source counts.
See `docs-v2/.migration/coverage.json` for the full source-to-target map.
