# Spec Delta — Rebrand Edits (Awen Hub → Cianfhoghlaim Oideachais)

## ADDED Requirements

### Requirement: Web App Brand
The web app (`sruth/oideachais/web/apps/web`) SHALL be branded as **Cianfhoghlaim Oideachais** (not Awen Hub).

#### Scenario: Header Text
- **GIVEN** `sruth/oideachais/web/apps/web/src/components/Header.tsx`
- **WHEN** the file is read
- **THEN** the logo text is `CIANFHOGHLAIM OIDEACHAIS` (not `AWEN HUB`)
- **AND** the tagline is educational, not RPG-fantasy
- **AND** a `<TranslationToggle>` chip is rendered in the header

#### Scenario: Landing Page Heading
- **GIVEN** `sruth/oideachais/web/apps/web/src/routes/index.tsx`
- **WHEN** the file is read
- **THEN** the `<h1>` text is `Fáilte go Cianfhoghlaim Oideachais` (not `Welcome to Awen Hub`)

#### Scenario: Page Title
- **GIVEN** `sruth/oideachais/web/apps/web/src/routeTree.tsx`
- **WHEN** the file is read
- **THEN** the `<title>` is `Cianfhoghlaim Oideachais` (not `Awen Hub — Oideachais Education Engine`)

#### Scenario: Chat Component Rename
- **GIVEN** `sruth/oideachais/web/apps/web/src/components/AwenChat.tsx`
- **WHEN** the file is inspected
- **THEN** it has been renamed to `OideachasChat.tsx`
- **AND** the `routeTree.tsx` import is updated
- **AND** the component name in the React tree is `<OideachasChat>`
- **AND** the agent name in `<CopilotKit agent="oideachais-exam-explorer">` is updated to `oideachais-stage-explorer` (or `oideachais-oideachas-chat` for the multi-stage version)

### Requirement: Documentation Brand Consistency
The README and architecture docs SHALL use **Cianfhoghlaim Oideachais** consistently.

#### Scenario: README Title
- **GIVEN** `readme2.md`
- **WHEN** the file is read
- **THEN** the title is `# Cianfhoghlaim Oideachais` (not `# Cianfhoghlaim & Awen Hub`)
- **AND** the introductory paragraph references the **Cianfhoghlaim Oideachais** platform name only

#### Scenario: ARCHITECTURE_DEPLOYMENT
- **GIVEN** `docs/ARCHITECTURE_DEPLOYMENT.md` line 91
- **WHEN** the file is read
- **THEN** the section heading `Start the Awen Hub Frontend` is replaced with `Start the Cianfhoghlaim Oideachais web app`

#### Scenario: Agentic Education Platform Docs
- **GIVEN** `docs/web/frontend/agentic-platform.md` and `docs/sruth/tuatha/Agentic Education Platform Development.md`
- **WHEN** the files are read
- **THEN** references to `Awen Hub` are replaced with `Cianfhoghlaim Oideachais`
- **AND** the x402 / Anam token / "Learn-to-Earn" narrative is demoted to `docs/sruth/tuatha/` (where the MMO lives) and removed from the oideachais-themed docs

## REMOVED Requirements

### Requirement: Awen Hub Brand

**Reason**: The "Awen Hub" brand is shelved in favour of the canonical "Cianfhoghlaim Oideachais" project name. The MMO theme is moving to the `sruth/tuatha/` subproject; the oideachais web app is a bilingual educational platform.

**Migration**:
- All `Awen Hub` strings in 4 source files (`sruth/oideachais/web/apps/web/src/routes/index.tsx:5`, `routeTree.tsx:20`, `components/Header.tsx`, and `readme2.md`) are replaced with `Cianfhoghlaim Oideachais`.
- `AwenChat.tsx` is renamed to `OideachasChat.tsx` and the import in `routeTree.tsx` is updated.
- The MMORPG/x402 references in `docs/web/frontend/agentic-platform.md` and `docs/sruth/tuatha/Agentic Education Platform Development.md` are replaced with educational content.
- The PyPI package name `cianfhoghlaim-oideachais` is unchanged.
- The monorepo directory name `sruth/oideachais/` is unchanged.
