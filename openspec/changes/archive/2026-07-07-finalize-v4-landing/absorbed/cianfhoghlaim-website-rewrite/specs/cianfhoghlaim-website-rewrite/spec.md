# Delta: cianfhoghlaim-website-rewrite

## ADDED Requirements

### Requirement: 6 content types (Subjects / Practice / Past Papers / Marking Schemes / Foundations / Notebooks) (R1)

The system SHALL expose 6 content types as BAML functions, each
mapping to a per-subject source in the existing dlt/ + cocoindex/ +
baml_src/ + meaisínfhoghlaim/ pipeline. The 6 content types are:

1. **Subjects** — the 8 NCCA Leaving Certificate subjects (Mathematics,
   Applied Mathematics, Chemistry, Geography, History, English, Gaeilge,
   Computer Science). Each subject has a full landing page + the 5×8
   mastery matrix + the 5-tab layout.
2. **Practice** — formative item generation + scoring via the
   `baml.qpack_{subject}.baml` schema. Uses the
   `ScoreFormativeResponse` function.
3. **Past Papers** — the LC past exam papers (2017-2025), served from CF
   R2 via the dlt `ncca_root_pdfs.py` extraction.
4. **Marking Schemes** — the LC marking schemes for the past papers,
   extracted via the `baml.subject_rubric.baml` schema.
5. **Foundations** — the 5 NCCA root-level programme PDFs at
   `leaving_certificate/{key-competencies,sc-l1-l2-programme,scr-advisory,online-learning,online-certification}.pdf`.
6. **Notebooks** — the marimo notebooks at
   `notebooks/leaving_cert/{subject}.py`, embedded as interactive
   widgets.

#### Scenario: A student opens Mathematics and sees the 6 content types

- **GIVEN** a student navigates to `/en/subjects/mathematics`
- **WHEN** the page loads
- **THEN** the student sees the 5-tab layout (Syllabus / Papers /
  Marking / Practice / Notebook)
- **AND** the 5×8 mastery matrix is rendered from
  `cocoindex/cross_subject_competency_embedding.py`
- **AND** the syllabus tab shows the BAML ExtractLeavingCertSyllabus output
- **AND** the papers tab shows the dlt ncca_root_pdfs.py output
- **AND** the marking tab shows the baml.subject_rubric.baml output
- **AND** the practice tab shows the baml.qpack_mathematics.baml output
- **AND** the notebook tab embeds the marimo notebook from
  `notebooks/leaving_cert/mathematics.py`

### Requirement: 4 entry points (Khan-style hero) (R2)

The system SHALL expose 4 entry points on the landing page, matching the
Khan Academy + iximiuz Labs pattern:

1. **Student** — "I am a student, learning for myself"
2. **Teacher** — "I am a teacher, looking for NCCA-aligned content"
3. **Family** — "I am a family member, supporting my child"
4. **School** — "I am a school or district, looking for AI-powered solutions"

Each entry point routes to a personalised landing for that audience.

#### Scenario: A teacher opens the site

- **GIVEN** a teacher opens `/`
- **WHEN** the page loads
- **THEN** the teacher sees the 4 entry points
- **AND** clicking "I am a teacher" routes to `/en/teachers` (a teacher-specific landing with class management tools)
- **AND** the teacher can see the 8 NCCA subjects + the 5×8 mastery matrix + the practice tools
- **AND** the teacher can sign in via Pocket ID OIDC to track student progress

### Requirement: 9 ADK agents (8 NCCA + 1 cianfhoghlaim operator) (R3)

The system SHALL expose 9 ADK agents — 8 NCCA subject specialists
(Mathematics, Applied Mathematics, Chemistry, Geography, History,
English, Gaeilge, Computer Science) + 1 cianfhoghlaim operator agent
(the repo self-reference agent).

Each agent is wired to the corresponding `baml.qpack_{subject}.baml`
schema + the per-subject cocoindex embeddings + the per-subject dlt
extraction.

#### Scenario: A student asks the cianfhoghlaim operator about the platform

- **GIVEN** a student opens the global CopilotKit chat
- **WHEN** the student types "how does cianfhoghlaim work?"
- **THEN** the cianfhoghlaim operator agent answers with a description
  of the dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/ pipeline
- **AND** the operator provides file paths to the 8 BAML subject
  schemas + the 8 cocoindex subject embeddings + the dlt
  `ncca_root_pdfs.py` extraction
- **AND** the operator explains the 4 entry points (Student / Teacher /
  Family / School)

### Requirement: A2UI surface rendering from agent chat (R4)

The system SHALL render A2UI surfaces (per the `a2ui-renderer` skill
in `/Users/cianmacandeisigh/dev/kings_college_galway/.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md`)
from the agent chat responses. The `CopilotRuntime({ a2ui: {} })`
configuration enables A2UI; the `<CopilotKit a2ui={{ theme }}>` provider
enables the client-side renderer.

The 4 A2UI demo patterns from dojo.ag-ui.com are all supported:
- Tool-based generative UI
- A2UI fixed schema (form, chart, card)
- A2UI dynamic schema
- A2UI error recovery (invalid surfaces are regenerated)

#### Scenario: A student asks the Mathematics agent for a study plan

- **GIVEN** a student is on `/en/subjects/mathematics/practice`
- **WHEN** the student asks the Mathematics agent "give me a study plan"
- **THEN** the agent returns an A2UI surface (a card with the 5×8 mastery
  matrix + the highest-priority LOs + a study schedule)
- **AND** the surface renders as an interactive A2UI card
- **AND** the student can click into each priority LO to start a practice item

### Requirement: Cloudflare Workers + R2 + Convex + better-auth v1.4 (R5)

The system SHALL deploy to Cloudflare Workers (the API) + Cloudflare R2
(the PDFs) + Convex (real-time state) + better-auth v1.4 with Pocket ID
OIDC. The existing Hono dev server stays for local development; the
CF Worker is the production target.

The wrangler.toml bindings:
- `R2_BUCKET_5_NCCA_PDFS` — the 5 NCCA root-level PDFs
- `R2_BUCKET_8_SUBJECT_PDFS` — the 8 NCCA subject PDF folders
- `BETTER_AUTH_SECRET` — the better-auth v1.4 secret
- `POCKET_ID_OIDC_DISCOVERY` — the OIDC discovery URL
- `CONVEX_DEPLOYMENT` — the Convex production deployment
- `COPILOTKIT_RUNTIME_URL` — the agent runtime URL

#### Scenario: A teacher self-hosts cianfhoghlaim

- **GIVEN** a teacher runs `git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git`
- **WHEN** the teacher runs `bun install && bun run dev`
- **THEN** the dev server starts on `http://localhost:3082`
- **AND** the API starts on `http://localhost:8787`
- **AND** the teacher can sign in via Pocket ID OIDC
- **AND** the 5 NCCA PDFs + 8 subject folders are available via the dlt
  + cocoindex pipelines
- **AND** the 9 ADK agents are wired to the chat

### Requirement: 6 content types exposed as BAML functions (R6)

The system SHALL expose the 6 content types as BAML functions in
`baml_src/education/_shared/content_types.baml`. Each function takes a
content type + subject + level + language and returns the structured
content (past papers, marking schemes, syllabus, etc.).

The 6 functions:
1. `GetSubjectList(language: string) -> Subject[]` — the 8 NCCA subjects
2. `GetPastPapers(subject: string, year_from: int, year_to: int) -> PastPaper[]` — the LC past papers
3. `GetMarkingSchemes(subject: string, year_from: int, year_to: int) -> MarkingScheme[]` — the marking schemes
4. `GetPracticeItems(subject: string, lo_code: string) -> PracticeItem[]` — the formative items
5. `GetFoundations() -> Foundation[]` — the 5 NCCA root-level PDFs
6. `GetNotebooks(subject: string) -> Notebook[]` — the marimo notebooks

#### Scenario: A student asks for past papers

- **GIVEN** a student is on `/en/subjects/mathematics/papers`
- **WHEN** the student selects "2017-2025" from the year range filter
- **THEN** the BAML `GetPastPapers("mathematics", 2017, 2025)` returns the past papers
- **AND** the papers are rendered as a list with the year + paper + topic tags
- **AND** each paper links to the CF R2 signed URL
- **AND** each paper links to its corresponding marking scheme

## MODIFIED Requirements

None — this is a new spec.

## REMOVED Requirements

None — the existing `rewrite-cianfhoghlaim-leaving-cert-v2` spec
remains. The new `cianfhoghlaim-website-rewrite` spec is additive.

## Cross-references

- `/Users/cianmacandeisigh/dev/kings_college_galway/.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md`
  (the CopilotKit a2ui-renderer skill used for the A2UI surface rendering)
- `baml_src/education/subjects/qpack_*.baml` (the 8 subject BAML schemas)
- `baml_src/education/_shared/eiraic_treasures.baml` (the 13 éraic treasures)
- `baml_src/education/_shared/subject_rubric.baml` (the marking scheme rubric)
- `cocoindex/cross_subject_competency_embedding.py` (the 5×8 mastery matrix)
- `dlt/british_isles/ireland/ncca_root_pdfs.py` (the 5 NCCA root-level PDFs)
- `agents/tuatha/agents/{8 subject agents + cross_subject_agent + cianfhoghlaim_operator}.py`
- `notebooks/leaving_cert/{8 subject notebooks}.py`
- `meaisínfhoghlaim/models/registry.py` (the 24-entry OCR/VLM registry)
- `web/apps/cianfhoghlaim-leaving-cert/` (the existing web app)
- The reference sites: khanacademy.org (Khanmigo + mastery), labs.iximiuz.com
  (6 content types + sandboxes), dojo.ag-ui.com (AG-UI + A2UI demos)