---
title: docs-v2 Migration Guide
status: living-document
description: How merged files are structured; how to read them
---

# docs-v2 Migration Guide

`docs-v2/` is a per-topic merged mirror of `docs/`. Every file in `docs-v2/`
follows the same structure so that the **original sources remain attributable**
and **no information is lost**.

## Section structure

Each merged `.md` file contains:

```
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

## From: docs/02-data-platform/dagster-orchestration.md (canonical)
<full original content with frontmatter stripped>

## From: docs/dagster/setup-guide.md (leftover dir)
<full original content>

## From: docs/archive/2026-06-06-data-engineering/Dagster-v0.md (archive)
<full original content>

## Cross-References
<links to related topics>
```

## Source provenance

Each `## From:` section is labelled with the source's provenance:

- **(canonical)** — from the original 7-domain tree (`docs/00-*` through `docs/08-*`)
- **(leftover dir)** — from a topic-grouped consolidation dir (`docs/dlt/`, `docs/baml/`, etc.)
- **(archive)** — from `docs/archive/2026-06-06-*/` (older or experimental versions)

## How to navigate

1. Start at `00_index.md` for the routing table
2. Each domain has its own directory
3. Within a domain, files are grouped by topic
4. Each file's frontmatter has `merged_from_count` to gauge breadth
5. Each `## From:` section is self-contained — read the parts you need

## How to add new docs

- New `.md` files: place in the appropriate `docs-v2/<domain>/<topic>/` dir
  as a new section, or create a new topic
- New non-`.md` files: place in `docs-v2/11-scripts/`, `12-configs/`, or `13-images/`
- Update `00_index.md` to reflect the change

## How to regenerate

```bash
uv run scripts/migrate-docs-v2.py
```

The script is idempotent: it regenerates `docs-v2/` from `docs/` each run.
