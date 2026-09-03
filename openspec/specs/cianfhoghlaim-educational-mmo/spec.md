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
`cocoindex/<subject>_embedding.py`, `agents/tuatha/<subject>_agent.py`,
`web/apps/cianfhoghlaim-mmo/src/routes/realm/<subject>.tsx`, and
`notebooks/leaving_cert/<subject>.py`. Every generation function in each
subject's `qpack_<subject>.baml` (`Generate<Subject>FormativeItem`,
`Generate<Subject>QuestPack`) SHALL take the current v3 extraction types
(`SyllabusDocument`, `ExamPaper`, `MarkingScheme` — as produced by the
`lc_extraction` BAML functions) as input and SHALL NOT reference the
superseded `_legacy/pdfs/leaving_cert_syllabus.baml` types. No generation
function SHALL contain a placeholder prompt body.

#### Scenario: Mathematics pipeline runs end-to-end

- **GIVEN** the Mathematics PDFs in
  `cianfhoghlaim/leaving_certificate/mathematics/{en,ga}/`
- **WHEN** the user materialises the `mathematics_quest_pack` Dagster
  asset (`orchestration/defs/2_materials/lc_extraction/
  quest_pack_assets.py`)
- **THEN** the asset extracts the real syllabus + past papers +
  marking schemes via the v3 extraction functions
- **AND** the asset calls `GenerateMathQuestPack` and writes the
  resulting `MathQuestPack` to the Convex `questPacks` table
- **AND** the pack's `items` reference real `evidence.source_page`
  values from the extracted syllabus, not fabricated content

Per-subject LanceDB embedding assets and marimo notebooks are real,
separate future work — not claimed as built by this scenario.

#### Scenario: Generated formative item cites real extraction, not a placeholder

- **GIVEN** a `MathEvidenceLink` built from a real
  `SyllabusDocument` (extracted by `ExtractCurriculumSyllabus` from a
  real ingested LC PDF), carrying its `source_page` and verbatim
  `excerpt_en`
- **WHEN** `GenerateMathFormativeItem(lo_code, difficulty, level,
  topic, evidence=<that MathEvidenceLink>)` runs
- **THEN** the returned `MathFormativeItem.evidence` matches the input
  evidence's `source_pdf`/`source_page`
- **AND** the BAML function body is not the literal string
  `"Auto-generated extraction prompt."`

#### Scenario: All 8 subjects have full pipelines

- **GIVEN** the per-subject PDF corpora are present
  (`cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/`)
- **WHEN** the user runs `mise run dagster:oideachais`
- **THEN** all 8 subject asset groups are visible in the Dagster UI
- **AND** all 8 marimo notebooks render without error

### Requirement: Per-subject quest pack generation

The system SHALL generate formative quest packs keyed to NCCA learning
outcomes + past paper questions + marking schemes, for both the Leaving
Certificate and Junior Cycle programmes. Each quest pack SHALL be
bilingual EN + GA (except a subject whose corpus is genuinely
single-medium, e.g. gaeilge's Irish-medium exam papers), and SHALL
support the NCCA levels a subject's corpus provides evidence for. A
quest pack SHALL contain a bounded number of `FormativeItem`s (up to
15, prioritising breadth of module/topic coverage over exhaustive
learning-outcome coverage — an unbounded "one item per LO" requirement
was found, via a live end-to-end run, to make generation calls
time out for syllabi with dozens of learning outcomes), each with
difficulty range 1-5, and SHALL reference the source NCCA PDF page in
its `evidence.source_page` field. Quest-pack generation functions
SHALL consume real extraction output (`SyllabusDocument`, `ExamPaper`,
`MarkingScheme`) — content SHALL NOT be generated from a learning-outcome
code string alone.

#### Scenario: Quest pack generated for Mathematics

- **GIVEN** a Mathematics `SyllabusDocument` with multiple
  `module_topics`, each with its own learning outcomes
- **WHEN** `GenerateMathQuestPack(syllabus, past_papers,
  marking_schemes, level="LC_HL")` runs
- **THEN** the output `MathQuestPack.items` contains up to 15
  `MathFormativeItem`s, each with `prompt`, `expected_answer`,
  `marking_scheme` (bilingual `text_en`/`text_ga`), `evidence.source_page`
  ≥1, and `difficulty` in 1-5
- **AND** `los_covered` lists exactly the LO codes of the generated
  items, not every LO in the syllabus
- **AND** the output content reflects the actual syllabus text passed
  in, not a generic template

#### Scenario: Gaeilge quest pack is Irish-only

- **GIVEN** a Gaeilge learning outcome `LC-GAEL-LO-3.1` and its
  `GaelEvidenceLink` (source PDF page + verbatim Irish excerpt)
- **WHEN** `GenerateGaelFormativeItem(lo_code="LC-GAEL-LO-3.1",
  difficulty=2, level="LC_HL", topic="...", evidence=...)` runs
- **THEN** the output `prompt.text_en` is null (Gaeilge is taught in
  Irish only) and `prompt.text_ga` is the canonical Irish phrasing
- **AND** the output `marking_scheme.text_en` is null and
  `marking_scheme.text_ga` is the canonical Irish marking scheme

#### Scenario: Junior Cycle quest pack issues a JCPA-framework badge

- **GIVEN** a Junior Cycle learning outcome for a subject with Junior
  Cycle coverage
- **WHEN** a student completes the generated formative item at ≥80%
- **THEN** a `SkillTreeBadge` is issued with `framework="ncca-jc"`
- **AND** the badge's `competency_code` matches the Junior Cycle LO code

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
bilingual EN + GA throughout. Subject realm pages SHALL render quest
content fetched from a real Convex query against generated content —
no hardcoded item counts or non-functional buttons. **No Babylon.js, no
SpacetimeDB.**

#### Scenario: Subject realm page renders real quest content

- **GIVEN** the user navigates to `/realm/mathematics`
- **WHEN** the page loads
- **THEN** the page displays the Mathematics realm header (bilingual)
- **AND** the page lists ≥1 quest pack fetched via a Convex query
  against the `questPacks` table, not a hardcoded count
- **AND** the "Start" button has a working `onClick` handler that
  begins a quest attempt

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
and SHALL NOT be loaded. The `dlt/british_isles/ireland/` subdirectory
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
  `cianfhoghlaim.lc.mathematics.embeddings` LanceDB table
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

### Requirement: Cian Mac an Déisigh Uí Liatháin personal lore (R10 — REPHASED 2026-07-09 to remove the Brown Ajah / Wheel of Time lens)

The system SHALL document the operator's personal lore in
`docs/CIANFHLOGHLAIM_LORE.md` (operator-only document).

The lore SHALL identify the hero as **Cian Mac an Déisigh Uí Liatháin**
of the triple-crown lineage (Deacy Uí Dhéisigh + Lyons Mac Liatháin +
Morris City of Tribes + Conroy Mac Conraoi), grounded in the 8
lineage clippings at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
(the 8 Wikipedia clippings: Tuatha Dé Danann, Cian, Aos Sí, Uí Liatháin,
Déisi, Delbhna Tír Dhá Locha, Leath Cuinn and Leath Moga, Éamonn
Deacy Park).

The lore document is operator-only — NEVER linked from the public
surface. The public app's theming is professional + minimal until the
mythology / historical-sources layer is introduced post-BIEP-v2 (per
the `2026-07-09-remove-brown-ajah-theming-v1` change).

#### Scenario: Lore document is operator-only

- **GIVEN** the operator opens `docs/CIANFHLOGHLAIM_LORE.md`
- **WHEN** the document is read
- **THEN** it identifies Cian Mac an Déisigh Uí Liatháin by name + lineage + the 3 Gemini Deep Research warrants
- **AND** it references all 8 lineage clippings by filename

#### Scenario: Public surface never displays personal lineage

- **GIVEN** the user opens any page on `cianfhoghlaim.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`
- **AND** no text matches the family surnames Deacy, Lyons, Morris, Conroy
- **AND** no text references the 3 Gemini Deep Research warrants
- **AND** no text matches "Aes Sedai", "Amyrlin Seat", "Dragon Reborn", "Dragon Banner", "Tuatha'an" (the WoT lens is removed)

#### Scenario: Footer shows the canonical Cianfhoghlaim credit (no WoT tagline)

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the Header does NOT show "Aes Sedai — servants of all" (the Brown Ajah motto is removed per `2026-07-09-remove-brown-ajah-theming-v1`)
- **AND** the Footer shows a small italicized "Cianfhoghlaim — Coláiste na Déisigh" footer credit
- **AND** the lore document is NEVER linked from the Header or Footer

### Requirement: Digital Learning Profile

The system SHALL provide a "Digital Learning Profile" route
(`/student/<id>/profile`) presenting a student's earned badges grouped
by the NCCA's 7 senior-cycle key competencies (thinking and solving
problems, being creative, communicating, working with others,
participating in society, cultivating wellbeing, managing learning and
self), per the presentation pattern described in the NCCA's own
commissioned research into digital credentials and micro-credentials
(`leaving_certificate/the-potential-of-technology-to-support-online-
certification-and-reporting.pdf`) — distinct from the plain
chronological badge wallet.

#### Scenario: Profile groups badges by key competency

- **GIVEN** a student has earned badges tagged with
  `THINKING_AND_SOLVING_PROBLEMS` and `COMMUNICATING`
- **WHEN** the user navigates to `/student/<id>/profile`
- **THEN** the page renders a section per key competency present in
  the student's badges, each containing only the badges tagged with
  that competency
- **AND** badges issued before key-competency tagging existed (empty
  `key_competencies`) render in a separate "not yet mapped" section
  rather than being silently dropped

### Requirement: Junior Cycle subject coverage

The system SHALL provide docs-informed quest-pack generation for the
NCCA Junior Cycle programme, for the subset of the 8 Leaving Cert
subjects that also have Junior Cycle equivalents plus any Junior-Cycle-
only subjects, using the same real-extraction-input pattern as the
Leaving Cert requirement above. Junior Cycle content SHALL be wired to
the existing Junior Cycle DLT ingestion sources
(`dlt_sources/british_isles/ireland/education/junior_cycle*.py`).

#### Scenario: Junior Cycle Mathematics content is generated from real extraction

- **GIVEN** a Junior Cycle Mathematics syllabus PDF has been ingested
  and extracted into a `SyllabusDocument` record
- **WHEN** the Junior Cycle generation function runs against that record
- **THEN** the output `FormativeItem` references the extracted
  `source_page`
- **AND** the badge issued on completion has `framework="ncca-jc"`

### Requirement: England GCSE + A-Level subject coverage

The system SHALL provide docs-informed quest-pack generation for
England's GCSE and A-Level qualifications, mirroring the Leaving Cert
pattern, consuming England's existing real extraction output
(`baml_src/british_isles/england/education/{curriculum_syllabus,
exam_paper_layout,marking_scheme}.baml`). England content is English-
only (no bilingual EN + GA requirement).

#### Scenario: England GCSE quest pack generated from real extraction

- **GIVEN** an England GCSE subject's `SyllabusDocument` and `ExamPaper`
  records extracted from real ingested board PDFs (AQA, OCR, or Edexcel)
- **WHEN** the corresponding `Generate<Subject>QuestPack` function runs
- **THEN** the output quest pack's items reference the extracted
  `source_page` evidence
- **AND** the output is scoped to the correct exam board

### Requirement: Badge key-competency and evidence-type grounding

Every `SkillTreeBadge` SHALL carry a `key_competencies` field (one or
more of the NCCA's 7 senior-cycle key competencies: thinking and
solving problems, being creative, communicating, working with others,
participating in society, cultivating wellbeing, managing learning and
self) and an `evidence_type` field distinguishing formative-item
evidence from Classroom-Based-Assessment-style evidence, per the
terminology in the NCCA's own commissioned research
(`leaving_certificate/the-potential-of-technology-to-support-online-
certification-and-reporting.pdf`).

#### Scenario: Badge issued with key-competency tagging

- **GIVEN** a student completes a Mathematics formative item requiring
  problem-solving
- **WHEN** `issue_badge()` is called
- **THEN** the resulting `SkillTreeBadge`'s `key_competencies` includes
  `KeyCompetency.THINKING_AND_SOLVING_PROBLEMS`
- **AND** the badge's `evidence_type` is set correctly for the
  evidence kind that triggered issuance

## Cross-references

- `openspec/changes/ncca-leaving-cert-syllabi-corpus/` — the
  per-subject PDF download + BAML `ExtractSyllabusStructure` that
  this change builds on
- `openspec/specs/tuatha-platform/spec.md` — deprecated alias,
  removed in 1 release
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — the underlying
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
## Migrated from (2026-07-06)

- `tuatha-platform` — the deprecated `tuatha-platform` spec (24 Requirements covering the Celtic educational MMO + crypteolas crypto + SpacetimeDB) was formally superseded by this canonical spec
