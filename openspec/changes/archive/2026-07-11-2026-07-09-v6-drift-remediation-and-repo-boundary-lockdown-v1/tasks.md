# Tasks: 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1

## Phase 0 — Pre-flight (no edits) (5 min)

- [ ] 0.1 Confirm 4 archive-now changes have been validated + archived (Wave 1):
      - `openspec validate 2026-07-09-cocoindex-v1-remaining-apps-v1 --strict && openspec archive ... --yes`
      - `openspec validate 2026-07-09-remove-brown-ajah-theming-v1 --strict && openspec archive ... --yes`
      - `openspec validate 2026-07-09-agent-fleet-and-observability-facade-v1 --strict && openspec archive ... --yes`
      - `openspec validate 2026-07-09-cross-nation-content-audit-v1 --strict && openspec archive ... --yes`
- [ ] 0.2 Confirm `bun run ccc:init && bun run ccc:index` has been run after the archive
- [ ] 0.3 Read current `AGENTS.md` (root) + `bonneagar/AGENTS.md` + `openspec/AGENTS.md`

## Phase 1 — Bonneagar drift remediation (1 hour)

- [ ] 1.1 Verify the 5 placeholder dirs have zero importers
- [ ] 1.2 `git -C bonneagar pull --rebase` (sync with remote before applying)
- [ ] 1.3 `cd bonneagar && rm -rf stacks/{backend,platform-service,runner,workers,x2text-service}`
- [ ] 1.4 Verify: `ls -d stacks/*/ | wc -l` returns `87` (post-v6: 5 pruned)
- [ ] 1.5 Update `bonneagar/AGENTS.md` — replace 8 hits of "88 / 86 stacks" → "87 stacks" + add `## IaC Repo Boundary` section
- [ ] 1.6 Update `bonneagar/GOLD_STANDARD.md` — replace 3 hits of "94 stacks" → "87 stacks"
- [ ] 1.7 Update `bonneagar/package.json` — "88-stack" → "87-stack"
- [ ] 1.8 Update `bonneagar/stacks/README.md` — "93/94 stacks" → "87 stacks"
- [ ] 1.9 Update `bonneagar/deploy-runbooks/bunchloch-bootstrap.md` — "86-stack" → "87-stack"
- [ ] 1.10 Update the 3 bonneagar-side spec files
- [ ] 1.11 Stage + commit on bonneagar worktree
- [ ] 1.12 `git -C bonneagar push bonneagar pick-5b-bonneagar-v5-continuation`

## Phase 2 — Cianfhoghlaim drift remediation (45 min)

- [ ] 2.1 Update root `AGENTS.md` — replace 3 hits of "94 stacks" → "87 stacks"
- [ ] 2.2 Update root `AGENTS.md` lines 275, 280 — `sruth/oideachais/...` → `cianfhoghlaim/...`
- [ ] 2.3 Update root `AGENTS.md` line 280 — remove stale `infrastructure/stacks/{engineering/n8n,tools/vikunja,tools/cal-diy}/` reference
- [ ] 2.4 Add new sections to root `AGENTS.md`: `## Repo Boundary`, `## OpenSpec Change Management`, `## OpenCode Safety`
- [ ] 2.5 Update `docs/stacks/README.md` — "88 stacks" → "87 stacks"
- [ ] 2.6 Update the 4 cianfhoghlaim-side spec files
- [ ] 2.7 Update `openspec/AGENTS.md` — add `## Cross-repo sync` + `## Dependencies` sections
- [ ] 2.8 Remove the 1Password + SOPS reference from root `AGENTS.md`

## Phase 3 — New safety script: `preflight:arm-oci` (1.5 hours)

- [ ] 3.1 Create `scripts/preflight-arm-oci.ts` with 4 checks (Pangolin health, Komodo health, Infisical health, process namespace isolation)
- [ ] 3.2 Wire `--dry-run` mode (default true)
- [ ] 3.3 Wire `--strict` mode
- [ ] 3.4 Wire `--emit-md` mode that writes a status report
- [ ] 3.5 Add 2 package.json scripts: `preflight:arm-oci` and `iac:bootstrap`
- [ ] 3.6 Add 4 mise task aliases

## Phase 4 — Wave 2 parallel work (3 hours)

- [ ] 4.1 Apply #6 spec delta — extend `infrastructure-stacks/spec.md`
- [ ] 4.2 Finish #3 — 3 remaining tasks (Brown Ajah component cleanup + 6 marimo embed widgets + bilingual toggle)
- [ ] 4.3 Validate #3: `openspec validate 2026-07-09-biep-6-subject-web-surfaces-v1 --strict`
- [ ] 4.4 Archive #3: `openspec archive 2026-07-09-biep-6-subject-web-surfaces-v1 --yes`
- [ ] 4.5 Validate the new remediation change

## Phase 5 — Wave 3 finish #1 (3 hours)

- [ ] 5.1 Read `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/tasks.md` and identify the 35 remaining unchecked tasks
- [ ] 5.2 Group the 35 tasks into 3 work batches
- [ ] 5.3 Tick each batch as the work lands
- [ ] 5.4 Validate #1
- [ ] 5.5 Archive #1

## Phase 6 — Commit + push (15 min)

- [ ] 6.1 Stage + commit on cianfhoghlaim
- [ ] 6.2 `git push origin pick-4-biep-v1`
- [ ] 6.3 Verify: `git status` shows "up to date with origin/pick-4-biep-v1"
- [ ] 6.4 Verify: `git -C bonneagar status` shows "up to date with bonneagar/pick-5b-bonneagar-v5-continuation"

## Phase 7 — Final acceptance (10 min)

- [ ] 7.1 `openspec list` returns only this remediation change (Wave 3 done)
- [ ] 7.2 `ccc search "94 stacks" | grep AGENTS.md` returns 0 hits
- [ ] 7.3 `ccc search "88 stacks" | grep bonneagar/AGENTS.md` returns 0 hits
- [ ] 7.4 `ccc search "86 stacks" | grep bonneagar/AGENTS.md` returns 0 hits
- [ ] 7.5 `ls -d bonneagar/stacks/*/ | wc -l` returns `87`
- [ ] 7.6 `bun run preflight:arm-oci` exits 0 with "ALL CHECKS PASSED"
- [ ] 7.7 `bun run preflight:arm-oci --strict --emit-md` writes the report
- [ ] 7.8 `mise run lint:skills` passes (53/53)
- [ ] 7.9 `openspec list --specs` returns 50 specs (48 + 2 new from this change)