# mailcow-dockerized

## Purpose for the Cianfhoghlaim project

Mailcow is an open-source, Docker-based email server suite providing a complete self-hosted email infrastructure. It includes Postfix (SMTP), Dovecot (IMAP), SOGo (webmail/groupware), Rspamd (spam filtering), ClamAV (antivirus), and more — all managed through a single administrative web UI.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/mailcow-dockerized/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: `https://mailcow-dockerized.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
