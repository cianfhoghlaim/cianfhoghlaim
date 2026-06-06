# `@croilar/hono-api` — BetterAuth + Hono

Self-hosted BetterAuth OIDC issuer for the Croílár multi-persona platform.

## What this does

Hosts BetterAuth at `auth.croilar.cianfhoghlaim.ie` (or `localhost:4000` in dev).
Issues JWTs to:

- **Convex** (`convex.croilar.cianfhoghlaim.ie`) — audience `convex_backend`
- **Web app** (`croilar.cianfhoghlaim.ie`) — audience `croilar_web`
- **Portal** — same as web, with org-scope checks

Validates JWTs in middleware for protected routes (`/api/me`, `/api/admin/*`).

## Architecture

```
Browser                    Hono (this)                   Convex
   │                          │                            │
   ├──── GET /api/auth/sign-in/email ──▶ BetterAuth         │
   │                          │                            │
   ├──── POST email + password ──▶│                          │
   │                          │ issue JWT                  │
   │◀── Set-Cookie + JWT ──────┤ (RS256, jwks_uri=/.well-known/jwks.json)
   │                          │                            │
   ├──── Authorization: Bearer JWT ────────▶                │
   │                                                       validate via jwks
   │                                                  ctx.auth.getUserIdentity()
   │                                                       │
   ├── requireOrg("aleyum") middleware ──▶ auth.api.listOrganizations
   │     (checks membership)            (Drizzle → Postgres)
   │◀── 403 Forbidden if not member ◀───┤
```

## Endpoints

### Public

| Method | Path | Purpose |
|:--|:--|:--|
| `GET` | `/.well-known/openid-configuration` | OIDC discovery |
| `GET` | `/.well-known/jwks.json` | JWKS public keys (Convex validates with these) |
| `GET` | `/api/health` | Health check |
| `ALL` | `/api/auth/*` | BetterAuth handler (sign-in, sign-up, sign-out, session, oauth2/callback, etc.) |

### Protected (require Bearer JWT)

| Method | Path | Org guard | Purpose |
|:--|:--|:--|:--|
| `GET` | `/api/me` | (any auth) | Current user session |
| `GET` | `/api/admin/stacks` | `croilar-admin` | (PR-4a) Komodo stack health |

## Database

Uses Drizzle against the local `croilar-postgres` stack (or PlanetScale in prod).
Schema:

- `better_auth.user` — user identity
- `better_auth.session` — active sessions
- `better_auth.account` — provider accounts (email, github, google)
- `better_auth.verification` — email verification tokens
- `better_auth.organization` — the 4 orgs (aleyum, cianfhoghlaim, croilar-admin, croilar-collab)
- `better_auth.member` — user ↔ org membership with role
- `better_auth.invitation` — pending invites
- `better_auth.jwks` — RS256 signing keys for OIDC

Schemas are auto-created in `better_auth` namespace on first migrate.

## Migrations

```bash
# Generate from schema
bun run db:generate

# Apply against local Postgres
bun run db:migrate

# Push schema without migrations (dev only)
bun run db:push
```

## Local development

```bash
# 1. Start the local Postgres stack
docker compose -f infrastructure/stacks/storage/croilar-postgres/compose.yaml \
               -f infrastructure/stacks/storage/croilar-postgres/sidecar.yaml \
               --env-file infrastructure/stacks/storage/croilar-postgres/secrets.env \
               up -d

# 2. Set up env
cp .env.example .env
# Edit .env with real values

# 3. Migrate
bun run db:migrate

# 4. Run
bun run dev
```

The API will be at `http://localhost:4000`.

## Multi-tenant org model

The 4 orgs are created on first login via `auth.api.createOrganization`:

| Slug | Visibility | Who can join |
|:--|:--|:--|
| `aleyum` | Public | Author + invited collaborators |
| `cianfhoghlaim` | Public | Author + invited collaborators |
| `croilar-admin` | Private | Author only (portal write access) |
| `croilar-collab` | Private | Invited collaborators (portal read-only) |

Membership is enforced at the API layer via `requireOrg()` middleware. The Convex layer enforces it again via `requireOrg()` in `convex/helpers.ts`.
