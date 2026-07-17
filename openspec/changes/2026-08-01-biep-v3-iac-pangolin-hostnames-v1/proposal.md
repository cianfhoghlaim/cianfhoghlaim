# 2026-08-01-biep-v3-iac-pangolin-hostnames-v1

## Why

The Pangolin resource definitions in the renamed
`bonneagar/stacks/cianfhoghlaim/pangolin.yaml` (A2) still use
hostnames of the form `*.oideachais.cianfhoghlaim.ie` (e.g.
`oideachais-web.cianfhoghlaim.ie`). The Phase 0 namespace rename
updated the database + DuckLake + BAML namespaces but missed the
Pangolin router hostnames.

This blocks the A3 step of the BIEP v3 live deploy — until the
Pangolin hostnames are aligned, no `*.cianfhoghlaim.ie` DNS record
exists.

This is the A3 change. It lives in the **bonneagar repo** (not
the cianfhoghlaim repo) per the post-v7 flatten split.

## What changes

### 1. Update 5 Pangolin router hostnames

- `web` router: `oideachais-web.cianfhoghlaim.ie` → `web.cianfhoghlaim.ie`
- `api` router: `api.oideachais.cianfhoghlaim.ie` → `api.cianfhoghlaim.ie`
- `dagster` router: `dagster.oideachais.cianfhoghlaim.ie` → `dagster.cianfhoghlaim.ie`
- `agent-os` router: `agents.oideachais.cianfhoghlaim.ie` → `agents.cianfhoghlaim.ie`
- `adk-agents` router: `adk-agents.oideachais.cianfhoghlaim.ie` → `adk-agents.cianfhoghlaim.ie`

### 2. Update CORS middleware name

- `oideachais-cors` → `cianfhoghlaim-cors`

## Dependencies

```yaml
Blocked by: 2026-08-01-bonneagar-iac-namespace-alignment-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
Affected repos: bonneagar (single-repo change)
```

## Acceptance gates

- `grep "oideachais.cianfhoghlaim" bonnegar/stacks/cianfhoghlaim/pangolin.yaml`
  returns 0 matches
- All 5 router hostnames use `*.cianfhoghlaim.ie`
- CORS middleware renamed to `cianfhoghlaim-cors`
- `openspec validate 2026-08-01-biep-v3-iac-pangolin-hostnames-v1 --strict` passes

## Cross-references

- `bonnegar/stacks/cianfhoghlaim/pangolin.yaml` (renamed by A2)
- `.agents/skills/infrastructure-stacks/SKILL.md` — the GOLD_STANDARD Pangolin contract