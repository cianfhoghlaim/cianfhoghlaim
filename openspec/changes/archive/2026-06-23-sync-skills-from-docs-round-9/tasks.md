# Tasks: sync-skills-from-docs-round-9

## 1. OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `MERGE_MAP.md` (Phase 0 reconnaissance).
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (agentic-frontend-frameworks).
- [x] Validate `--strict`.

## 2. Phase 1: New skills (2)
- [x] `.agents/skills/web-mirrors/SKILL.md` (188 lines) —
      8 KCG-authored upstream summaries for the web stack.
- [x] `.agents/skills/agentic-frontend-frameworks/SKILL.md`
      (287 lines) — umbrella skill stitching TanStack +
      CopilotKit + AG-UI + Convex + Hono + oRPC + Cloudflare
      + Pydantic AI for KCG agentic web frontends.

## 3. Phase 2: Move 52 files
- [x] 27 KEEP-NEW files → various skills' `references/`
- [x] 7 WEB-MIRROR files → `web-mirrors/references/`
- [x] 18 CLIPPING files → various skills'
      `references/clippings/`

## 4. Phase 3: Expand 14 existing skills (+1,536 lines)
- [x] tanstack-start (+145)
- [x] better-auth (+91)
- [x] ag-ui (+100)
- [x] convex (+145)
- [x] effect-ts (+159)
- [x] orpc (+146)
- [x] cloudflare (+77)
- [x] pydantic-ai (+70)
- [x] copilotkit (+45)
- [x] stagehand (+37)
- [x] monorepo (+97)
- [x] ui-components (+89)
- [x] pdf (+83)
- [x] tuatha-mmo (+138)
- [x] celtic-asset-generation (+89)

## 5. Phase 4: Delete
- [x] 38 .md files from `docs/web/` (3 nav, 4 tanstack
      indexes, 3 alchemy empties, 1 07-asset dedup, 1
      09-clipping dedup, 1 08-repo trivial, 1 README, 16
      chrome-devtools-mcp, 3 tanmaxx-17, 4 misc)
- [x] 2 cloned subdirs: `docs/web/chrome-devtools-mcp/`,
      `docs/web/tanmaxx-17/`
- [x] 11 cloned upstream repos: `docs/tuatha/08-mirrors/<name>/`
      × 11 (93 MB)
- [x] `rm -rf docs/web/`
- [x] `rm -rf docs/tuatha/` (after the 08-mirrors subdir
      is gone)

## 6. Verify
- [ ] Re-validate `--strict`.
- [ ] `git status --short | wc -l` is reasonable
      (~150-180 staged).

## 7. Archive
- [ ] `openspec archive sync-skills-from-docs-round-9 --yes`.

## 8. Land the plane
- [ ] `git add` only my changes (avoid the pre-existing
      .gitignore, .infisical.env, stirling-pdf,
      cocoindex_flows, untracked top-level docs, etc.).
- [ ] `git commit -m "..."`.
- [ ] `git push`.
