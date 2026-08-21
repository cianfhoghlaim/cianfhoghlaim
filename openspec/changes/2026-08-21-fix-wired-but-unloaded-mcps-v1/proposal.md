# Change: 2026-08-21-fix-wired-but-unloaded-mcps-v1

## Why

Per the runtime MCP audit (2026-08-21), 4 MCP servers are configured
in `opencode.json` + `.mcp.json` with `enabled: true`:

1. `cocoindex-code` (ccc) — ✓ Active (loaded at session start)
2. `firecrawl` — ✓ Active (12 tools loaded)
3. `motherduck` — ✓ Active (6 tools loaded)
4. `huggingface` — ✓ Active (remote MCP)
5. `chrome-devtools-mcp` — ❌ **WIRED BUT NOT LOADED** (no `chrome_*` tools visible at runtime)
6. `dlt-workspace-mcp` — ❌ **WIRED BUT NOT LOADED** (no `dlt_*` tools visible at runtime)
7. `dlt-workspace-mcp` (in `.mcp.json`) — ❌ Same gap

This is a **bug**, not a design decision. The 2 MCP entries are
correctly wired (the `enabled: true` flags are set, the commands are
valid, the env vars resolve), but the agent runtime fails to register
them at session start.

Likely causes (per the runtime audit):

| MCP | Command pattern | Likely cause |
|:--|:--|:--|
| `chrome-devtools-mcp` | `bunx -y chrome-devtools-mcp` | Bun subprocess loader may need `--stdio` flag, OR Chrome browser not installed on the agent host |
| `dlt-workspace-mcp` | `uv run dlthub ai mcp --stdio` | Requires a `.dlt/.workspace` file at the session root, OR the dlthub CLI isn't on the PATH at session start |

This change diagnoses and fixes both gaps.

## What Changes

### 1. Diagnose the gap for each MCP

For each of the 2 wired-but-not-loaded MCPs, run a 4-step diagnostic:

1. Check the command exists (`which bunx` / `which uv` / `which dlthub`)
2. Run the command in isolation (`bunx -y chrome-devtools-mcp --help`,
   `uv run dlthub ai mcp --help`)
3. Capture stderr + exit code
4. Compare with the MCP server contract docs

Document the diagnosis in `openspec/research/2026-08-21-mcp-server-revival/diagnostics/{chrome-devtools,dlt-workspace}.md`.

### 2. Fix the gap

Apply the fix identified by the diagnosis (per MCP):

- **`chrome-devtools-mcp`**: either add the `--stdio` flag, OR
  install Chrome on the agent host, OR fall back to a different
  Chrome MCP server
- **`dlt-workspace-mcp`**: either create a `.dlt/.workspace` file
  at the session root, OR add `dlthub` to the PATH, OR fall back
  to a different dlthub invocation pattern

### 3. Add `mise run lint:mcp-runtime`

A new CI gate that runs all `mcp:smoke:*` tasks in sequence and fails
if any `enabled: true` MCP entry does not register its expected
tools within 5 seconds.

#### Scenario: lint:mcp-runtime catches a regression

- **GIVEN** a new MCP entry has been added to `opencode.json` with `enabled: true`
- **AND** the corresponding `mcp:smoke:*` task has not been written
- **WHEN** `mise run lint:mcp-runtime` runs as part of CI
- **THEN** the task fails with "no smoke test for MCP entry `<name>`"
- **AND** the developer is forced to write the smoke test before merge

#### Scenario: lint:mcp-runtime catches a runtime crash

- **GIVEN** an existing MCP entry's command has changed (e.g. new `dlthub` version)
- **AND** the command fails to spawn at session start
- **WHEN** `mise run lint:mcp-runtime` runs
- **THEN** the smoke task exits non-zero with "MCP `<name>` failed to register within 5s"
- **AND** the CI gate fails the build

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` (the smoke harness pattern in #1 is shared)
- `Affected repos: cianfhoghlaim`

## Cross-links

- Companion to: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
  (the crawl4ai MCP smoke task uses the same `lint:mcp-runtime` harness)
- Companion to: `2026-08-21-bring-up-knowledge-and-design-mcps-v1`
  (3 new MCPs that need the same diagnostic + smoke pattern)
- Spec delta: `agent-platform-cluster` (the 12-MCP inventory contract)

## Requirements

See `tasks.md` for the 3-phase plan (A: chrome-devtools diagnose + fix,
B: dlt-workspace diagnose + fix, C: lint:mcp-runtime CI gate).

## Validation gate

- [ ] `openspec validate 2026-08-21-fix-wired-but-unloaded-mcps-v1 --strict` exits 0
- [ ] `chrome-devtools-mcp` registers 5+ `chrome_*` tools within 5 s of session start
- [ ] `dlt-workspace-mcp` registers the dlt workspace tools within 5 s
- [ ] `mise run lint:mcp-runtime` fails CI if any `enabled: true` MCP fails to register