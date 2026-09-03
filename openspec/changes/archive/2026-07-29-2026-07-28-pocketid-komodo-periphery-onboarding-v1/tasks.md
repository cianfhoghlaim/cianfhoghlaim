# Tasks: 2026-07-28-pocketid-komodo-periphery-onboarding-v1

## 1. Build the onboard-pocketid.sh guided wizard

- [x] 1.1 Write the TUI/CLI script (231 lines, --help, --non-interactive modes)
- [x] 1.2 Add credential collection prompts (3 + optional extras)
- [x] 1.3 Add Pocket ID + Pangolin API key validation (live HTTP calls)
- [x] 1.4 Add .env upsert logic (idempotent)
- [x] 1.5 Add --skip-komodo / --skip-wire / --with-infisical flags
- [x] 1.6 Test --help + --non-interactive + verify the script runs end-to-end

## 2. Build the wire-pocketid-resource-idp.sh script

- [x] 2.1 Write the Resource IdP binding script (4th manual step)
- [x] 2.2 Add --resource=DOMAIN + --all flags
- [x] 2.3 Add --dry-run mode
- [x] 2.4 Add the PANGOLIN_ORG_ID + POCKETID_PANGOLIN_CLIENT_ID env validation
- [x] 2.5 Add the help check BEFORE the env validation (UX fix)
- [x] 2.6 Test the script's bash syntax + help flag

## 3. Build the bootstrap-komodo-periphery.sh script (5th step)

- [x] 3.1 Write the Komodo+Periphery bootstrap script
- [x] 3.2 Add the Periphery self-registration (Newt protocol)
- [x] 3.3 Add the .env cleanup for stale credentials
- [x] 3.4 Add the reachability checks for Komodo + Pangolin
- [x] 3.5 Add the audit record write

## 4. Build the rotate-pocketid-secrets.sh cron job

- [x] 4.1 Write the 90-day rotation script
- [x] 4.2 Use the refactored pocketIdLogin() (which fetches fresh secrets)
- [x] 4.3 Update .env with the new PANGOLIN_API_KEY
- [x] 4.4 Write the audit record to /tmp/pocketid-rotation-{ts}.json

## 5. Test end-to-end + commit + push

- [x] 5.1 Run onboard-pocketid.sh --help + --non-interactive (uses .env)
- [x] 5.2 Run wire-pocketid-resource-idp.sh --help
- [x] 5.3 Run bootstrap-komodo-periphery.sh (will skip steps that need live envs)
- [x] 5.4 Run rotate-pocketid-secrets.sh (will fail on stale creds but demonstrates the flow)
- [x] 5.5 Stage + commit + push all 4 scripts + this openspec change

## 6. Out of scope (for future changes)

- [ ] Test the Resource IdP binding (4th manual step) on a real Pangolin resource
- [ ] Add a wire-pocketid-pangolin-resource-idp.sh --komodo flag
- [ ] Add per-Periphery onboarding token (right now bootstrap uses Pocket ID but the Komodo side needs a separate API key)
- [ ] Add a guard for "Pangolin Resource already has PocketID bound" to prevent duplicate IdP bindings
- [ ] Add monitoring/alerting for failed rotations
