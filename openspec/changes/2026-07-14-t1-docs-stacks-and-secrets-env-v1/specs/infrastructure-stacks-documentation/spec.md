## MODIFIED Requirements

### Requirement: All `secrets.env` files use `infisical://dev-baile/<stack>/<key>` references

The system SHALL ensure every `bonneagar/stacks/<name>/secrets.env`
file uses the canonical v4 secret-management contract:
`KEY=infisical://dev-baile/<stack>/<KEY>` for runtime secrets and
`LOCKET_MODE=watch|exec|oneshot` header for Locket sidecar injection
mode.

The legacy template form `{{ infisical:///<key> }}` (handlebars-style,
used by ~36 stacks including `openclaw`, `cal-diy`) SHALL still be
accepted by `scripts/stack-doctor.sh` (whose regex is
`(infisical://dev-baile/|\{\{ infisical://)`), but new stacks MUST
use the canonical form. A follow-up change MAY normalise the 36
legacy-template stacks into the canonical form.

For stacks whose `compose.yaml` declares no secret env vars (e.g.
`it-tools`, `marimo`, `actual`), the `secrets.env` SHALL contain:
- The canonical v4 header block (`# COMMITTED: yes. PLAINTEXT: NEVER.` +
  `# Resolved at container runtime by the Locket sidecar.`)
- `LOCKET_MODE=watch` declared at the top
- A commented-out example reference
  (`# <STACK>_EXAMPLE_KEY=infisical://dev-baile/<stack>/example_key`)
  for pattern documentation

The `scripts/fix-secrets-env-placeholders.ts` Bun script SHALL be
the canonical idempotent converter from the placeholder-comment form
to the canonical v4 form. It SHALL default to dry-run and accept
`--apply` to write files.

The `scripts/stack-doctor.sh` CI gate SHALL report zero
`secrets.env has no infisical:// refs` warnings (with the regex
`(infisical://dev-baile/|\{\{ infisical://)`).

#### Scenario: A new secrets.env file is added with plaintext values

- **GIVEN** a developer adds `bonneagar/stacks/<new>/secrets.env`
  with plain `KEY=value` lines
- **WHEN** the developer runs `bun run validate-stacks`
- **THEN** the `secrets.env has no infisical:// refs` warning SHALL
  fire
- **AND** the developer MUST convert to
  `KEY=infisical://dev-baile/<new>/KEY` before merging

#### Scenario: A placeholder secrets.env is converted to canonical form

- **GIVEN** the 13 `secrets.env` files listed in
  `2026-07-14-t1-docs-stacks-and-secrets-env-v1` were either plaintext
  (5 files: `it-tools`, `komodo`, `llama-swap`, `marimo`, `searxng`)
  OR placeholder-comment-only (8 files: `actual`, `audiobookshelf`,
  `dozzle`, `enclosed`, `Kapowarr`, `LetterFeed`, `pastemax`,
  `pinchflat`)
- **WHEN** `bun run scripts/fix-secrets-env-placeholders.ts --apply`
  + the 5 inline plaintext edits land
- **THEN** every one of the 13 files SHALL contain either:
  - At least one `KEY=infisical://dev-baile/<stack>/<key>` ref, OR
  - `LOCKET_MODE=watch` + the canonical v4 header block
- **AND** `DOCS_DIR=docs/stacks bun run validate-stacks` SHALL report
  zero `secrets.env has no infisical:// refs` warnings
