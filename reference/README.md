# reference/ — upstream reference material

This directory holds **upstream reference material** that the
project depends on but is not part of the canonical codebase.
Nothing under `reference/` is imported or built; the directory
exists for human reference and to support ad-hoc agent
exploration.

| Subdirectory | Source | Purpose |
|:--|:--|:--|
| `notebooks/` | Cloned from upstream docs (`hf.co/docs`, `geoai.org`, `lakefs.io`, `marimo.io`, etc.) | Reference notebooks for the 5+ upstream tool families the project integrates. **Not a project artifact** — these are upstream example notebooks cloned at repo-init time for context. |

If you want to:

- **Add new reference material** — create a new subdirectory
  under `reference/` named after the upstream source (e.g.
  `reference/arxiv-2606-celtic-llm-survey/`).
- **Move a notebook into a quadrant** — if a notebook
  demonstrates a pattern that should be a first-class artifact
  in the codebase, copy it to the appropriate quadrant
  (`oideachais/notebooks/`, `meaisinfhoghlaim/notebooks/`, etc.)
  and remove it from `reference/`.
- **Delete obsolete reference material** — `git rm -r reference/<dir>/`.
