# Tasks: 2026-08-21-fix-wired-but-unloaded-mcps-v1

## Phase A: Diagnose + fix `chrome-devtools-mcp` (1st priority)

- [ ] A.1 — Verify the chrome-devtools-mcp binary is installable (`bunx -y chrome-devtools-mcp --help`)
- [ ] A.2 — Check whether Chrome is installed on the agent host (`which google-chrome` / `which chromium`)
- [ ] A.3 — Run the command in isolation and capture stderr + exit code
- [ ] A.4 — Document the diagnosis at `openspec/research/2026-08-21-mcp-server-revival/diagnostics/chrome-devtools.md`
- [ ] A.5 — Apply the fix (one of: add `--stdio` flag, install Chrome, fall back to alternative MCP server)
- [ ] A.6 — Verify `chrome_*` tools register within 5 s of session start
- [ ] A.7 — Add `mcp:smoke:chrome` mise task that confirms 5+ `chrome_*` tools are discoverable

## Phase B: Diagnose + fix `dlt-workspace-mcp` (2nd priority)

- [ ] B.1 — Verify `dlthub` CLI is on the PATH (`which dlthub`)
- [ ] B.2 — Check for the `.dlt/.workspace` file at the session root
- [ ] B.3 — Run `uv run dlthub ai mcp --help` and capture stderr + exit code
- [ ] B.4 — Document the diagnosis at `openspec/research/2026-08-21-mcp-server-revival/diagnostics/dlt-workspace.md`
- [ ] B.5 — Apply the fix (one of: create `.dlt/.workspace`, add dlthub to PATH, fall back to alternative invocation)
- [ ] B.6 — Verify the dlt workspace tools register within 5 s
- [ ] B.7 — Add `mcp:smoke:dlt-workspace` mise task that confirms the dlt tools are discoverable

## Phase C: `mise run lint:mcp-runtime` CI gate (3rd priority)

- [ ] C.1 — Add the `lint:mcp-runtime` task to `mise.toml`
- [ ] C.2 — Implement the task as a shell script that runs all `mcp:smoke:*` tasks in sequence
- [ ] C.3 — Implement the "no smoke test for MCP entry" check (fail if an `enabled: true` MCP entry has no smoke task)
- [ ] C.4 — Implement the "MCP failed to register within 5s" check (timeout the smoke task at 5 s)
- [ ] C.5 — Wire the task into `.github/workflows/lint-mcp-runtime.yaml` (the CI workflow)

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-fix-wired-but-unloaded-mcps-v1 --strict` exits 0
- [ ] V.2 `chrome-devtools-mcp` registers 5+ `chrome_*` tools within 5 s of session start
- [ ] V.3 `dlt-workspace-mcp` registers the dlt workspace tools within 5 s
- [ ] V.4 `mise run lint:mcp-runtime` fails CI if any `enabled: true` MCP fails to register
- [ ] V.5 `mise run lint:mcp-runtime` exits 0 with the fix in place