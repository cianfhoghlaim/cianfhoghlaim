# Proposal: Delete superseded `infrastructure/legacy/{ANALYSIS,LOCKET-MODES}.md`

## Why

Two legacy reference documents under `infrastructure/legacy/`
were superseded by current skill docs and have been dead-on-disk
for several rounds of docs consolidation:

| File | Size | Replaced by |
|:--|--:|:--|
| `infrastructure/legacy/ANALYSIS.md` | 15,539 bytes | `.agents/skills/kcg-pangolin-stack/SKILL.md` |
| `infrastructure/legacy/LOCKET-MODES.md` | 8,630 bytes | `.agents/skills/kcg-locket-sidecar/SKILL.md` |

Both files are referenced EXACTLY ONCE in the entire repo, and
both references explicitly say "(now superseded)":

- `.agents/skills/kcg-pangolin-stack/SKILL.md:155`:
  "the 2025-12 predecessor-project analysis (now superseded)"
- `.agents/skills/kcg-locket-sidecar/SKILL.md:201`:
  "the v0 predecessor analysis (now superseded)"

Zero production callers:

- NOT in `mise.toml`
- NOT in any of the 103 Docker Compose stacks
- NOT in `scripts/` or `infrastructure/scripts/`
- NOT in any DAG (`infrastructure/dagger/`)
- NOT in any GitHub Actions workflow
- NOT in any `.forgejo/` workflow
- NOT in any agent fleet prompt

`infrastructure/legacy/README.md` (the archive index, 1,454
bytes) does NOT reference these 2 files — it only documents the
4 archived TypeScript scripts (`cloudflare-dns.ts`,
`pangolin-setup.ts`, `servers.ts`, `taisce-deploy.ts`).
KEEP `README.md`.

## What changes

1. `git rm infrastructure/legacy/ANALYSIS.md`
2. `git rm infrastructure/legacy/LOCKET-MODES.md`
3. Leave `infrastructure/legacy/README.md` untouched (it's the
   archive index for the 4 TypeScript scripts and remains valid)

## Out of scope

- The 2 dangling cross-references in skill docs
  (`.agents/skills/kcg-pangolin-stack/SKILL.md:155` +
  `.agents/skills/kcg-locket-sidecar/SKILL.md:201`) are
  pre-existing in-flight work per the user's exclusion list
  (`.agents/skills/*.md`). They will reference deleted files
  after this change. **Flagged as a follow-up task** in
  `tasks.md` for the user to clean up out-of-band.
- The 4 archived TypeScript scripts (`cloudflare-dns.ts` etc.)
  in `infrastructure/legacy/` are documented in
  `infrastructure/legacy/README.md` and referenced by
  `openspec/changes/archive/2026-06-24-infrastructure-stack-doctor-v1/`
  as the canonical archive index entry. KEEP.

## Impact

- Disk: 24,169 bytes freed
- Risk: zero — no production callers
- Dangling refs: 2 cross-references in skill docs (pre-existing
  in-flight work; flagged for follow-up)
- Spec delta: 1 ADDED Requirement to `indexing-and-cognition`
  (no-dead-superseded-legacy-docs)

## Spec delta

Adds the no-dead-superseded-legacy-docs requirement to
`openspec/specs/indexing-and-cognition/spec.md`.