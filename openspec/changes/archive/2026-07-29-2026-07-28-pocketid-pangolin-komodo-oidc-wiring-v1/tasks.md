# Tasks: 2026-07-28-pocketid-pangolin-komodo-oidc-wiring-v1

## 1. Build the wire-pocketid-pangolin-komodo.sh script

- [x] 1.1 Write the bash script (~300 lines) with all 6 steps
- [x] 1.2 Add argument parsing (--dry-run, --force, --skip-komodo, --skip-pangolin, --domain, --pocketid-*, --pangolin-*, --komodo-*, -h/--help)
- [x] 1.3 Add idempotency checks (each step checks for existing state first)
- [x] 1.4 Add audit record write to /tmp/wire-pocketid-pangolin-komodo-{ts}.json
- [x] 1.5 Test the script end-to-end: dry-run + skip-komodo + actual run created Pocket ID client id=1f3434cb-... with secret written to .env

## 2. Add Pangolin IDP methods to the bons IaC client

- [x] 2.1 Add listIdps() to GET /api/v1/idp?org_id=...
- [x] 2.2 Add createIdp(opts) to POST /api/v1/idp (OAuth2OIDC, OAuth2Generic, SAML)
- [x] 2.3 Add deleteIdp(idpId) to DELETE /api/v1/idp/{idp_id}?org_id=...

## 3. Refactor the bons IaC wire-pocketid-as-oidc.ts

- [x] 3.1 Replace the 330-line TypeScript implementation with a 100-line TypeScript wrapper that shells out to the bash script
- [x] 3.2 Preserve the bun run iac:wire-pocketid-as-oidc UX from package.json
- [x] 3.3 Add proper error handling + audit record reading

## 4. Create the onboarding runbook

- [x] 4.1 Write deploy-runbooks/pocketid-pangolin-komodo-onboarding.md
- [x] 4.2 Document the exact Pocket ID config values (issuer, discovery URL, client_id, etc.)
- [x] 4.3 Document verification commands
- [x] 4.4 Document prerequisites (what the .env needs)
- [x] 4.5 Document the "for non-technical users" path

## 5. Test end-to-end + commit + push

- [x] 5.1 Run the script with --dry-run
- [x] 5.2 Run the script with --skip-komodo (since we don't have Komodo on this Mac)
- [x] 5.3 Verify the .env was updated with KOMODO_OIDC_CLIENT_ID + _SECRET
- [x] 5.4 Verify the audit record was created
- [x] 5.5 Commit + push the changes

## 6. Out-of-scope (for future changes)

- [ ] 6.1 Wire the Pangolin Resource IdP (4th manual step)
- [ ] 6.2 Rotate the bons-iac OIDC client secret every 90 days
- [ ] 6.3 Wire Komodo + Periphery from the get-go (so deployments self-configure)
- [ ] 6.4 Onboard less-technical users via a guided wizard
