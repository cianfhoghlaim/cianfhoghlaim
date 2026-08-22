## Implementation Tasks

- [x] 1. Update `mise.toml [tools]` to replace `"latest"` with explicit `>=X.Y,<X+1.0` ranges for the 6 minor-stable tools (uv, bun, dagger, pulumi, infisical, duckdb) + `>=X.0,<X+1.0` for opencode-ai. Leave `latest` for the 7 external infra tools (gh, cloudflared, gcloud, oci, sops, aqua, zoxide). (verification-id: version-pinning-applied) (verification: inspection — `grep -E '= "latest"' mise.toml` should show 7 lines, not 14)

- [x] 2. Add the `core:tool-versions:report` task to `mise.toml [tasks]` — runs `mise ls --installed --json | jq 'map({name, version})'`. (verification-id: tool-versions-report-task) (verification: integration — `mise run core:tool-versions:report` exits 0 and prints a 14-row table)

- [x] 3. Add the `core:tool-versions:check-stale` task to `mise.toml [tasks]` — runs `mise ls-remote <tool>` for each pinned tool + compares against the pinned range. Emits a warning per stale tool + exits 1 if any tool is > 1 major behind. (verification-id: tool-versions-check-stale-task) (verification: integration — `mise run core:tool-versions:check-stale` exits 0 in the steady state, 1 if a tool is stale)

- [x] 4. Update `.agents/skills/mise/SKILL.md` to add a "Pinning conventions" subsection (under the existing "Tool management" section). Document the 3 patterns: minor-stable (`>=X.Y,<X+1.0`), major-version-aware (`>=X.0,<X+1.0`), external-infra (`latest`). Cross-link to the new `core:tool-versions:check-stale` task. (verification-id: pinning-conventions-doc) (verification: inspection — `.agents/skills/mise/SKILL.md` contains a `## Pinning conventions` heading)

- [x] 5. Run `mise install` to confirm the pinned ranges resolve cleanly. (verification-id: pinned-install-succeeds) (verification: integration — `mise install` exits 0 and `mise ls --installed` shows the expected pinned versions)

- [x] 6. Run the canonical CI gates to confirm no regressions: `mise run core:typecheck` (must exit 0), `mise run core:lint` (must exit 0), `mise run openspec:validate-all` (must exit 0 with 140+ items). (verification-id: no-regressions-after-pinning) (verification: integration — all 3 gates pass)

- [x] 7. Add the new `core:tool-versions:report` task to the "Daily 'I'm working on X' commands" section in AGENTS.md. (verification-id: doctor-aggregates-tool-versions) (verification: inspection — AGENTS.md contains `core:tool-versions:report` in the priority mise tasks list)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-dev-tooling-version-pinning-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-dev-tooling-version-pinning-v1 --strict` passes
- [x] `mise run core:tool-versions:report` exits 0
- [x] `mise run core:tool-versions:check-stale` exits 0
- [x] `mise install` resolves cleanly
- [x] `mise run core:typecheck` exits 0
- [x] `mise run core:lint` exits 0
- [x] `mise run openspec:validate-all` exits 0

## Notes

- The change deliberately leaves 7 tools as `latest` (external infra: gh, cloudflared, gcloud, oci, sops, aqua, zoxide). These have infrequent breaking changes and are tracked separately via audit cycles. A future change can pin them too if determinism becomes an issue.
- This change is **observability + hygiene only** — no actual tool upgrades. The uv 0.11 → 0.12 bump is gated by a separate openspec change (per the previous round's `uv-0-12-features-v1`).
- The `core:tool-versions:check-stale` task uses `mise ls-remote` which requires network access. In CI, the task should be in a separate job that has network access (or use a cached version manifest).
