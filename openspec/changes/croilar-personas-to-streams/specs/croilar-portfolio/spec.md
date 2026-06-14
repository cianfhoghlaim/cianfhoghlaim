# Spec Delta: `croilar-portfolio`

## MODIFIED Requirements

### Requirement: 9 Subproject Routes (preserved; no UI route changes)

The system SHALL continue to expose 9 subproject routes at the public root.

#### Scenario: Music route renders (preserved)

- **WHEN** a visitor navigates to `/music`
- **THEN** the music page SHALL render embedded Spotify/SoundCloud/YouTube players for the artist's catalogue
- **AND** the page SHALL show audio analytics (tempo, energy, danceability) extracted via BAML from DLT pipelines
- **AND** the data SHALL come from the `music` stream in the Stream registry (previously: the `aleyum` persona)

#### Scenario: Code route renders (modified)

- **WHEN** a visitor navigates to `/code`
- **THEN** the code page SHALL render the GitHub repos for the author
- **AND** the GitHub username SHALL be `cianfhoghlaim` (consolidated from the legacy `Yedya` alias that was the `aleyum` persona's GitHub identity)
- **AND** the data SHALL come from the `teaching` stream's `github` source (the new Stream-registry model: one canonical GitHub identity per owner, not per persona)

#### Scenario: Research route renders (modified)

- **WHEN** a visitor navigates to `/research`
- **THEN** the research page SHALL render the author's publications and projects
- **AND** the page SHALL include data from the new `researchgate` source on the `teaching` stream
- **AND** the author display name SHALL be "Cian Mac an Déisigh Uí Liatháin" (canonical owner display name from the Stream registry)

### Requirement: Image Management (preserved)

The system SHALL process and serve all images via the croilar-assets R2 bucket + sharp pipeline.

#### Scenario: Image upload processed (preserved)

- **WHEN** an image is added to `croilar/web/public/images/`
- **THEN** the build-time sharp pipeline SHALL compress it to 3 sizes (thumbnail 200px, card 800px, full 1920px) and convert to WebP
- **AND** upload the 3 sizes to `croilar-assets/{category}/{slug}/{size}.webp`
- **AND** the site SHALL reference the CDN URL `https://assets.iomha.cianfhoghlaim.ie/{category}/{slug}/{size}.webp`

#### Scenario: R2 bucket created (preserved)

- **WHEN** the first image is uploaded
- **THEN** the `croilar-assets` R2 bucket SHALL be created (idempotent)

### Requirement: Deployment (preserved)

The system SHALL deploy `croilar/web` to Cloudflare Pages.

#### Scenario: Cloudflare Pages deploy (preserved)

- **WHEN** the build completes
- **THEN** `wrangler pages deploy .output/public` SHALL push the static site to Cloudflare Pages
- **AND** the site SHALL be reachable at `iomha.cianfhoghlaim.ie`

### Requirement: PII Handling (preserved)

The system SHALL encrypt PII (identity documents) at rest using SOPS.

#### Scenario: Identity documents encrypted (preserved)

- **WHEN** a PDF is added to `croilar/identity/raw/`
- **THEN** the file SHALL be GPG-encrypted with the croilar-encryption key from Infisical
- **AND** only the `verification_metadata.json` (non-PII summary) SHALL be committed to git
- **AND** runtime decryption SHALL require Pocket ID OIDC authentication via the Pangolin private resource

### Requirement: Stream-Driven Notebooks (new)

The system SHALL organise marimo notebooks under `croilar/notebooks/streams/<stream-id>/` keyed by Stream id, not by persona.

#### Scenario: Notebook paths are stream-keyed

- **WHEN** the build runs `bun run notebook:wasm`
- **THEN** the marimo export step SHALL emit `public/wasm/music/`, `public/wasm/teaching/`, etc. — one directory per Stream id
- **AND** the legacy `notebook:wasm:aleyum` / `notebook:wasm:cianfhoghlaim` package.json keys SHALL be replaced by `notebook:wasm:music` / `notebook:wasm:teaching`
- **AND** the persona-keyed notebook directories (`notebooks/aleyum/`, `notebooks/cianfhoghlaim/`) SHALL NOT exist after the migration

#### Scenario: Portal analytics routes use stream ids

- **WHEN** the portal `/analytics` route renders
- **THEN** the MotherDuck dive URLs SHALL be keyed by Stream id — `music`, `teaching`, `cv`, `research` — and SHALL NOT contain the literal strings `aleyum`, `cianfhoghlaim`, or `carlcashman`

### Requirement: i18n Resources Are Stream-Keyed (new)

The system SHALL organise i18n resources under `croilar/packages/i18n/src/resources/streams/<stream-id>/{en,ga}/persona.json`.

#### Scenario: i18n imports use stream ids

- **WHEN** `croilar/packages/i18n/src/index.ts` is loaded
- **THEN** the resource map SHALL be keyed by Stream id
- **AND** the persona-keyed imports `aleyum` / `cianfhoghlaim` SHALL NOT exist in the data-layer code
- **AND** the persona-keyed directories `resources/aleyum/`, `resources/cianfhoghlaim/` SHALL NOT exist after the migration

#### Scenario: Tenant aliases preserved for UI branding

- **WHEN** the portal renders a tenant-branded page (OG image, favicon, email)
- **THEN** the tenant alias `aleyum` or `cianfhoghlaim` MAY be used for the visual branding
- **AND** this alias SHALL come from `Stream.owner`, not be a hard-coded literal in the data layer
- **AND** the body class SHALL be `tenant-<owner>` (e.g. `tenant-cianfhoghlaim`)

## REMOVED Requirements

### Requirement: Persona-Coupled i18n Bundle

**Reason**: The persona-keyed i18n bundle (`packages/i18n` resources at `aleyum/`, `cianfhoghlaim/`) conflated owner identity with translation scope. Translations belong to a stream (what kind of work), not a persona (who owns it). The bundle is replaced by the stream-keyed layout under `resources/streams/<id>/{en,ga}/`.

**Migration**: The migration script `croilar/scripts/migrate-personas-to-streams.ts` moves `resources/aleyum/{en,ga}/persona.json` → `resources/streams/music/{en,ga}/persona.json` and `resources/cianfhoghlaim/{en,ga}/persona.json` → `resources/streams/teaching/{en,ga}/persona.json`. The TypeScript import map in `packages/i18n/src/index.ts` is rewritten to key on Stream id.
