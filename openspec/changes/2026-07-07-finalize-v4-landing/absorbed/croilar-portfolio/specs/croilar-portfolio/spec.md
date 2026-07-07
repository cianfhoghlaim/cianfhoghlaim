# `croilar-portfolio` capability spec (NEW)

The personal-portfolio subproject for Cian. Public TanStack Start site with 9 subprojects (Home, CV, Music, Code, Research, Teaching, Data, Identity, Contact) — bilingual (English + Irish) — served from Cloudflare Pages + R2.

## ADDED Requirements

### Requirement: 9 Subproject Routes
The system SHALL expose 9 subproject routes at the public root.

#### Scenario: Home route renders
- **WHEN** a visitor navigates to `/`
- **THEN** the home page SHALL render with name, photo, hero tagline, and links to all 9 subprojects
- **AND** the page SHALL be in English by default with an `ga` alternate

#### Scenario: CV route renders
- **WHEN** a visitor navigates to `/cv`
- **THEN** the CV page SHALL render sections for Education, Awards, Publications, References, Teaching, all extracted from BAML schemas over the source PDFs in `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/achievement/` and `teaching/`
- **AND** the page SHALL include a semantic search input over the extracted Markdown

#### Scenario: Music route renders
- **WHEN** a visitor navigates to `/music`
- **THEN** the music page SHALL render embedded Spotify/SoundCloud/YouTube players for the artist's catalogue
- **AND** the page SHALL show audio analytics (tempo, energy, danceability) extracted via BAML from DLT pipelines

#### Scenario: Code route renders
- **WHEN** a visitor navigates to `/code`
- **THEN** the code page SHALL render the GitHub repos for `@Yedya` sorted by stars + last-updated

#### Scenario: Research route renders
- **WHEN** a visitor navigates to `/research`
- **THEN** the research page SHALL render outputs cross-linked from `sruth/oideachais/` and `meaisínfhoghlaim/`, filtered by author "Cian de Búrca"
- **AND** the page SHALL link back to the originating monorepo subproject

#### Scenario: Teaching route renders
- **WHEN** a visitor navigates to `/teaching`
- **THEN** the teaching page SHALL render placements, student feedback, and curriculum designed, all extracted via BAML from teaching PDFs

#### Scenario: Data route renders
- **WHEN** a visitor navigates to `/data`
- **THEN** the data page SHALL render the live status of all 12+ Dagster pipeline assets (via Dagster GraphQL API)
- **AND** the page SHALL include links to the Dagster UI (private Pangolin resource)

#### Scenario: Identity route renders
- **WHEN** a visitor navigates to `/identity`
- **THEN** the identity page SHALL render verification metadata (Pangolin-protected)
- **AND** PII documents SHALL NOT be served — only their verification metadata
- **AND** the page SHALL require Pocket ID OIDC authentication

#### Scenario: Contact route renders
- **WHEN** a visitor navigates to `/contact`
- **THEN** the contact page SHALL render an end-to-end encrypted contact form
- **AND** form submissions SHALL be HMAC-signed and sent to a Hono Worker on Cloudflare

### Requirement: Image Management
The system SHALL process and serve all images via the croilar-assets R2 bucket + sharp pipeline.

#### Scenario: Image upload processed
- **WHEN** an image is added to `sruth/croilar/web/public/images/`
- **THEN** the build-time sharp pipeline SHALL compress it to 3 sizes (thumbnail 200px, card 800px, full 1920px) and convert to WebP
- **AND** upload the 3 sizes to `croilar-assets/{category}/{slug}/{size}.webp`
- **AND** the site SHALL reference the CDN URL `https://assets.iomha.cianfhoghlaim.ie/{category}/{slug}/{size}.webp`

#### Scenario: R2 bucket created
- **WHEN** the first image is uploaded
- **THEN** the `croilar-assets` R2 bucket SHALL be created (idempotent)

### Requirement: Deployment
The system SHALL deploy `sruth/croilar/web` to Cloudflare Pages.

#### Scenario: Cloudflare Pages deploy
- **WHEN** the build completes
- **THEN** `wrangler pages deploy .output/public` SHALL push the static site to Cloudflare Pages
- **AND** the site SHALL be reachable at `iomha.cianfhoghlaim.ie` (or `croilar.cianfhoghlaim.ie` — to be confirmed)

### Requirement: PII Handling
The system SHALL encrypt PII (identity documents) at rest using SOPS.

#### Scenario: Identity documents encrypted
- **WHEN** a PDF is added to `sruth/croilar/identity/raw/`
- **THEN** the file SHALL be GPG-encrypted with the croilar-encryption key from Infisical
- **AND** only the `verification_metadata.json` (non-PII summary) SHALL be committed to git
- **AND** runtime decryption SHALL require Pocket ID OIDC authentication via the Pangolin private resource
