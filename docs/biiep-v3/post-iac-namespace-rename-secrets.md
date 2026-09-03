# Post-IaC-Namespace-Rename Secrets Sync

> **Status:** Documented (NOT yet executed — requires running
> `bun run scripts/init-vault.ts` against a live Infisical instance
> with valid `INFISICAL_CLIENT_ID` / `INFISICAL_CLIENT_SECRET`).
> This file is the operator hand-off artifact for Stage 10 of the
> `2026-08-01-bonneagar-iac-namespace-alignment-v1` openspec change.

## Why this file exists

The Bonneagar IaC rename (`oideachais` → `cianfhoghlaim`) touched
two secret paths in the self-hosted `dev-baile` Infisical vault:

| Old path (pre-A2) | New path (post-A2) |
|:--|:--|
| `dev-baile/oideachais-llm/api_key` | `dev-baile/cianfhoghlaim-llm/api_key` |
| `dev-baile/oideachais-llm/provider` | `dev-baile/cianfhoghlaim-llm/provider` |

The corresponding `.infisical.env` template was already updated on
2026-07-29 in commit `b824dd921` (see lines 682–686):

```bash
# =============================================================================
# CIANFHGHLLAIM-SPECIFIC SECRETS        (was OIDEACHAIS-SPECIFIC pre-A2)
# =============================================================================
# From sruth/cianfhoghlaim/secrets.env (was sruth/oideachais pre-v7)
CIANFHGHLLAIM_LLM_API_KEY=infisical://dev-baile/cianfhoghlaim-llm/api_key
CIANFHGHLLAIM_LLM_PROVIDER=infisical://dev-baile/cianfhoghlaim-llm/provider
```

> **Spelling note:** The env-var prefix is `CIANFHGHLLAIM_` (two
> consecutive `L`s), matching the convention established in commit
> `b824dd921`. The vault folder name uses the standard spelling
> `cianfhoghlaim-llm` (one `L` after the `H`), matching the rest of
> the Infisical vault.

## What still needs to happen

The vault-side rename MUST be executed by an operator with access
to the live Infisical instance. Two acceptable paths:

### Option A — Run the init-vault script (preferred)

```bash
# 1. Ensure credentials are present in the local .env
grep -E '^INFISICAL_(CLIENT_ID|CLIENT_SECRET|PROJECT_ID|URL)=' .env

# 2. Verify Infisical is reachable
curl -sf "${INFISICAL_URL:-http://localhost:8081}/api/status" | jq .

# 3. Run the sync
bun run scripts/init-vault.ts
# (alias: mise run secrets:init)
```

The script will:
1. Read every `infisical://` URI in `.infisical.env`
2. Create / update each vault secret under
   `dev-baile/<path-from-uri>`
3. Verify the 2 renamed paths exist with the correct values

### Option B — Manual vault update (if the script fails)

1. Open `https://infisical.cianfhoghlaim.ie` (or the local
   `http://arm1-oci:8081` on `arm1-oci`)
2. Project: `dev-baile`
3. Folder: `cianfhoghlaim-llm`
4. Secrets to create:

| Secret name | Type | Suggested value |
|:--|:--|:--|
| `api_key` | `shared` | (rotate from upstream LLM provider; see Langfuse) |
| `provider` | `shared` | `kimi-k2.6` (the canonical lc6 LLM; see `litellm.cianfhoghlaim.ie`) |

5. Delete the legacy `oideachais-llm/` folder if it still exists
   (it should be gone after `init-vault.ts` runs, but verify).

## Verification

After either option, confirm:

```bash
# Vault folders
infisical folders list --projectId "$INFISICAL_PROJECT_ID" \
  --env dev-baile | grep -E "cianfhoghlaim-llm|oideachais-llm"
# Expect: cianfhoghlaim-llm  (no oideachais-llm)

# Secret resolution
infisical secrets get API_KEY \
  --projectId "$INFISICAL_PROJECT_ID" \
  --env dev-baile \
  --path cianfhoghlaim-llm
# Expect: a real API key, not a 404

# Compose stack can pull the secrets
docker compose -f bonneagar/stacks/cianfhoghlaim/compose.yaml config --quiet
# Expect: silent success (locket dependency is a warning, not an error)
```

## Acceptance gate for Stage 10

Stage 10 is considered complete when **all three** of these are true:

1. `infisical folders list ... | grep oideachais-llm` returns no matches.
2. `bun run scripts/init-vault.ts` exits 0 with no errors.
3. The `cianfhoghlaim` stack can boot on `bunchloch` (Komodo procedure
   `deploy-cianchfhoghlaim-bunchloch` — note the historical typo in
   the filename preserved per the A2 proposal) without any
   `INFISICAL_RESOLUTION_FAILED` errors in the Locket sidecar logs.

## Related changes

- `openspec/changes/2026-08-01-bonneagar-iac-namespace-alignment-v1/` —
  the parent A2 change
- `openspec/changes/2026-07-29-2026-07-26-biep-v3-root-namespace-rename-v1/` —
  the cianfhoghlaim-side rename (already archived)
- Commit `b824dd921` — the bulk IaC rename commit (July 29 2026)
- Commit `b3535ba36` — the lakehouse reproducible-deploy fix
  (introduced a YAML indentation bug in
  `bonneagar/stacks/lakehouse/compose.yaml:154`; unrelated to this
  change — tracked separately as a follow-up issue)