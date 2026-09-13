# Tasks: Bonneagar infra remediation v3

## Phase A — Commit working-tree fixes (code-only)

- [ ] A1 `git add bonneagar/stacks/litellm/config/config.yaml` —
  the 11 model-name fixes (`-it-GGUF` → bare alias) from the
  `2026-08-08-lakehouse-extensive-hydration-v1` change.
- [ ] A2 `git add bonneagar/stacks/llama-swap/compose.yaml` — the
  `:v166` → `:cpu` image tag fix + the mount-path fix.
- [ ] A3 `git add meaisinfhoghlaim/models/llama_swap_config.yaml` —
  the upstream alias mapping alignment.
- [ ] A4 `git add bun.lock package.json` — the dependency drift from
  the lakehouse-hydration install pass.

## Phase B — Reconcile `storage-infrastructure.toml` repo namespace

- [ ] B1 Verify the canonical remote URL:
  `git ls-remote https://git.cianfhoghlaim.ie/cianfhoghlaim/bonneagar
  main` returns a valid SHA. (If unreachable, flag for operator.)
- [ ] B2 Edit
  `bonneagar/komodo/resource-syncs/storage-infrastructure.toml:14`:
  `repo = "cliste/bonneagar"` → `repo = "cianfhoghlaim/bonneagar"`.
- [ ] B3 `git add` + commit.

## Phase C — Automate bootstrap Phases 6/6b/7

- [ ] C1 Read
  `bonneagar/komodo/procedures/komodo-core.toml` to confirm the
  procedure name and signature.
- [ ] C2 Read
  `bonneagar/komodo/procedures/deploy-tinyauth-bunchloch.toml` to
  confirm the procedure name and signature.
- [ ] C3 Edit `bonneagar/iac/commands/bootstrap.ts:140-150` —
  replace the 3 `logWarn("not yet automated")` blocks with the
  corresponding `await execKomodoProcedure("<proc-name>")` calls
  (or the equivalent Bun-side `child_process.exec` invocations
  matching the rest of the bootstrap.ts pattern).
- [ ] C4 Verify `bun run iac:bootstrap` completes Phases 6/6b/7
  without any `logWarn("not yet automated")` output.

## Phase D — Operator actions (flagged for manual follow-up)

- [ ] D1 (operator) Re-run `scripts/fetch-image-digest.sh
  ghcr.io/openchamber/openchamber:1.0.0` from a host with live GHCR
  access; replace the mock SHA256 at
  `bonneagar/stacks/openchamber/compose.yaml:38`.
- [ ] D2 (operator) `cd ai-that-works && git fetch && git checkout
  main && cd ..` — reconcile the submodule pointer.

## Phase E — Validation

- [ ] E1 `git status` clean (no modified/untracked files remain).
- [ ] E2 `mise run stack-doctor:strict` reports zero grammar
  regressions on the modified IaC files.
- [ ] E3 `mise run lint:drift-docs` passes (validates every AGENTS.md
  number claim against ground truth).
- [ ] E4 `bun run sync:komodo --dry-run` shows no diff against the
  live Komodo Core (storage-infrastructure sync now polls the correct
  repo).
- [ ] E5 `openspec validate 2026-08-13-bonneagar-infra-remediation-v3
  --strict` returns 0 errors.

## Out of scope (flagged for follow-up)

- The litellm redeploy blocker (the deployed container at
  `~/.komodo-stacks/litellm/config/config.yaml` needs a manual
  `km deploy stack litellm` to pick up the fixed config — not in scope
  here, tracked by `2026-08-13-biep-v3-orchestration-activation-v1`).
- The llama-swap GGUF weights download (~60-80 GB) — not in scope here,
  tracked by the same orchestration-activation change.
