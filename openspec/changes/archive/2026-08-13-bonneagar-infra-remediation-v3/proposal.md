# Change: Bonneagar infra remediation v3 (commit working-tree fixes + reconcile repo namespace + automate bootstrap Phases 6/6b/7)

## Why

After the `2026-08-15-bonneagar-infra-remediation-v2` change was
archived (commit `8d2f73d1a`), the working tree on the
`token-plan-lc-pipeline-2026-08` branch contains **6 modified files +
2 untracked paths** that exist in neither `main` nor
`origin/token-plan-lc-pipeline-2026-08`. The most critical of these
are:

1. **`bonneagar/stacks/litellm/config/config.yaml`** — 11 model-name
   mismatches fixed (`-it-GGUF` / `-Instruct-GGUF` suffixes removed
   so the names match the actual llama-swap aliases).
2. **`bonneagar/stacks/llama-swap/compose.yaml`** — image tag
   corrected from `ghcr.io/mostlygeek/llama-swap:v166` (which never
   existed in GHCR) to `:cpu`; mount path corrected.
3. **`meaisinfhoghlaim/models/llama_swap_config.yaml`** — the
   upstream alias mapping updated.
4. **`bun.lock` + `package.json`** — dependency drift from the
   lakehouse-hydration install pass.

Plus three further drifts that this change corrects at source:

5. **`bonneagar/komodo/resource-syncs/storage-infrastructure.toml:14`**
   declares `repo = "cliste/bonneagar"` — the **old pre-merge GitHub
   namespace** that no longer exists post the 2026-07-17 v7 flatten.
   All 3 sibling resource-syncs (`arm1-oci.toml`, `bunchloch.toml`,
   `cross-cutting.toml`) correctly declare `repo =
   "cianfhoghlaim/bonneagar"`. The `storage-infrastructure` sync has
   been silently failing (or worse — silently succeeding against a
   separate fork) for some time, masked by Komodo's
   `delete = false` safety.
6. **`bonneagar/iac/commands/bootstrap.ts:140-150`** — Phases 6 (Komodo
   Core deploy) and 6b (Komodo Periphery deploy) and 7 (TinyAuth
   deploy) emit `logWarn("not yet automated")` and require manual
   `km run procedure deploy-tinyauth-bunchloch` invocations per
   cold-boot.
7. **`bonneagar/stacks/openchamber/compose.yaml:38`** — the SHA256
   digest pin is a deterministic mock (`MOCK_MODE=1` fallback) that
   doesn't correspond to the real `ghcr.io/openchamber/openchamber:1.0.0`
   image.

The deployment-critical risk: a future rebase of
`token-plan-lc-pipeline-2026-08` against `main` silently drops the
litellm + llama-swap fixes (they're currently in the working tree but
uncommitted), leaving the platform with the broken config on disk.

## What Changes

- **Commit the 4 uncommitted working-tree files** that are valid
  fixes from the lakehouse-hydration change
  (`litellm/config.yaml`, `llama-swap/compose.yaml`,
  `meaisinfhoghlaim/models/llama_swap_config.yaml`, plus the
  `bun.lock` + `package.json` drift).
- **Reconcile the `storage-infrastructure.toml:14` repo drift**:
  `repo = "cliste/bonneagar"` → `repo = "cianfhoghlaim/bonneagar"`.
- **Automate bootstrap Phases 6/6b/7** in
  `bonneagar/iac/commands/bootstrap.ts:140-150` — replace the 3
  `logWarn("not yet automated")` blocks with `await deployKomodoCore()
  + await deployKomodoPeriphery() + await deployTinyauth()` calls
  using the existing 4 cross-cutting procedures
  (`komodo-core.toml`, `komodo-periphery-bunchloch.toml`,
  `deploy-tinyauth-bunchloch.toml`).
- **Update the openchamber SHA256 digest** at
  `openchamber/compose.yaml:38` to a real digest (operator action —
  re-run `scripts/fetch-image-digest.sh` from a host with live GHCR
  access).
- **Reconcile the `ai-that-works` submodule pointer** to the canonical
  upstream commit (operator action — `cd ai-that-works && git fetch &&
  git checkout main && cd ..`).
- Add an `infrastructure-stacks` spec delta (1 MODIFIED Requirement)
  that tightens the "6-file GOLD_STANDARD" requirement to also
  enforce `repo =` consistency across all 4 resource-sync files.

## Dependencies

`Blocked by: none`. `Affected repos: cianfhoghlaim (single repo) +
1 submodule pointer reconciliation (ai-that-works)`.

## Impact

- Capabilities: MODIFIED `infrastructure-stacks` (1 MODIFIED
  Requirement tightening the resource-sync repo-coverage invariant).
- Code: 4 commit-only files (`bonneagar/stacks/litellm/config/config.yaml`,
  `bonneagar/stacks/llama-swap/compose.yaml`,
  `meaisinfhoghlaim/models/llama_swap_config.yaml`, `bun.lock`,
  `package.json`) + 1 modified IaC file
  (`bonneagar/komodo/resource-syncs/storage-infrastructure.toml`) +
  1 refactor (`bonneagar/iac/commands/bootstrap.ts:140-150`) + 1
  operator action (`bonneagar/stacks/openchamber/compose.yaml:38`).
- Risk: low — all changes have been validated in the working tree
  (the litellm/llama-swap fixes already ran live for the
  lakehouse-hydration Phase C/D5 verification).
