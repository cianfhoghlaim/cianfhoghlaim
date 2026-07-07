# `croilar-portfolio` spec delta — MODIFIED for multi-persona

## MODIFIED Requirements

### Requirement: Multi-Persona Routing
The system SHALL serve N personas at subpath routes under a single domain, with per-persona theme, i18n, and content.

#### Scenario: Persona routes resolve
- **WHEN** a visitor navigates to `/aleyum`
- **THEN** the aleyum persona home page SHALL render with the aleyum theme (dark mode, electric violet accent), aleyum i18n labels, and aleyum-specific data sources (Spotify, SoundCloud, GitHub)
- **AND** the page SHALL be in English by default with a GA (`ga`) alternate

#### Scenario: Second persona routes resolve
- **WHEN** a visitor navigates to `/cianfhoghlaim`
- **THEN** the cianfhoghlaim persona home page SHALL render with the cianfhoghlaim theme (light mode, celtic green accent), cianfhoghlaim i18n labels, and cianfhoghlaim-specific data sources (CV/teaching PDFs, oideachais cross-links, publications)

#### Scenario: Unknown persona returns 404
- **WHEN** a visitor navigates to `/unknown-persona`
- **THEN** the app SHALL return a 404 page with a link to the persona list

#### Scenario: Persona switcher available
- **WHEN** a visitor views any persona page
- **THEN** a persona switcher SHALL be visible in the global header
- **AND** selecting a persona SHALL persist in a cookie and swap theme + i18n

### Requirement: Persona Registry
The system SHALL define each persona in a type-safe registry file.

#### Scenario: Persona types are Zod-validated
- **WHEN** `bun run typecheck` is run
- **THEN** the `Persona` Zod schema in `personas/_schema.ts` SHALL validate `id`, `slug`, `i18n`, `theme`, `routes`, `dataSources`, `featureFlags`, `dagsterAssetGroup`, and `bamlSchemas`
- **AND** each registered persona in `_registry.ts` SHALL conform to the schema

#### Scenario: New persona added
- **WHEN** a new persona file is added at `personas/<id>.ts`
- **AND** registered in `_registry.ts`
- **THEN** the persona SHALL appear in the persona switcher, receive its own routes, and render with its specified theme

### Requirement: Server-Function Data Loaders
The system SHALL load all persona page data via typed server functions that query DuckDB.

#### Scenario: Home page loads real data
- **WHEN** a visitor navigates to a persona home page
- **THEN** a `createServerFn` SHALL query DuckDB for the persona's latest metadata
- **AND** the page SHALL NOT contain any hardcoded `PLACEHOLDER_*` arrays

#### Scenario: Music page loads from DuckDB
- **WHEN** a visitor navigates to `/aleyum/music`
- **THEN** a server function SHALL query `SELECT * FROM spotify_data.tracks WHERE artist_id = ? ORDER BY popularity DESC LIMIT 20`
- **AND** the `AudioCard` components SHALL render live data

#### Scenario: Code page loads from DuckDB
- **WHEN** a visitor navigates to a persona's code page
- **THEN** a server function SHALL query `SELECT * FROM github_data.repos ORDER BY stargazers_count DESC`

### Requirement: Per-Persona Theme Tokens
The system SHALL apply CSS theme tokens per persona via Tailwind 4 CSS-first configuration.

#### Scenario: Dark theme for aleyum
- **WHEN** the aleyum persona is active
- **THEN** the `:root` CSS custom properties SHALL include `--color-accent: oklch(0.74 0.18 285)` and `color-scheme: dark`

#### Scenario: Light theme for cianfhoghlaim
- **WHEN** the cianfhoghlaim persona is active
- **THEN** the `:root` CSS custom properties SHALL include `--color-accent: oklch(0.62 0.16 145)` and `color-scheme: light`

### Requirement: Bilingual Content per Persona
The system SHALL serve English and Irish translations scoped to each persona.

#### Scenario: Aleyum i18n bundle loads
- **WHEN** the aleyum persona is active
- **THEN** i18next SHALL load `packages/i18n/resources/aleyum/{en,ga}.json` for persona-specific labels

#### Scenario: Cianfhoghlaim i18n bundle loads
- **WHEN** the cianfhoghlaim persona is active
- **THEN** i18next SHALL load `packages/i18n/resources/cianfhoghlaim/{en,ga}.json`

## ADDED Requirements

### Requirement: Convex + Hono + BetterAuth Integration
The system SHALL provide full multi-tenant authentication via self-hosted BetterAuth OIDC, Hono API gateway, and Convex real-time backend.

#### Scenario: BetterAuth serves OIDC discovery
- **WHEN** a client requests `/.well-known/openid-configuration`
- **THEN** the Hono server SHALL return the OIDC discovery document with issuer, JWKS endpoint, and supported scopes

#### Scenario: Convex validates BetterAuth JWT
- **WHEN** a Convex function is called with a BetterAuth-issued JWT
- **THEN** Convex SHALL validate the token via BetterAuth's JWKS endpoint
- **AND** the caller's identity SHALL be available via `auth.getUser()`

#### Scenario: Multi-tenant org access control
- **WHEN** a user is auth'd as a member of the `aleyum` org
- **THEN** they SHALL access aleyum-specific Convex tables
- **AND** they SHALL NOT access cianfhoghlaim-specific tables

### Requirement: Public Read, Invite-Only Write
The system SHALL serve all persona pages as public read-only with auth gating only for the portal and private content.

#### Scenario: Public visitor views persona pages
- **WHEN** an unauthenticated visitor navigates to any persona page
- **THEN** the page SHALL render without prompting for authentication

#### Scenario: Invited collaborator accesses portal
- **WHEN** an invited collaborator signs in via BetterAuth
- **THEN** they SHALL access the `/portal` dashboard with role-restricted views
