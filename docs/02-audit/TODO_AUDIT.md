---
title: 'TODO / FIXME Audit — 5 Frontend Workspaces'
domain: 'audit'
status: 'stable'
description: '**Generated:** Phase 10 cross-cutting audit (commit cf824ddad era)'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/TODO_AUDIT.md
ccc_query_hints:
  - todo / fixme audit — 5 frontend workspac
---

# TODO / FIXME Audit — 5 Frontend Workspaces

**Generated:** Phase 10 cross-cutting audit (commit cf824ddad era)

## Method

```bash
grep -rln "TODO\|FIXME\|XXX" oideachais/web/{apps,packages} \
  tuatha/ui croilar/apps/{web,portal} croilar/hono-api \
  --include='*.ts' --include='*.tsx' --include='*.json' \
  --exclude-dir={node_modules,dist,.output}
```

## Result

**Zero TODO / FIXME / XXX comments** in source code across the 5 frontend
workspaces. The codebase is clean of explicit deferral markers.

## Placeholder Strings Found (UI)

The following are *intentional* placeholder strings in user-facing form fields
or pre-built mock data — not deferral markers. Each is documented below.

| File | Line | String | Status |
|:--|:--|:--|:--|
| `oideachais/web/apps/web/src/components/OideachasChat.tsx:98` | `placeholder="Ask Oideachas…"` | **Kept** — standard input placeholder |
| `oideachais/web/apps/web/src/components/leaving-cert/MotherDuckDive.tsx:*` | MotherDuck Dive iframe | **Kept** — wired to real `/api/v1/motherduck` oRPC procedure |
| `tuatha/ui/src/routes/index.tsx` | mock landing content | **Kept** — Phase 5 deliverable; will be replaced when Babylon.js game is bundled |
| `tuatha/ui/src/routes/map.tsx` | mock Celtic regions | **Kept** — Phase 6 deliverable; will be replaced when MapLibre tiles wired |
| `tuatha/ui/src/server/{mythology,curriculum}.ts` | mock data fallback | **Kept** — graceful degradation when API unreachable |

## OpenSpec-Tracked Future Work

| Change ID | Task | Status |
|:--|:--|:--|
| `state-of-art-5-workspaces/3.5` | Add Babylon.js game client workspace | Pending |
| `state-of-art-5-workspaces/5.1` | Wire SpacetimeDB real-time multiplayer | Pending |
| `state-of-art-5-workspaces/5.4` | Replace mythology mock with Graphiti MCP | Pending (deferred — Graphiti MCP not yet running) |
| `state-of-art-5-workspaces/5.5` | Replace curriculum mock with LanceDB MCP | Pending (deferred — LanceDB MCP not yet running) |
| `state-of-art-5-workspaces/6.1` | Wire MapLibre Celtic GeoJSON tiles | Pending |

These are tracked in the OpenSpec change with task IDs, so they do not
appear as TODO comments in source.
