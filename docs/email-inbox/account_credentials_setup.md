# Email Inbox Pipeline — Per-Account Credential Setup

> **Manual one-time setup.** These credentials are created by the user
> (not programmatically) and stored into Infisical manually. The full
> setup takes ~30 minutes.

The `leabharlann-email-inbox-pipeline` change ingests email from 4
accounts via the Mailcow `dovecot_imapsync_runner`. Each account
needs:

1. An **App Password** generated at the provider (not the user's
   main password — providers require App Passwords for IMAP).
2. The App Password + the account email stored in Infisical under
   the `imapsync/<account>/{user,app_password}` keys.

The 4 accounts are:

| Account label | Provider | IMAP server | App Password how-to |
|:--|:--|:--|:--|
| `dkit_ie` | Microsoft 365 (Outlook) | `imap.outlook.com:993` | [Microsoft App Passwords](https://account.microsoft.com/security) |
| `gmail_personal` | Gmail (Google) | `imap.gmail.com:993` | [Google App Passwords](https://myaccount.google.com/apppasswords) |
| `gmail_academic` | Gmail (Google) | `imap.gmail.com:993` | [Google App Passwords](https://myaccount.google.com/apppasswords) |
| `hotmail_legacy` | Hotmail (Microsoft) | `outlook.office365.com:993` | [Microsoft App Passwords](https://account.microsoft.com/security) |

## 1. Microsoft 365 App Passwords (DKIT.ie + Hotmail Legacy)

### Prerequisites

- You have access to the DKIT.ie / Hotmail Microsoft account.
- 2FA is enabled on the account (App Passwords require 2FA).
- The DKIT.ie account is **not** a federated Azure AD account with
  conditional access that blocks App Passwords. (Some DKIT.ie
  accounts under IT-managed Conditional Access policies **do** block
  App Passwords. If yours does, see the OAuth fallback note at
  the bottom.)

### Steps

1. Sign in to <https://account.microsoft.com/security>.
2. Click **Advanced security options**.
3. Under **App passwords**, click **Create a new app password**.
4. Name it `Mailcow Cianfhoghlaim` (or similar).
5. Copy the 16-character generated password (shown once).
6. Store it in Infisical:
   - `imapsync/dkit_ie/app_password` (or
     `imapsync/hotmail_legacy/app_password`)
7. Also store the account email in:
   - `imapsync/dkit_ie/user` (e.g. `your.name@dkit.ie`)
   - `imapsync/hotmail_legacy/user` (e.g. `your.name@hotmail.com`)

## 2. Google App Passwords (Gmail Personal + Academic)

### Prerequisites

- 2-Step Verification is enabled on the Google account.
- The account is **not** under Google Workspace Advanced
  Protection (which blocks App Passwords).

### Steps

1. Sign in to <https://myaccount.google.com/apppasswords>.
2. Select app = **Mail**, device = **Other (custom name)** =
   `Mailcow Cianfhoghlaim`.
3. Click **Generate**.
4. Copy the 16-character generated password (shown once, with
   spaces — strip the spaces when storing in Infisical).
5. Store it in Infisical:
   - `imapsync/gmail_personal/app_password`
   - `imapsync/gmail_academic/app_password`
6. Also store the account email in:
   - `imapsync/gmail_personal/user`
   - `imapsync/gmail_academic/user`

## 3. Sync the secrets to local `.env`

After storing all 8 vault refs, run:

```bash
bun run secrets:init
```

This resolves every `infisical://dev-baile/imapsync/<account>/...`
reference into the local `.env` (gitignored) via Locket.

## 4. Verify the Mailcow container can poll

```bash
# From the bunchloch host (the stack runs there, not arm1-oci)
cd infrastructure/stacks/mailcow-dockerized
docker compose exec dovecot-mailcow bash -c "doveadm mailbox list -A"
# Expected output: a list of 4 Mailcow mailboxes (inbox-dkit_ie, inbox-gmail_personal, ...)
```

If the imapsync_runner log shows
`dovecot_imapsync_runner: <account> sync failed: Authentication
failed`, the App Password is wrong — regenerate per steps 1 or 2.

## 5. Mailbox naming convention

The Mailcow `dovecot_imapsync_runner` writes synced mail to
`inbox-<account>@cianfhoghlaim.ie`. The 4 mailbox names are
hard-coded in
`infrastructure/stacks/mailcow-dockerized/data/conf/dovecot/imapsync_runner.conf`
(also created in the `leabharlann-email-inbox-pipeline` change).

The downstream `mailcow-export` companion container reads
`/var/vmail/cianfhoghlaim.ie/inbox-<account>/` every 6 hours
and writes
`/srv/mailcow-exports/mailbox-<account>-<date>.mbox`.

## 6. OAuth fallback (for accounts that block App Passwords)

If a DKIT.ie account is under IT-managed Conditional Access that
blocks App Passwords (common in some Irish HEA institutions), the
fallback is to:

1. Use `offlineimap3` or `isync (mbsync)` with OAuth 2.0 on the
   bunchloch host to sync IMAP → local Maildir.
2. Then have the `mailcow-export` companion container read the
   local Maildir instead of (or in addition to) the
   imapsync_runner.

This fallback is **not** part of the v1 change. It's documented
here for future use; the change ships the App-Password path
because it's the simplest, most portable, and works for 3 of the
4 accounts out of the box.

## 7. Security notes

- The 4 App Passwords grant **read-only IMAP access** (no send
  capability, no mailbox-modification).
- The App Passwords are stored in Infisical (encrypted at rest)
  and in the local `.env` (file mode `0600`, gitignored).
- No email content is written to the repo. Only MBOX exports
  (under `/srv/mailcow-exports/`) and DuckLake rows (under
  `ducklake_cianfhoghlaim.inbox_*`) are persisted; both are
  Pangolin-private.
- The `gpg_encrypt_paths` knob in `author_archive_accounts.yaml`
  encrypts emails matching the `legal/`, `medical/`, `hsc/`, or
  `nhs/` path prefixes **before** the row is yielded to DuckLake.
- The Lakehouse stack (Garage S3 + Lakekeeper + Lance Namespace)
  is Pangolin-private and Pocket ID-gated; no public-domain
  access to email data.
