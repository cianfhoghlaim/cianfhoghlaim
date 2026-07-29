## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

# Change: 2026-07-28-openchamber-bunchloch-dev-parity-v1

## Why

OpenChamber currently has a bundled-runtime development shape that does not
provide parity with the existing Bunchloch OpenCode 1.17.9 environment. The
container must use the host OpenCode server rather than starting a second
runtime, and it must address the host repository using the same absolute path
that the host-side OpenCode process uses. Otherwise session directory filters,
working-tree discovery, and MCP configuration resolve against different paths
and the browser UI cannot reliably resume the host user's work.

The change defines a Bunchloch-only development contract for OpenChamber 1.16.3:
external OpenCode mode is explicit, host sessions and MCP configuration remain
owned by the host OpenCode server, OpenChamber configuration persists without
covering the application files, and the container has the tooling needed for
git-aware sessions. It also defines secret, network, and verification gates so
this can be implemented without falling back to plaintext `.env` values or an
accidental public port.

## What changes

- Add a Bunchloch development overlay/implementation contract for
  `bonneagar/stacks/openchamber/`; this proposal does **not** implement or
  edit stack files.
- Pin the OpenChamber image/build to `1.16.3` and require `git` in the runtime
  image.
- Make external mode explicit with the host OpenCode endpoint, port `4096`,
  and `OPENCODE_SKIP_START=true`, so OpenChamber never starts a bundled
  OpenCode daemon in this environment.
- Mount the host repository at the identical absolute path
  `/Users/cianmacandeisigh/dev/kings_college_galway` inside the container.
- Keep host OpenCode sessions and MCP configuration behind the external server;
  verification must prove that existing sessions are visible and that the
  enabled MCP list is non-empty/expected.
- Persist OpenChamber's own config/state under its XDG config directory while
  leaving `/home/bun/.openchamber` (the application/work directory) unshadowed.
- Use Infisical/Locket injection only, bind the UI port to loopback, and use
  the correct OpenChamber `/health` and OpenCode `/global/health` checks.

## Impact

- **Affected capabilities:** `infrastructure-stacks`,
  `agent-platform-cluster`.
- **Affected host:** `bunchloch` development environment only.
- **Implementation boundary:** stack files, Dockerfile, and runbook changes
  are intentionally deferred to implementation; this change only establishes
  their acceptance contract and verification plan.
- **Security:** no plaintext secret values may be added to the stack, image,
  repository, or generated verification artifacts.

## Non-goals

- Do not deploy or modify the arm1-oci OpenChamber surface.
- Do not replace the host OpenCode installation, host session store, host MCP
  configuration, or host repository checkout.
- Do not run a second bundled OpenCode server in the OpenChamber container.
- Do not expose the Bunchloch development UI on a non-loopback host address.
- Do not commit stack files or implementation code as part of this authoring
  task.

## Dependencies

`Blocked by: 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
`Blocked by: 2026-07-24-full-local-agent-platform-stack-up-v1`
`Blocked by (soft): 2026-07-28-reconcile-stack-contract-and-rename-bons-kcg-to-cianfhoghlaim-v1`
`Affected repos: cianfhoghlaim`

The hard blockers provide the Bunchloch local Infisical/Locket and shared
agent-platform prerequisites. This change MUST NOT archive until both hard
blockers have archived; the stack-contract reconciliation is an informational
sequencing dependency.

## Validation

The authoring gate is:

```bash
openspec validate 2026-07-28-openchamber-bunchloch-dev-parity-v1 --strict
```

Implementation must additionally execute the task-level Compose, health,
session, MCP, secret, and loopback checks recorded in `tasks.md`.
