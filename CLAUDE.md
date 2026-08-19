@AGENTS.md

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
