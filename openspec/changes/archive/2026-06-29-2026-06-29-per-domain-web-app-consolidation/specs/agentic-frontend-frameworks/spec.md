# Delta: agentic-frontend-frameworks

## ADDED Requirements

### Requirement: hono-api path consolidation

The `hono-api` backend at `cianfhoghlaim/web/hono-api/hono-api/` SHALL be moved to `cianfhoghlaim/web/hono-api/` to dedupe the doubled path that was residue from the 2026-06-28 v4 consolidation. The hono-api SHALL continue to host the BetterAuth OIDC issuer at `/.well-known/openid-configuration`, the JWKS public keys at `/.well-known/jwks.json`, the health check at `/api/health`, and the BetterAuth handler at `/api/auth/*` (sign-in, sign-up, sign-out, etc.). The 3 OIDC audiences SHALL be `convex_backend` (Convex), `croilar_web` (croilar-web app), and `croilar_portal` (croilar-portal app).

#### Scenario: the hono-api is mounted at the consolidated path

- **GIVEN** the v4 consolidation left a doubled `web/hono-api/hono-api/` path
- **WHEN** the developer runs `bun run dev` from `web/hono-api/`
- **THEN** the Hono server starts on port 4000
- **AND** `curl http://localhost:4000/.well-known/jwks.json` returns a valid JWKS payload

### Requirement: BetterAuth client in web/packages/packages/auth/

The empty `web/packages/packages/auth/src/index.ts` (currently `export {};`) SHALL be populated with a BetterAuth client that wraps the hono-api's `auth.ts` configuration. The client SHALL use `better-auth/react` for the React-side and `better-auth/client` for the vanilla JS side. The client SHALL read `PUBLIC_AUTH_URL` from the environment (default `http://localhost:4000`) and SHALL export a typed `Auth` instance.

#### Scenario: croilar-web imports @croilar/auth

- **GIVEN** the @croilar/auth package is populated
- **WHEN** a croilar-web component does `import { auth } from "@croilar/auth"`
- **THEN** the auth instance is available
- **AND** `auth.signIn.email(...)` calls `POST /api/auth/sign-in/email` on the hono-api
