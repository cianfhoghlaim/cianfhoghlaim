# cianfhoghlaim/ci — Code-only utilities for the cianfhoghlaim CI surface

The `cianfhoghlaim/ci/` subpackage contains the Python code
for the `ci/` stacks in `bonneagar/stacks/`. The ops
(Dockerfile, compose, blueprint, sidecar, secrets.env,
pangolin.yaml, .env.example) live in `bonneagar/stacks/ci/`.

## Design principle

`cianfhoghlaim/` = the code. `bonneagar/` = the ops.

For each stack in `bonneagar/stacks/ci/`, the Python code
lives in this subpackage and the ops live in
`bonneagar/stacks/ci/<name>/`. The Dockerfile in
`bonneagar/stacks/ci/<name>/` uses a multi-stage build to
`COPY` the Python code from the cianfhoghlaim image.

## Current sub-stacks

| Stack | Python module | Purpose |
|:--|:--|:--|
| `ci/hf-watchdog` | `cianfhoghlaim.ci.hf_watchdog` | Daily HF Hub liveness check for the v4 OCR/VLM registry |

## Adding a new sub-stack

1. Add the Python module to `cianfhoghlaim/ci/<name>.py`
2. Add the ops to `bonneagar/stacks/ci/<name>/` (6-file
   GOLD_STANDARD + Dockerfile)
3. The Dockerfile uses `COPY --from=ghcr.io/cianfhoghlaim/cianfhoghlaim:dev
   /app/cianfhoghlaim/ci/<name>.py /app/`
4. Register the stack in
   `bonneagar/iac/komodo/deploy-stacks.ts` with tag
   `host:bunchloch` + `tier:ci` + `project:cianfhoghlaim`
5. Document the stack at
   `cianfhoghlaim/docs/stacks/ci_<name>.md`
6. Add a row to the table above

## Cross-references

- [`.agents/skills/infrastructure-stacks-documentation/SKILL.md`](../../../.agents/skills/infrastructure-stacks-documentation/SKILL.md) —
  the per-stack doc template
- [`../docs/stacks/ci/hf-watchdog.md`](../docs/stacks/ci_hf-watchdog.md) —
  the hf-watchdog doc
- [`../../bonneagar/stacks/ci/hf-watchdog/`](../../bonneagar/stacks/ci/hf-watchdog/) —
  the ops dir
- [`openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/`](../../../openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/) —
  the openspec change artifacts
