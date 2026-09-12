## Why

The repo ran `@fission-ai/openspec@1.4.1` while upstream shipped 1.5
through 1.11; `openspec/AGENTS.md` and `.agents/skills/openspec/SKILL.md`
described an "OPSX schema not adopted" framing that conflated the
legacy-schema/OPSX-schema choice with the `/opsx:*` command-delivery
profile and mis-stated that adopting `/opsx:*` commands requires
re-archiving all pending changes. Verified inventory on 2026-09-02
found 36 pending changes, 102 specs, and 344 archived changes. CLI
upgrade, corrected framing, and the new `.openspec.yaml` convention
are the scope.

## What Changes

- Upgrade `@fission-ai/openspec` from 1.4.1 to 1.11.0 globally.
- Create `openspec/config.yaml` with `schema: spec-driven` so the new
  `openspec doctor` root-health check reports the root healthy.
- Adopt the `.openspec.yaml` per-change metadata convention (schema,
  created, goal, affected_areas, optional `skip_specs`,
  `retire_capabilities`).
- Correct the legacy-vs-OPSX framing in `openspec/SKILL.md` and
  `openspec/AGENTS.md` so it accurately describes the single in-use
  schema and the `/opsx:*` profile layer.
- Adopt upstream's undated-kebab change-ID convention for new changes
  going forward; existing dated IDs are left as-is.

## Capabilities

### New Capabilities
- `openspec-cli-conventions`: the project's contract for openspec CLI
  usage, change authoring, and `openspec config profile` selection
  under openspec 1.11.

### Modified Capabilities
(none — this change is a docs/CLI/tooling refactor; its single
`openspec-cli-conventions` spec establishes the convention going forward
without modifying any existing capability's requirements)

## Impact

- **Affected files**: `.agents/skills/openspec/SKILL.md` (rewritten for
  1.11), `openspec/AGENTS.md` (corrected OPSX framing), `openspec/config.yaml`
  (new), all *new* `openspec/changes/<id>/.openspec.yaml` files
  (convention adopted).
- **Affected skill description**: `.agents/skills/openspec/SKILL.md`
  description field updated to mention 1.11 + the corrected schema
  framing.
- **No code changes** in `dlt_sources/`, `orchestration/`,
  `cocoindex_flows/`, or `agents/`.

## Dependencies

`Blocked by: none`
`Blocked by (soft): none`
`Affected repos: cianfhoghlaim`