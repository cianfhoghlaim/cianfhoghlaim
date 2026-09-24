# Cross-repo sync: 2026-09-24-web-agentic-deep-refactor-v1

This change touches ONLY `web/` + `agents/` (in-repo subdirectories). No sister-repo coordination required.

## Files touched

- `web/hono-api/src/db/schema.ts` — Drizzle schema extension
- `web/hono-api/src/db/client.ts` — type aliases for the new tables
- `web/hono-api/src/db/migrations/2026-09-24-k12-agentic-tables.sql` — DDL
- `web/hono-api/src/routes/copilotkit/registry.ts` — agent registry end-to-end wire-up
- `web/apps/_shared/copilotkit/stage_router.ts` — NEW canonical shared module
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/_base.ts` — NEW canonical base
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/index.ts` — NEW barrel
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/actions.ts` — NEW 18-action canonical list
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/runtime.ts` — +/actions endpoint
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts` — re-export
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` — re-export
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/_base.ts` — NEW shared base
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/stage_router.ts` — re-export
- `web/apps/_archive/_oideachais_apps/` → `web/apps/_archive/cianfhoghlaim-pre-v6/` — rename
- `web/AGENTS.md` — document AG-UI wire-up
- `web/apps/_shared/copilotkit/README.md` — NEW
- `.agents/skills/copilotkit-agui-bridge/SKILL.md` — NEW

## Order of operations

1. **Single-repo change** — all files in `cianfhoghlaim/`
2. **Commit + push** to `origin/openspec/cianchosaint-handoff-v1`

No ciandlithe or other sister-repo coordination required.

## Verification

```bash
# 1. Type check + lint
cd web && bun install && bun run typecheck && bun run lint
# Expected: exit 0

# 2. Drizzle migration
bun run drizzle-kit migrate
# Expected: creates the 12 new tables without error

# 3. Opspec strict validation
openspec validate 2026-09-24-web-agentic-deep-refactor-v1 --strict
# Expected: exit 0

# 4. The directory rename
ls web/apps/_archive/cianfhoghlaim-pre-v6/
# Expected: contains _oideachais_apps/ subdir
```
