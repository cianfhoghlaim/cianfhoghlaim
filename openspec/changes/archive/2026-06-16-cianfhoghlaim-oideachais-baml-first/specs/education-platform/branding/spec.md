# Spec Delta — Cianfhoghlaim Oideachais Branding

## MODIFIED Requirements

### Requirement: Project Brand
The interactive web app (`oideachais/web/apps/web`) and all oideachais-themed documentation SHALL use the canonical brand **"Cianfhoghlaim Oideachais"** (not "Awen Hub").

#### Scenario: Web App
- **GIVEN** the user loads `http://localhost:3001/`
- **WHEN** the page is rendered
- **THEN** the page title is `Cianfhoghlaim Oideachais`
- **AND** the header text is `CIANFHOGHLAIM OIDEACHAIS`
- **AND** the landing page heading is `Fáilte go Cianfhoghlaim Oideachais` (with a `<TranslationToggle>` to switch to English)

#### Scenario: README
- **GIVEN** the user opens `readme2.md`
- **WHEN** the file is rendered
- **THEN** the title is `# Cianfhoghlaim Oideachais` (not `# Cianfhoghlaim & Awen Hub`)

#### Scenario: PyPI Package
- **GIVEN** the published PyPI package
- **WHEN** it is queried
- **THEN** the package name is `cianfhoghlaim-oideachais` (unchanged from before)
- **AND** the monorepo directory name is `oideachais/` (unchanged; the brand is at the user-facing layer only)

#### Scenario: Documentation
- **GIVEN** the user opens `docs/ARCHITECTURE_DEPLOYMENT.md` or `docs/web/frontend/agentic-platform.md`
- **WHEN** the file is rendered
- **THEN** all references to `Awen Hub` are replaced with `Cianfhoghlaim Oideachais`
- **AND** the MMORPG/x402/Anam token narrative is removed from the oideachais-themed docs
- **AND** the educational focus (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary; bilingual EN/GA) is preserved

## REMOVED Requirements

### Requirement: Awen Hub as the Interactive Frontend Brand

**Reason**: The MMO/Game theme from `tuatha/` is being shelved for the educational platform. The canonical project name is "Cianfhoghlaim Oideachais" across the rest of the monorepo, the published PyPI package, and `openspec/project.md`.

**Migration**:
- 4 source-file edits in `oideachais/web/apps/web/` (rebrand only)
- 1 file rename: `AwenChat.tsx` → `OideachasChat.tsx`
- 2 doc updates (`readme2.md`, `docs/ARCHITECTURE_DEPLOYMENT.md`)
- 2 demoted docs (`docs/web/frontend/agentic-platform.md`, `docs/tuatha/Agentic Education Platform Development.md`)
- The PyPI package name and the monorepo directory name are unchanged
