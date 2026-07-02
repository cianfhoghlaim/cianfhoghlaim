# Cianfhoghlaim Educational MMO Capability

## Purpose

`cianfhoghlaim-educational-mmo` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` (TanStack Start 2D game
client) + `cianfhoghlaim/agents/meaisinfhoghlaim/educational/`
(8 NCCA specialist agents) + `cianfhoghlaim/badges/`
(hybrid x402 educational credential) +
`cianfhoghlaim/{baml,dlt,dagster,cocoindex,notebooks}/<subject>/`
(per-subject end-to-end pipelines for the 8 NCCA Leaving Certificate
subjects).

This is the canonical openspec spec for the educational MMO. It
**supersedes** the deprecated `tuatha-platform` spec (the latter is
preserved as a deprecated alias for 1 release, then archived).

## Background

Cianfhoghlaim is building a formative-assessment-driven educational
MMO for the Republic of Ireland's **NCCA Junior Cycle + Leaving
Certificate** curriculum. The 8 LC subjects are:

- mathematics
- applied_mathematics
- chemistry
- geography
- history
- english
- gaeilge (taught in Irish; some content also in English)
- computer_science

The MMO is built on the existing Cianfhoghlaim pipeline stack:
DLT (per-subject sources) + Dagster (per-subject asset groups) +
CocoIndex v1 (per-subject embedding) + BAML (per-subject extraction +
quest-pack generation) + FalkorDB + LanceDB + Cognee + Graphiti
(memory layer) + Letta (agent memory) + LiteLLM (unified LLM gateway) +
CopilotKit AG-UI (streaming chat) + Hono + Convex + TanStack Start
(2D game client) + BetterAuth + SIWE (auth).

The historic skills `.agents/skills_backup/tuatha-mmo/` and
`.agents/skills_backup/tuatha-platform/` are preserved as
**archaeology** — they document an earlier Babylon.js 3D + SpacetimeDB
v2 + Pent-Elemental Cosmology + Crypteolas financial token design
that did not land. The new build drops those themes but keeps the
technological choices.

The hybrid x402 educational credential is verifiable by third parties
(employers, universities) via a daily Merkle root anchored on Base L2.
**It is educational, not financial** — students do not buy anything
with real money, and the educational credit tokens are issued by the
platform itself as quest-completion rewards.

## Requirements

### Requirement: 8 NCCA Subjects

The system SHALL provide end-to-end per-subject pipelines for the 8
NCCA Leaving Certificate subjects: mathematics, applied_mathematics,
chemistry, geography, history, english, gaeilge, computer_science.
Each subject SHALL have a `qpack_<subject>.baml` file,
`dlt/subjects/<subject>/` source, `dagster/assets/<subject>_assets.py`,
`cocoindex/<subject>_embedding.py`, `agents/meaisinfhoghlaim/educational/<subject>_agent.py`,
`web/apps/cianfhoghlaim-mmo/src/routes/realm/<subject>.tsx`, and
`notebooks/leaving_cert/<subject>.py`.

#### Scenario: Mathematics pipeline runs end-to-end

- **GIVEN** the 7 Mathematics PDFs in
  `cianfhoghlaim/leaving_certificate/mathematics/{en,ga}/`
- **WHEN** the user materialises the 6 Mathematics Dagster assets
- **THEN** the `math_syllabus_raw` asset produces ≥1 `MathSyllabusTopic` per topic
- **AND** the `math_quest_pack` asset produces ≥1 `FormativeItem` per learning outcome
- **AND** the `math_embedding` asset populates the LanceDB table
  `oideachais.lc.mathematics.embeddings` with ≥1 BGE-M3 1024-dim
  vector per quest item
- **AND** the marimo notebook at
  `cianfhoghlaim/notebooks/leaving_cert/mathematics.py` renders
  the 8-subject NCCA syllabus landscape with bilingual EN + GA content

#### Scenario: Applied Mathematics partial pipeline runs

- **GIVEN** the 4 Applied Mathematics PDFs in
  `cianfhoghlaim/leaving_certificate/applied_mathematics/{en,ga}/`
  (`LC020ALP000EV.pdf`, `LC020ALP000IV.pdf`, `LC020GLP000EV.pdf`, `LC020GLP000IV.pdf`)
- **WHEN** the user materialises the 6 Applied Mathematics Dagster assets
- **THEN** the `appm_syllabus_raw` asset produces ≥1 `AppmSyllabusTopic` per topic
- **AND** the `appm_quest_pack` asset produces ≥1 `FormativeItem` per learning outcome

#### Scenario: All 8 subjects have full pipelines

- **GIVEN** the per-subject PDF corpora are present
  (`cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/`)
- **WHEN** the user runs `mise run dagster:oideachais`
- **THEN** all 8 subject asset groups are visible in the Dagster UI
- **AND** all 8 marimo notebooks render without error

### Requirement: Per-subject quest pack generation

The system SHALL generate formative quest packs keyed to NCCA learning
outcomes + past paper questions + marking schemes. Each quest pack
SHALL be bilingual EN + GA, and SHALL support the 3 NCCA levels
(Higher / Ordinary / Foundation where applicable). The quest pack
SHALL contain ≥1 `FormativeItem` per NCCA learning outcome, with
difficulty range 1-5, and SHALL reference the source NCCA PDF page
in its `evidence.source_page` field.

#### Scenario: Quest pack generated for a Mathematics LO

- **GIVEN** a Mathematics learning outcome `LC-MATHS-LO-2.4`
- **WHEN** the BAML function `GenerateMathFormativeItem("LC-MATHS-LO-2.4", difficulty=3)` runs
- **THEN** the output is a `MathFormativeItem` with `text_en`, `text_ga`,
  `marking_scheme_en`, `marking_scheme_ga`, `evidence.source_page` ≥1,
  and `difficulty == 3`

#### Scenario: Gaeilge quest pack is Irish-only

- **GIVEN** a Gaeilge learning outcome `LC-GAEL-LO-3.1`
- **WHEN** the BAML function `GenerateGaelFormativeItem("LC-GAEL-LO-3.1", difficulty=2)` runs
- **THEN** the output's `text_en` is null (Gaeilge is taught in Irish only)
- **AND** the output's `text_ga` is the canonical Irish phrasing
- **AND** the output's `marking_scheme_en` is null
- **AND** the output's `marking_scheme_ga` is the canonical Irish marking scheme

### Requirement: 8 ADK specialist agents + 1 root orchestrator

The system SHALL provide 8 ADK `LlmAgent`s (one per NCCA subject) plus
the existing `root_agent` updated to route keyword-level traffic to
them. Each subject agent SHALL be backed by the LiteLLM gateway
(`litellm.cianfhoghlaim.ie:4000`) and expose ≥5 tools (syllabus lookup,
past paper lookup, marking scheme lookup, formative item generation,
response scoring). Each subject agent SHALL use BAML for all extraction
+ generation, and SHALL persist player mastery state via Letta
(`letta.cianfhoghlaim.ie:8283`).

#### Scenario: Root agent routes to math_agent

- **GIVEN** the `root_agent` is configured with the 8-bucket
  `ROUTING_KEYWORDS` map (math / appm / chem / geog / hist / engl /
  gael / comp)
- **WHEN** a user query contains the keyword "differentiation"
- **THEN** the `root_agent` routes the query to `math_agent`
- **AND** the `math_agent` returns a response that references
  Mathematics syllabus content via its `math_syllabus_lookup` tool

#### Scenario: Each subject agent has ≥5 tools

- **GIVEN** any of the 8 subject agents is registered in
  `cianfhoghlaim/agents/meaisinfhoghlaim/educational/`
- **WHEN** the agent is instantiated
- **THEN** the agent has ≥5 tools registered
- **AND** at least 1 tool is a BAML client, 1 tool is a LanceDB query,
  and 1 tool is a Letta memory read/write

### Requirement: Hybrid x402 educational credential

The system SHALL issue educational credentials as off-chain
`SkillTreeBadge`s (Convex + FalkorDB + LanceDB) plus a daily Merkle
root anchored on Base L2 via the `CredAnchor` smart contract. Each
badge SHALL be ETH-signed by the issuing agent's wallet and SHALL
include the NCCA learning outcome code, the agent issuer, the date
earned, the evidence hash, and the bilingual competency text (EN +
GA where applicable). The on-chain anchor SHALL be queryable via a
public verification page that recomputes the Merkle path.

#### Scenario: Badge is issued after quest completion

- **GIVEN** a student has completed a Mathematics quest at HL level
  covering `LC-MATHS-LO-2.4`
- **WHEN** the `math_agent` validates the student's final response
- **THEN** a `SkillTreeBadge` row is created in Convex with
  `framework="ncca-lc"`, `level="hl"`, `subject="mathematics"`,
  `competency_code="LC-MATHS-LO-2.4"`, `agent_issuer="math_agent"`,
  and an ETH signature from the agent's wallet
- **AND** a corresponding FalkorDB `SkillTreeBadge` node is created
  with edges to the player's profile node and to the LO node

#### Scenario: Daily Merkle anchor published on Base L2

- **GIVEN** the `daily_credential_anchor` Dagster asset runs at 02:00 UTC
- **WHEN** there are ≥1 new badges since the last anchor
- **THEN** the asset computes the Merkle root of the new badges
- **AND** the asset calls `CredAnchor.publish(root, batchId)` on Base L2
- **AND** the asset writes the resulting `tx_hash` back into each
  badge row in Convex

#### Scenario: Third party verifies a badge

- **GIVEN** a badge with `id = "uuid"`, `evidence_hash = "0x..."`,
  `on_chain_anchor = "0x..."` (Base L2 tx_hash), and `anchor_date = "2026-07-01"`
- **WHEN** a third party calls `GET /anchor/2026-07-01`
- **THEN** the page displays the Merkle root published on Base L2
- **AND** the page accepts the badge's `id + evidence_hash` and
  verifies the Merkle path against the on-chain root
- **AND** the verification result is a clear pass/fail indicator

### Requirement: 2D TanStack Start game client

The system SHALL provide a TanStack Start 2D game client at
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` on port 3080 with routes
for the 8 subject realms, the student badge wallet, the cross-subject
mastery dashboard, the teacher view, and the public Merkle anchor
verification page. The client SHALL use BetterAuth (email/password +
SIWE wallet) for authentication, Convex for real-time state, and
CopilotKit AG-UI for streaming agent chat. The client SHALL be
bilingual EN + GA throughout. **No Babylon.js, no SpacetimeDB.**

#### Scenario: Subject realm page renders

- **GIVEN** the user navigates to `/realm/mathematics`
- **WHEN** the page loads
- **THEN** the page displays the Mathematics realm header (bilingual)
- **AND** the page lists ≥1 quest pack from the `math_quest_pack` asset
- **AND** the CopilotKit chat panel is open with `math_agent` as the active agent

#### Scenario: Student badge wallet renders

- **GIVEN** a student has ≥1 `SkillTreeBadge` in Convex
- **WHEN** the user navigates to `/student/<id>/badges`
- **THEN** the page displays ≥1 badge card with the badge id, framework,
  level, subject, competency code, date earned, and on-chain anchor
- **AND** the page links to the public verification page for each badge

#### Scenario: Cross-subject mastery dashboard renders

- **GIVEN** a student has badges in ≥2 subjects
- **WHEN** the user navigates to `/student/<id>/mastery`
- **THEN** the page displays a FalkorDB-backed visualisation of the
  student's mastery across the 8 NCCA subjects

#### Scenario: Public anchor verification page renders

- **GIVEN** a date `2026-07-01` has a published Merkle anchor
- **WHEN** the user navigates to `/anchor/2026-07-01`
- **THEN** the page displays the Merkle root and the Base L2 tx_hash
- **AND** the page accepts a badge `id + evidence_hash` and verifies
  the Merkle path against the on-chain root

### Requirement: NCCA-only narrowing

The system SHALL operate on the NCCA (Ireland) curriculum framework
only. The `cianfhoghlaim/dlt/british_isles/{sct,wls,ni,jey,iom,ggy}/`
DLT subdirectories SHALL be archived to `.archive/dlt/british_isles_other/`
and SHALL NOT be loaded. The `dlt/british_isles/ie/` subdirectory
SHALL remain active and SHALL be the canonical source for NCCA
curriculum content.

#### Scenario: Non-IE DLT subdirs are not loaded

- **GIVEN** the archived `sct/wls/ni/jey/iom/ggy` directories are moved
  to `.archive/dlt/british_isles_other/`
- **WHEN** Dagster starts up
- **THEN** no assets from those directories are loaded
- **AND** the only `british_isles` asset group visible is `ie`

### Requirement: Per-subject marimo notebook

The system SHALL provide 8 marimo notebooks (one per NCCA subject)
at `cianfhoghlaim/notebooks/leaving_cert/<subject>.py`. Each notebook
SHALL render the per-subject syllabus landscape with bilingual EN + GA
content, BGE-M3 semantic search over the per-subject quest packs, and
a teacher view with quest designer controls.

#### Scenario: Mathematics notebook renders

- **GIVEN** the user runs `marimo edit cianfhoghlaim/notebooks/leaving_cert/mathematics.py`
- **WHEN** the notebook loads
- **THEN** the notebook displays all Mathematics NCCA learning outcomes
  in a searchable table (bilingual EN + GA)
- **AND** the notebook has a semantic search box that queries the
  `oideachais.lc.mathematics.embeddings` LanceDB table
- **AND** the notebook has a "design quest" panel that lets a teacher
  generate a custom `MathFormativeItem` via the BAML client

### Requirement: Bilingual EN + GA throughout

Every BAML output field that holds user-facing text SHALL have a
`text_en` and a `text_ga` field. Gaeilge-only fields (e.g., Irish
syllabus content) SHALL have `text_en = null` and `text_ga` as the
canonical value. Every UI string in the TanStack Start game client
SHALL be bilingual. Every quest content string SHALL be bilingual.

#### Scenario: Bilingual quest content

- **GIVEN** a quest for Mathematics LO `LC-MATHS-LO-2.4`
- **WHEN** the quest is rendered in the game client
- **THEN** the English and Irish versions are both visible
- **AND** the user can toggle between EN and GA
- **AND** the marking scheme references in the quest are also bilingual

#### Scenario: Gaeilge quest is Irish-only

- **GIVEN** a quest for Gaeilge LO `LC-GAEL-LO-3.1`
- **WHEN** the quest is rendered in the game client
- **THEN** only the Irish version is shown
- **AND** the toggle to switch to EN is disabled (Gaeilge is taught in Irish only)

### Requirement: Cian of the Tuatha Dé Danann Lore (R10 — NEW per `rewrite-cianfhoghlaim-leaving-cert-v2`)

The system SHALL document the platform's lore in
`docs/CIANFHLOGHLAIM_LORE.md`. The lore SHALL identify the hero as
**Cian Mac an Déisigh Uí Liatháin** of the triple-crown lineage
(Deacy Uí Dhéisigh + Lyons Mac Liatháin + Morris City of Tribes +
Conroy Mac Conraoi), grounded in the 7 lineage clippings at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
(Tuatha Dé Danann + Cian + Aos Sí + Uí Liatháin + Déisi + Delbhna
Tír Dhá Locha + Leath Cuinn and Leath Moga) and the 4 Wheel of Time
excerpts (Aes Sedai + Amyrlin Seat + Dragon Reborn + Dragon Banner +
Tuatha'an). The lore document is operator-only — NEVER linked from
the public surface. The public app's theming is the Brown Ajah only.

#### Scenario: Lore document is operator-only

- **GIVEN** the operator opens `docs/CIANFHLOGHLAIM_LORE.md`
- **WHEN** the document is read
- **THEN** it identifies Cian Mac an Déisigh Uí Liatháin by name + lineage + the 3 Gemini Deep Research warrants
- **AND** it references all 7 lineage clippings by filename
- **AND** it references all 4 Wheel of Time excerpts by section title

#### Scenario: Public surface never displays personal lineage

- **GIVEN** the user opens any page on `oideachais.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`
- **AND** no text matches the family surnames Deacy, Lyons, Morris, Conroy
- **AND** no text references the 3 Gemini Deep Research warrants

#### Scenario: Header shows Brown Ajah tagline + ciphered reference

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the tagline reads "Aes Sedai — servants of all" (the Brown Ajah motto)
- **AND** the Footer shows a small italicized "Cianfhoghlaim — Coláiste na Déisigh" footer credit
- **AND** the lore document is NEVER linked from the Header or Footer

## Cross-references

- `openspec/changes/ncca-leaving-cert-syllabi-corpus/` — the
  per-subject PDF download + BAML `ExtractSyllabusStructure` that
  this change builds on
- `openspec/specs/tuatha-platform/spec.md` — deprecated alias,
  removed in 1 release
- `openspec/specs/oideachais-pipeline/spec.md` — the underlying
  pipeline capability
- `openspec/specs/agentic-frontend-frameworks/spec.md` — the
  TanStack Start + CopilotKit + Hono + Convex pattern
- `.agents/skills/cianfhoghlaim-mmo/SKILL.md` — the canonical skill
  (replaces `.agents/skills/tuatha-mmo/`)
- `.agents/skills/cianfhoghlaim-platform/SKILL.md` — the canonical
  skill (replaces `.agents/skills/tuatha-platform/`)
- `.agents/skills/cianfhoghlaim-achievement-ledger/SKILL.md` — the
  canonical skill (replaces `.agents/skills/tuatha-achievement-ledger/`)
- `.agents/skills/cianfhoghlaim-mcp-server-tools/SKILL.md` — the
  canonical skill (replaces `.agents/skills/tuatha-mcp-server-tools/`)
- `.agents/skills/ncca-formative-assessment/SKILL.md` — the canonical
  formative assessment skill (replaces `.agents/skills/british-isles-formative-assessment/`)
- `.agents/skills/agent-fleet-orchestration/SKILL.md` — the 12-agent
  fleet pattern (this change extends it with 8 subject agents)
- `.agents/skills/agent-observability/SKILL.md` — Langfuse + MLflow +
  RAGAS + Logfire observability
- `.agents/skills/agent-memory-systems/SKILL.md` — Letta + Graphiti +
  Cognee + LanceDB + FalkorDB memory layer
- `.agents/skills/data-engineering-pipeline-documentation/SKILL.md` —
  the per-pipeline STATUS.md / REFACTORING.md convention
- `.agents/skills/infrastructure-stacks/SKILL.md` — the 70+ Docker
  Compose stacks + Pangolin + Infisical + Locket secret pattern
- `.agents/skills/secrets-management/SKILL.md` — Infisical + Locket +
  mise 3-way secrets contract