# Spec Delta: croilar-web

## ADDED Requirements

### Requirement: Real CV Data Sources
All CV-related pages SHALL source data from the hono-api backed by DuckDB/GitHub/Zotero:
- `cv/awards.tsx` SHALL load from `createServerFn` → hono-api `/api/v1/cv`
- `cv/education.tsx` SHALL load from `createServerFn` → hono-api `/api/v1/cv`
- `cv/publications.tsx` SHALL load from `createServerFn` → Zotero API
- `cv/references.tsx` SHALL load from `createServerFn` → hono-api `/api/v1/cv`

#### Scenario: CV page loads with real data
- **WHEN** user navigates to `/cv`
- **THEN** each section's server function fetches from the backend
- **AND** components render actual data instead of PLACEHOLDER_* arrays

### Requirement: Marimo WASM Music Analytics
The music route SHALL embed a Marimo WASM notebook that runs in-browser via Pyodide, loading the `notebook:wasm:aleyum` build output and displaying interactive audio analytics charts.

#### Scenario: Music analytics notebook loads
- **WHEN** user navigates to `/music`
- **THEN** the Marimo WASM notebook loads Pyodide and renders interactive charts
- **AND** audio visualizations display music catalog analytics
- **AND** the notebook is interactive (user can filter, sort, and explore)

### Requirement: BAML Research Query
The research route SHALL provide a BAML-powered semantic search via a `ResearchQuery` server function that calls `baml_src/curriculum_extraction.baml` with the user's query and renders structured results in `crosslinks.tsx`.

#### Scenario: Research query returns structured results
- **WHEN** user searches "Irish language education policy 2024" on the research page
- **THEN** server function runs the BAML `ResearchQuery` function
- **AND** returns structured results with title, source, date, and summary fields
- **AND** `crosslinks.tsx` renders each result as a clickable card linking to the source

### Requirement: Live Pipeline Status
The data route SHALL display live pipeline status by polling the hono-api `/api/v1/pipelines` endpoint every 30 seconds via `useQuery({ refetchInterval: 30000 })`, querying the Komodo API for pipeline stack statuses.

#### Scenario: Pipeline status card updates
- **WHEN** user navigates to `/data`
- **THEN** pipeline status component renders loading skeletons
- **AND** within 30 seconds, real status data loads showing each pipeline's name, group, and status (idle/running/success/failed)
- **AND** status auto-refreshes every 30 seconds without page reload

### Requirement: SIWE Identity Verification
The identity route SHALL support wallet-based identity verification via the `useSiweAuth()` hook, displaying the connected wallet's ENS name and avatar if resolved, with on-chain verification of the wallet address.

#### Scenario: Connect wallet on identity page
- **WHEN** user navigates to `/identity` and clicks "Connect Wallet"
- **THEN** SIWE auth flow initiates via Better Auth's `siwe` plugin
- **AND** on success, the verification card displays the wallet address (truncated)
- **AND** if ENS name is resolved, it displays alongside the ENS avatar

### Requirement: MCP Contact Form
The contact form SHALL submit through the MCP gateway via a `createServerFn`, with the option to trigger a Firecrawl MCP browse to a configured CRM link on successful submission, and display sent/error state with a Toast notification.

#### Scenario: Contact form submitted successfully
- **WHEN** user fills in name, email, and message on the contact form and clicks "Send"
- **THEN** server function calls the MCP gateway with the form data
- **AND** on success, a Toast notification shows "Message sent!"
- **AND** the form resets to its initial state

### Requirement: Bilingual i18n
The croilar/web app SHALL support Irish language via `@croilar/i18n`, which SHALL include a `ga.json` translations bundle with all user-facing strings, with language toggling via `i18next.useTranslation()` while keeping route paths language-agnostic.

#### Scenario: Switch to Irish
- **WHEN** user clicks the language toggle from EN to GA
- **THEN** `i18next.changeLanguage('ga')` is called
- **AND** all visible UI strings switch to their Irish translations
- **AND** the language preference persists in localStorage across page reloads

## MODIFIED Requirements

None — all existing pages keep their structure; only data sources change.

## REMOVED Requirements

### Requirement: PLACEHOLDER_* Constant Arrays
**Reason**: No longer needed; replaced by real server functions.
**Migration**: Each PLACEHOLDER_* replaced by a `createServerFn` with fallback to an empty array during loading.
