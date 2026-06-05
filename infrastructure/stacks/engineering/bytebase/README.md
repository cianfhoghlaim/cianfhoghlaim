# Bytebase — Database CI/CD

SQL review + GitOps for the 6 schemas in the PlanetScale "bunchloch" database.

## Deploy via Komodo (arm1-oci)
```bash
komodo-cli deploy bytebase --server arm1-oci
```

## Connect to PlanetScale
1. Open `https://bytebase.cianfhoghlaim.ie`
2. Add instance → PostgreSQL
3. Host: `eu-west-3.pg.psdb.cloud`, Port: `5432`, Database: `bunchloch`
4. Use PlanetScale credentials from Infisical: `PLANETSCALE_USERNAME` / `PLANETSCALE_PASSWORD`
5. SSL mode: `require`
6. Bytebase auto-discovers the 6 schemas: `vikunja`, `n8n`, `calcom`, `paperless`, `glance`, `changedetect`

## Connection fallback
If PlanetScale is unreachable, add the self-hosted Postgres at `infisical-db:5432` as a fallback instance.

## Features
- SQL review with approval workflow
- GitOps migration (sync from `infrastructure/stacks/*/migrations/`)
- Schema drift detection
- Point-in-time recovery (via PlanetScale branching)
- VCS integration (Forgejo + GitHub)

## See also
- `infrastructure/stacks/infrastructure/planetscale/schemas/bunchloch.sql` — initial schema DDL
- `scripts/setup-planetscale.sh` — idempotent schema bootstrap
