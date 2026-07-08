# Cianfhoghlaim Leaving Cert Portal Capability

## Purpose

`cianfhoghlaim-leaving-cert-portal` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/` (TanStack Start
front-end + Hono oRPC API + Convex `conic-leaving-cert` deployment) +
`cianfhoghlaim/{baml,cocoindex,dagster,dlt,leaving_certificate,notebooks}/<subject>/`
(per-subject end-to-end pipelines for the 8 NCCA Leaving Certificate
subjects + the 5 NCCA root-level programme PDFs).

This is the canonical openspec spec for the Leaving Cert portal. It
**supersedes** the deprecated `oideachais-web` app (which is retired
as a prototype) and integrates with the `cianfhoghlaim-educational-mmo`
spec for the 8 NCCA ADK specialists + the `retro-game-asset-pipeline`
spec for the Diagram Generator + 3D Asset Gallery + the
`ncca-leaving-cert-root-pdfs` spec for the 5 NCCA root-level programme
PDFs.

## Background

Cianfhoghlaim is building the bilingual (EN + GA) educational portal
for the Republic of Ireland's **NCCA Leaving Certificate** curriculum.
The portal renders 8 NCCA LC subjects with 6 sections per subject +
4 diagram modes + a 2D + 3D asset gallery + a CopilotKit v2 chat +
an accurate British Isles map split into 6 subnations.

The 6 subnations are: Éire (Ireland, v1 active) + Northern Ireland +
Scotland + England + Wales + Isle of Man.

The 8 NCCA LC subjects are:

- mathematics
- applied_mathematics
- chemistry
- geography
- history
- english
- gaeilge
- computer_science

The public theming is currently professional + minimal (no mythological
overlay). The 8 NCCA subject specialists are referenced as the 8 subject
agents. The land is the British Isles; the wound is the language loss;
the healing is education.

The mythology / historical-sources theming layer will be introduced
**long after the full BIEP v1 lands** (see the
`british-isles-education-pipeline` spec for the cross-nation foundation
and the `2026-07-09-remove-brown-ajah-theming-v1` change for the
removal of the Brown Ajah / Wheel of Time lens).

The lore document `docs/CIANFHLOGHLAIM_LORE.md` (the operator's personal
triple-crown lineage — Cian Mac an Déisigh Uí Liatháin + Deacy + Lyons +
Morris + Conroy) is operator-only and NEVER displayed on the public
surface.

## Requirements

### Requirement: 8 NCCA LC Subjects × EN+GA (R1)

The system SHALL provide per-subject landing pages for the 8 NCCA Leaving
Certificate subjects (mathematics, applied_mathematics, chemistry, geography,
history, english, gaeilge, computer_science) in both EN and GA, with the
Leaving Cert 2026 exam-window compat for 7 legacy subjects
(mathematics, irish, biology, french, history, business, construction-studies).

#### Scenario: Mathematics bilingual landing page

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics` or `/ga/leaving-cert/mata`
- **WHEN** the page loads
- **THEN** the syllabus section renders ≥1 topic per `qpack_mathematics.baml` topic
- **AND** the CopilotKit sidebar mounts in the same language
- **AND** the `TranslationToggle` swaps EN↔GA labels without page reload

### Requirement: 6-section per-subject shell (R2)

The system SHALL render each per-subject landing page with exactly 6 sections,
in this order: (1) Syllabus analysis, (2) Past exam question table, (3) Marking
scheme patterns, (4) Topic prioritisation (marks ÷ study-hours), (5) Exam layout
tips, (6) PDF library (original NCCA syllabus + SEC exam papers + marking
schemes, all served as signed R2 URLs).

#### Scenario: Mathematics 6-section shell renders

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics`
- **WHEN** the page loads
- **THEN** the 6 sections render in order: SyllabusAnalysis / PastExamTable / MarkingSchemePatterns / TopicPrioritisation / ExamLayoutTips / PdfLibrary
- **AND** each section has the bilingual EN+GA heading
- **AND** the PDF library shows signed R2 URLs

### Requirement: Syllabus + Exam Diagram Generator (R3)

The system SHALL render 4 diagram modes for each per-subject page:

1. **Concept-map** — syllabus concept-map (uses `b.ExtractSyllabusStructure`)
2. **Topic-frequency heatmap** — question × paper × topic × year (D3 v8 + Vega-Lite)
3. **PCLM marking flow** — Partial Credit, Logical Marking flowchart (React Flow + dagre)
4. **Question-paper-topic Sankey** — question → topic → difficulty → year Sankey

#### Scenario: Concept-map diagram renders from the 5 NCCA Key Competencies

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics?window=diagram-concept-map`
- **WHEN** the diagram loads
- **THEN** the diagram renders 5 root nodes (one per NCCA Key Competency) + child nodes for each Mathematics LO + bilingual EN + GA labels

### Requirement: 2D + 3D Asset Gallery — Hades dual-mode (R4)

The system SHALL render both 3D meshes and 2D sprite atlases for each subject.

#### Scenario: Mathematics asset gallery shows 3D + 2D

- **GIVEN** the user navigates to `/en/assets/mathematics`
- **WHEN** the page loads
- **THEN** the Gallery shows ≥1 GLB rendered in Babylon.js + ≥1 sprite atlas rendered as a CSS sprite

### Requirement: CopilotKit v2 Factory Mode + AG-UI (R5)

The system SHALL mount a `<CopilotSidebar defaultOpen>` from
`@copilotkit/react-core/v2` at the root layout. The 8 NCCA subject ADK
specialists SHALL be registered as CopilotKit dispatch targets.

#### Scenario: Mathematics student asks "what topics should I revise first?"

- **GIVEN** the user opens the CopilotKit sidebar on `/en/leaving-cert/mathematics`
- **WHEN** the user types "what topics should I revise first?"
- **THEN** the orchestrator dispatches to `math_agent`
- **AND** the `useRenderTool` hook renders the prioritisation as an inline component

### Requirement: BetterAuth + Pocket ID OIDC + optional SIWE (R6)

The system SHALL use BetterAuth + Pocket ID OIDC + optional SIWE on the
fresh standalone `conic-leaving-cert` Convex deployment with 5
carried-over + 3 new tables.

### Requirement: Accurate British Isles map + 6 subnations (R7)

The system SHALL render an accurate OpenStreetMap-based map of the
British Isles split into 6 subnations (Éire + Northern Ireland +
Scotland + England + Wales + Isle of Man) with 5 NCCA Key Competencies
as 5 land-marks + 8 NCCA subjects as 8 overlay buttons.

### Requirement: (R8 REMOVED 2026-07-09 — Brown Ajah theming)

The Brown Ajah Wheel of Time theming (Aes Sedai / Amyrlin Seat /
Dragon Reborn / Tuatha'an + the "Aes Sedai — servants of all" tagline)
was removed per the `2026-07-09-remove-brown-ajah-theming-v1` change.
The mythology / historical-sources theming is deferred to BIEP-v2
(see the `british-isles-education-pipeline` spec). The lore document
`docs/CIANFHLOGHLAIM_LORE.md` is operator-only.

### Requirement: Celtic UI Design System (R9)

The system SHALL implement the design tokens + 12 reusable `<Ci*>` components
documented in `docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css`.

### Requirement: Cianfhoghlaim OS PostHog-style window manager (R10)

The system SHALL implement a `<CianfhoghlaimOS>` provider with
`{windows, activeId, dispatch}` state machine + Framer Motion physics.

## See also

- [cianfhoghlaim-educational-mmo](../cianfhoghlaim-educational-mmo/spec.md) — the 8 NCCA ADK specialists
- [retro-game-asset-pipeline](../retro-game-asset-pipeline/spec.md) — the 2D + 3D asset generator
- [ncca-leaving-cert-root-pdfs](../ncca-leaving-cert-root-pdfs/spec.md) — the 5 NCCA root-level PDFs
- [agentic-frontend-frameworks](../agentic-frontend-frameworks/spec.md) — the 5th canonical surface (R5 + R6 + R7)