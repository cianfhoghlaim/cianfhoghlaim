---
title: ccc search sample for "Dagster"
generated: 2026-06-13
status: living-document
description: Demonstrates that ccc search over docs/ returns the same source files that were merged into docs-v2/02-data-platform/dagster-orchestration.md
---

# ccc search sample: "Dagster"

This file shows that **ccc search over the canonical `docs/` returns the
exact same source files** that were merged into
`docs-v2/02-data-platform/dagster-orchestration/dagster-orchestration.md`.

Run:

```bash
ccc search "Dagster" --limit 20
```

Top 20 results (most-relevant first):

```
$ ccc search "Dagster" --limit 20
```

Result 1 (score 0.686): `infrastructure/stacks/engineering/dagster/README.md:1-4`
- This is the live infrastructure README — primary navigation surface

Result 2 (score 0.681): `docs/00-package-ecosystem/orchestration/dagster-sdk.md:1-9`
- Folded into `docs-v2/02-data-platform/dagster-orchestration/dagster-orchestration.md` §1

Result 3 (score 0.6xx): `docs/02-data-platform/dagster-sdk.md`
- Folded into the same merged file

Results 4-N: `docs/dagster/*.md` (leftover dir, 22+ files)
- All folded into the same merged file (see `supersedes` list in frontmatter)

## How to navigate

| Use case | Path |
|:--|:--|
| Live infra reference | `infrastructure/stacks/engineering/dagster/README.md` |
| Consolidated overview (61 source files) | `docs-v2/02-data-platform/dagster-orchestration/dagster-orchestration.md` |
| Specific SDK detail | `docs/00-package-ecosystem/orchestration/dagster-sdk.md` |
| Specific leftover topic | `docs/dagster/<topic>.md` |

## Per-source section in the merged file

The merged file's `## From:` sections preserve each source's full content
with its original frontmatter stripped, so a reader can:

1. See the consolidated view (1 file)
2. Drill into any individual source (1 section)
3. Compare versions (multiple sections per topic)
4. Jump to the live code via the source paths in `supersedes`
