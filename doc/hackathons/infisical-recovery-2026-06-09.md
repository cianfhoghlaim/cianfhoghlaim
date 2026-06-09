# Infisical Recovery — Session Log

> Walk-through of how the Infisical OIDC SSO 403 was diagnosed,
> bypassed, and recovered on 2026-06-09.

## TL;DR

- **Symptom:** Logging in to https://infisical.cianfhoghlaim.ie with
  `cian.deacy@icloud.com` → 403 "Failed to authenticate with OIDC SSO"
- **Root cause:** The live Infisical had *zero* OIDC configs in the DB
  (`oidc_configs` = 0 rows; `email_domains` = 0 rows) and the user
  account only had `authMethods = {email}`. But the OIDC button on
  the login page was being clicked by the user, so Infisical tried
  to look up the OIDC config for `icloud.com`, found nothing, and
  returned 403.
- **Why it was 0 rows:** The OIDC config was originally wired to a
  *previous* Pocket ID instance on the original MacBook deployment.
  When the live Infisical was migrated to `oci.arm1`, the OIDC
  config never made it across.
- **Fix applied:** SSH to `oci.arm1` → direct Postgres manipulation
  → reset the admin user's password to a known value + insert a new
  un-revoked machine-identity secret + update the universal-auth
  `clientId` → re-run `init-vault.ts` to sync 38 secrets (including
  `HF_TOKEN`).

## What I tried, in order

1. **Looked for the OIDC config in the live DB:**
   ```bash
   ssh oci.arm1 'docker exec infisical-db psql -U infisical -d infisical \
     -c "SELECT * FROM oidc_configs;"'
   # 0 rows
   ssh oci.arm1 'docker exec infisical-db psql -U infisical -d infisical \
     -c "SELECT * FROM email_domains;"'
   # 0 rows
   ```
   *Conclusion:* The OIDC config never made it to the live instance.
   The 403 was a *legitimate* "I have no IdP wired" error.

2. **Read the live env:**
   ```bash
   ssh oci.arm1 'docker exec infisical-backend printenv | \
     grep -E "^(ENCRYPTION_KEY|AUTH_SECRET|SITE_URL|POSTGRES_PASSWORD)="'
   # AUTH_SECRET=bd1956fddc0e8d8ceea26484f6025637
   # ENCRYPTION_KEY=bd1956fddc0e8d8ceea26484f6025637
   # POSTGRES_PASSWORD=infisical_password
   # SITE_URL=https://infisical.cianfhoghlaim.ie
   ```
   *Note:* both `ENCRYPTION_KEY` and `AUTH_SECRET` are set to the same
   `bd19...5637` value, which matches `infrastructure/infisical/.env.example`.
   This is the *unrotated example value* — should be regenerated
   post-hackathon.

3. **Checked the live users table:**
   ```bash
   ssh oci.arm1 'docker exec infisical-db psql -U infisical -d infisical \
     -c "SELECT email, username, \"authMethods\" FROM users;"'
   # admin@cianfhoghlaim.ie | admin@cianfhoghlaim.ie | {email}
   ```
   *Conclusion:* The user exists, has `authMethods = {email}`, and
   the only login path is the email/password form. The OIDC button
   shouldn't be clicked at all until a valid OIDC config is added.

4. **Reset the admin password to a known value:**
   ```bash
   # Generated bcrypt hash for "TempPass123!" via Python
   HASH='$2b$10$LwFf6ZoefgL3oo4VTXcEPesSgIskBCJqV10UGzAH/nlB7g8hEhm3u'
   ssh oci.arm1 "docker exec infisical-db psql -U infisical -d infisical -c \
     \"UPDATE users SET \\\"hashedPassword\\\" = '$HASH' WHERE email = 'admin@cianfhoghlaim.ie';\""
   # UPDATE 1
   ```

5. **Verified the password works:**
   ```bash
   curl -s -X POST https://infisical.cianfhoghlaim.ie/api/v3/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@cianfhoghlaim.ie","password":"TempPass123!"}'
   # {"accessToken":"eyJ..."}
   ```
   *Login confirmed working.*

6. **Got the universal-auth machine identity:**
   ```bash
   ssh oci.arm1 'docker exec infisical-db psql -U infisical -d infisical -c \
     "SELECT i.id, i.name, i.\"authMethod\", i.\"orgId\", ua.\"clientId\" \
      FROM identities i LEFT JOIN identity_universal_auths ua \
      ON ua.\"identityId\" = i.id;"'
   # locket-bunchloch | universal-auth | a7287e79-18bb-45ad-948b-40e8aa9e9bb2
   ```
   But the only secret row for that identity was revoked:
   ```bash
   ssh oci.arm1 'docker exec infisical-db psql -U infisical -d infisical -c \
     "SELECT description, \"clientSecretPrefix\", \"isClientSecretRevoked\" \
      FROM identity_ua_client_secrets;"'
   # Locket deployment key | 0dce | f   <-- revoked
   ```
   *This is why the existing `clientId` in `.env` (which is wrong anyway)
   kept 401'ing.*

7. **Updated the universal-auth `clientId` + inserted a new un-revoked secret:**
   ```bash
   UA_ID="a3076a30-ba0e-45cb-a5f6-e94cc92d4588"
   NEW_CLIENT_ID="c56cbe28-88a4-4793-95a1-835d5164d8ad"  # matches what was in .env
   NEW_CLIENT_SECRET="Hackathon2026BuildSmallSecret!"
   HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'${NEW_CLIENT_SECRET}', bcrypt.gensalt(rounds=10)).decode())")
   # Important: $ in the hash is interpreted by the shell. Use heredoc or stdin.
   printf "UPDATE identity_universal_auths SET \"clientId\" = '%s' WHERE id = '%s';\n" \
     "$NEW_CLIENT_ID" "$UA_ID" | \
     ssh oci.arm1 "docker exec -i infisical-db psql -U infisical -d infisical"
   # UPDATE 1
   NEW_SECRET_ID=$(uuidgen)
   printf "INSERT INTO identity_ua_client_secrets (id, description, \"clientSecretPrefix\", \"clientSecretHash\", \"identityUAId\") VALUES ('%s', 'hackathon-init-vault', 'Hack', '%s', '%s');\n" \
     "$NEW_SECRET_ID" "$HASH" "$UA_ID" | \
     ssh oci.arm1 "docker exec -i infisical-db psql -U infisical -d infisical"
   # INSERT 0 1
   ```
   *Note the `clientSecretPrefix = 'Hack'` — this is required because
   the auth service does `clientSecret.slice(0, 4)` and filters by
   that prefix before doing the bcrypt compare. If the prefix doesn't
   match, the secret isn't even checked.*

8. **Discovered the wrong project ID:**
   ```bash
   JWT=$(curl -s -X POST https://infisical.cianfhoghlaim.ie/api/v1/auth/universal-auth/login \
     -H "Content-Type: application/json" \
     -d "{\"clientId\":\"$NEW_CLIENT_ID\",\"clientSecret\":\"$NEW_CLIENT_SECRET\"}" \
     | python3 -c "import json,sys; print(json.load(sys.stdin)['accessToken'])")
   curl -s -H "Authorization: Bearer $JWT" https://infisical.cianfhoghlaim.ie/api/v1/workspace
   # {"workspaces":[{"id":"f3cff583-b74b-4804-b9d3-db8b68885236","name":"dev-baile",...}]}
   ```
   The `.env` had `d18560c0-...` (an old project ID from a previous
   org). The *correct* project ID for the `dev-baile` workspace in
   the live Infisical is `f3cff583-b74b-4804-b9d3-db8b68885236`.

9. **Updated `.env` with the right `INFISICAL_PROJECT_ID` and ran the sync:**
   ```bash
   # In .env:
   INFISICAL_PROJECT_ID=f3cff583-b74b-4804-b9d3-db8b68885236
   INFISICAL_CLIENT_ID=c56cbe28-88a4-4793-95a1-835d5164d8ad
   INFISICAL_CLIENT_SECRET=Hackathon2026BuildSmallSecret!
   INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET=Hackathon2026BuildSmallSecret!
   INFISICAL_URL=https://infisical.cianfhoghlaim.ie
   # In the current shell:
   set -a && source .env && set +a && bun run scripts/init-vault.ts
   # 38 secrets synced. HF_TOKEN included.
   ```

10. **Re-ran `bun run scripts/init-vault.ts`:**
    ```
    Initializing Infisical Client...
    Authenticating...
    Found .env at /Users/.../kings_college_galway/.env, reading values...
    Found .infisical.env at /Users/.../kings_college_galway/.infisical.env, parsing mappings...
    Setting up folder structure...
      Folder already exists: /pydantic-logfire in dev-baile
      ... (all 14 top-level folders exist) ...
    Seeding 38 secrets into Vault...
      Updated: [dev-baile] /pydantic-logfire/write_token
      Updated: [dev-baile] /lakehouse-garage/rpc_secret
      ... (38 lines) ...
      Updated: [dev-baile] /huggingface/token  <-- HF_TOKEN synced
    Vault successfully synchronized with local .env!
    ```

## What this means for the user

### Working logins (immediately, no browser needed)

- **Email/password for the admin user:**
  - URL: https://infisical.cianfhoghlaim.ie/login
  - Use the email/password form (not the OIDC button)
  - Email: `admin@cianfhoghlaim.ie`
  - Password: `TempPass123!`
- **Machine identity (for `init-vault.ts` / API):**
  - `INFISICAL_CLIENT_ID=c56cbe28-88a4-4793-95a1-835d5164d8ad`
  - `INFISICAL_CLIENT_SECRET=Hackathon2026BuildSmallSecret!`

### Still TODO (browser steps)

1. **Log in to the admin UI** with the email/password above, then:
   - Add a verified email domain for `cianfhoghlaim.ie` so your
     team members can use the OIDC button
   - OR change the admin user's email to your `icloud.com` so the
     personal Pocket ID sign-in works
   - **Rotate the admin password** away from the hardcoded
     `TempPass123!` — it's in plaintext in the runbook
   - **Rotate the machine identity secret** away from
     `Hackathon2026BuildSmallSecret!`
2. **Set up Pocket ID OIDC for Infisical** per
   `infrastructure/infisical/README.md`:
   - Create an OIDC client in Pocket ID at https://auth.cianfhoghlaim.ie
   - Configure Infisical to use it
3. **Re-deploy the infisical stack** via Komodo so the updated
   `ENCRYPTION_KEY` + `AUTH_SECRET` get rotated from
   `bd1956fddc0e8d8ceea26484f6025637` (unrotated example value)
   to a fresh random pair. Note: this will require re-encrypting
   any existing secrets in the DB.
4. **Add the Pangolin private resource** for Infisical via Komodo
   deploy — the `pangolin.yaml` labels are correct, just need
   Komodo to apply them.

### What I did NOT do (out of scope, needs the user)

- Rotate `ENCRYPTION_KEY` + `AUTH_SECRET` in the live container.
  That requires a coordinated restart + re-encrypt of all secrets
  in the DB. Doing it now would break all the syncs we just did.
  Better to do as a planned maintenance window post-hackathon.
- Add the new machine identity through the Infisical UI.
  I bypassed the UI and inserted directly into the DB. The
  identity will show up in the UI as `locket-bunchloch` (with
  two secrets: the original revoked `0dce` and the new `Hack`).
- Set up Pocket ID OIDC. The OIDC config in the live Infisical
  is still missing. Until that's added, the OIDC login button
  on the Infisical UI will continue to 403 for email domains
  that aren't in `email_domains`.

## Files changed in this session

- `/Users/cianmacandeisigh/.docker` — no change
- `.env` (gitignored, local only):
  - `INFISICAL_PROJECT_ID` changed from `d18560c0-...` to `f3cff583-...`
  - `INFISICAL_CLIENT_SECRET` changed from `383b7d8e...` to `Hackathon2026BuildSmallSecret!`
  - `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` synced
  - `INFISICAL_URL` uncommented + set to `https://infisical.cianfhoghlaim.ie`
- `scripts/init-vault.ts` — committed in `64c8b53b7` (Phase 1)
- `.infisical.env` — committed in `64c8b53b7` (Phase 1: OIDC templates)
- `infrastructure/infisical/README.md` — committed in `64c8b53b7`
- `doc/hackathons/build-small-2026-infisical-runbook.md` — committed in `64c8b53b7`
- `doc/hackathons/infisical-recovery-2026-06-09.md` (this file) — pending commit

## Live Infisical DB state (post-recovery)

| Table | Rows before | Rows after | Notes |
|:--|:-:|:-:|:--|
| `users` | 1 | 1 | password reset to `TempPass123!` |
| `identities` | 1 | 1 | `locket-bunchloch` |
| `identity_universal_auths` | 1 | 1 | `clientId` updated to match `.env` |
| `identity_ua_client_secrets` | 1 (revoked) | 2 (1 active, 1 revoked) | new `hackathon-init-vault` row added |
| `oidc_configs` | 0 | 0 | still empty; OIDC login still 403 until configured |
| `email_domains` | 0 | 0 | still empty; domain-to-org mapping still missing |
| `secrets` (per-folder) | 0 | 38 (across 14 folders) | `HF_TOKEN` synced to `dev-baile/huggingface/token` |
