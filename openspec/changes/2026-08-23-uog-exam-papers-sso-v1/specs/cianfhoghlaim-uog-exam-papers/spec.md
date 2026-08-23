# cianfhoghlaim-uog-exam-papers Specification

## Purpose

`cianfhoghlaim-uog-exam-papers` is the **authenticated, single-tenant** companion
to `cianfhoghlaim-university-deep-extraction`. It extends the existing public
UoG pipeline (`course_pages / module_pages / programme_pages / handbook_pdfs /
lecturer_pages`) with a sealed-pipeline layer that ingests the **past-exam-paper
corpus** the student sees after Campus Identity login at
`https://auth.universityofgalway.ie`.

The thesis link is the **exam ↔ learning-outcome mapping**: every exam paper
question has a Bloom-level cognitive target and an LO code, and the proposed
`UoGExamPaper-COVERS-UoGModuleDescriptor` Cognee edge is the formal evidence
that an LO is in fact assessed.

This is **not** a generic multi-university scraper. It is a single-tenant,
Infisical-credentialed, opt-in pipeline that can be enabled or disabled per run.

## Requirements

### Requirement: Three-tier secret resolution

The system SHALL resolve the two `UoGSsoConfig` secrets
(`student_id`, `student_password`) through the canonical
`SecretsResolver.get(name) -> str | None` priority chain:

1. **Self-hosted Infisical** — read from `${INFISICAL_URL}/api/v3/secrets/raw/${name}`
   using `${INFISICAL_TOKEN}` (machine identity) inside the project
   `${INFISICAL_PROJECT}` and environment `${INFISICAL_ENV}` (default `dev`).
   A 4xx from Infisical is treated as "secret not present", not as an error.
2. **Local `.env` fallback** — fall back to `os.environ[name]` (e.g.
   `OOG_STUDENT_ID` / `OOG_STUDENT_PASSWORD`). This is the **default**
   and is the only path the CI runners ever take.
3. **OnePassword CLI (documented only)** — `op read op://Private/University
   SSO/${name}` is **not** invoked by the runner. It is documented in
   `specs/cianfhoghlaim-uog-exam-papers/design/auth-credential-priority-chain.md`
   as the option for users who clone the repo and want Infisical feature
   parity using their own 1Password vault.

The SecretsResolver SHALL emit a single structured-log line on first
read per process: `secrets_backend_resolved` with the chosen backend name.

#### Scenario: Local `.env` resolves in CI

- **GIVEN** no `INFISICAL_*` env vars are set on the CI runner
- **AND** `.env` contains `OOG_STUDENT_PASSWORD=fixture-only`
- **WHEN** `SecretsResolver().get("OOG_STUDENT_PASSWORD")` is called
- **THEN** it returns `"fixture-only"`
- **AND** the first call logs `secrets_backend_resolved: backend="env"`
- **AND** no Infisical HTTP call is made

#### Scenario: Infisical wins when configured

- **GIVEN** `INFISICAL_TOKEN`, `INFISICAL_URL`, `INFISICAL_PROJECT`, and
  `INFISICAL_ENV` env vars are set
- **AND** the project has the secret `OOG_STUDENT_PASSWORD` mapped to a real value
- **WHEN** `SecretsResolver().get("OOG_STUDENT_PASSWORD")` is called
- **THEN** the value from Infisical is returned
- **AND** the first call logs `secrets_backend_resolved: backend="infisical"`
- **AND** `os.environ["OOG_STUDENT_PASSWORD"]` is **not** read

#### Scenario: OnePassword CLI is not invoked

- **GIVEN** `OP_SERVICE_ACCOUNT_TOKEN` is set (a cloner has logged into 1Password)
- **AND** no `INFISICAL_*` env vars are set
- **WHEN** the resolver runs
- **THEN** the resolver SHALL NOT invoke `op`
- **AND** it SHALL fall through to the `.env` lookup
- **AND** it SHALL log a one-line info note
  `"secrets_op_service_account_present_but_doc_only" path="op.read"
   hint="See design/auth-credential-priority-chain.md to enable 1Password manually"`

### Requirement: Browser backend SSO support

The canonical `BrowserBackend` SHALL accept `user_data_dir: Path | None = None`
and `storage_state_path: Path | None = None` kwargs on `initialize()`, so an
authenticated Playwright persistent context can be opened.

When both paths are `None` (default), the backend SHALL behave identically to
pre-change (anonymous, fresh context). When at least one is set, the backend
SHALL:

- Persist cookies + localStorage in `user_data_dir` (Playwright "user data dir" mode).
- Pre-load cookies from `storage_state_path` if it exists.

#### Scenario: Persistent login survives a restart

- **GIVEN** `UoGSsoLogin.login()` has succeeded once with
  `user_data_dir=Path("~/.cache/uog-sso")` and
  `storage_state_path=Path("~/.cache/uog-sso/state.json")`
- **WHEN** a second run starts with the same paths and
  `UoGSsoConfig.has_real_credentials() == True`
- **THEN** `UoGSsoLogin.login()` SHALL complete in < 2.0 s (no SSO
  round-trip, no 2FA challenge)
- **AND** the Dagster asset `uog_exam_login_health` SHALL log `auth_kind="cached"`

#### Scenario: CI runner sees fixture-only

- **GIVEN** `UoGSsoConfig.has_real_credentials() == False` (no real SSO creds)
- **WHEN** the asset `uog_exam_login_health` runs
- **THEN** it SHALL emit `MaterializeResult(skipped=True,
  metadata={"reason": "fixture-only credentials"})`
- **AND** it SHALL NOT touch the Playwright browser
- **AND** no HTTP call to Infisical is made (`SecretsResolver` short-circuits)

### Requirement: Authenticated DLT source with 5 resources

The system SHALL provide `uog_exam_papers_source` at
`dlt_sources/british_isles/ireland/education/university/exam_papers/uog_exam_papers_source.py`
yielding 5 `@dlt.resource` resources:

1. `exam_papers` (primary_key `[module_code, academic_year, sitting, paper_format, language, content_hash]`)
2. `marking_schemes` (primary_key `[module_code, academic_year, sitting, content_hash]`)
3. `model_solutions` (primary_key `[module_code, academic_year, sitting, content_hash]`)
4. `supplementary_papers` (primary_key `[module_code, academic_year, sitting, content_hash]`)
5. `all_exam_materials` (primary_key `[module_code, academic_year, sitting, material_type, content_hash]`)

All resources SHALL use `write_disposition="merge"` and `merged_at` timestamp.

When `UoGSsoConfig.has_real_credentials() == False`, the source SHALL emit one
`status="skipped_fixture"` row per resource (not crash), so DLT pipelines
remain valid in CI.

#### Scenario: An M.Sc. AI module is fully indexed

- **GIVEN** `UoGSsoConfig.has_real_credentials() == True`
- **AND** the module `CT516 (Deep Learning)` has 6 past papers on the
  authenticated index (2020-2025, 2 sittings each)
- **WHEN** `uog_exam_papers_source(modules=["CT516"])` is materialised
- **THEN** `exam_papers` SHALL yield 12 rows (6 papers × 2 sittings)
- **AND** `marking_schemes` SHALL yield 12 rows
- **AND** `model_solutions` SHALL yield ≥ 6 rows (for years ≥ 2022)
- **AND** every row's `source_url` SHALL match `^https://exams\.universityofgalway\.ie/`

#### Scenario: Re-running the source is idempotent

- **GIVEN** a previous run has written the 12 CT516 rows
- **WHEN** `uog_exam_papers_source(modules=["CT516"])` is re-materialised
- **THEN** exactly the same 12 rows are merged (no duplicates,
  `load_info.load_packages[0].jobs[0].file_path[-12:] == last_run_hash`)

### Requirement: BAML exam-paper + syllabus schema

The system SHALL provide the BAML file
`baml_src/british_isles/ireland/education/university/uog_exam_paper_extraction.baml`
with:

- `class UoGExamPaper extends ExamPaper { module_code, programme_code,
  semester, sitting: UoGSitting, paper_format: UoGPaperFormat,
  language: "en" | "ga", source_kind: UoGProvenanceKind }`
- `class UoGSyllabusDescriptor extends ModuleDescriptor { syllabus_pdf_url,
  source_kind: UoGProvenanceKind, exam_paper_overlap_score: float? }`
- `class UoGLearningOutcome` with Bloom-level + action verbs
- `enum UoGSitting { AUTUMN, SPRING, SUMMER, AUTUMN_SUPPLEMENTARY, WINTER }`
- `enum UoGPaperFormat { WRITTEN_ONLINE, MCQ_BANK, PDF_UPLOAD, TAKE_HOME, OPEN_BOOK }`
- `enum UoGProvenanceKind { PUBLIC_WEB, AUTH_PDF, PUBLIC_WEB_AUTH_PDF_MERGED }`

Functions:
- `ExtractUoGExamPaper(pdf_text, module_code, academic_year) -> UoGExamPaper`
- `ExtractUoGSyllabus(syllabus_pdf_text) -> UoGSyllabusDescriptor`
- `MapUoGExamQuestionsToLOs(exam: UoGExamPaper, lo_codes: string[]) -> map<string, string[]>`

All three route through the canonical `ExtractEn` LiteLLM client.

#### Scenario: An M.Sc. AI CT516 paper is extracted by GLM-4.6V

- **GIVEN** the downloaded PDF `downloads/uog_exam_papers/CT516/2023/summer/AUTUMN.pdf`
- **WHEN** `b.ExtractUoGExamPaper(pdf_text, module_code="CT516",
  academic_year=2023)` is called
- **THEN** the returned `UoGExamPaper` SHALL include
  - `module_code = "CT516"`
  - `programme_code = "MSCAI"`
  - `semester = SEMESTER_1`
  - `sitting = AUTUMN`
  - 5–8 `questions` with marks + Bloom-level + LO-code tags
  - `source_kind = AUTH_PDF`
  - `source_url` matching the authenticated index URL
  - `confidence >= 0.75`

#### Scenario: BAML round-trip preserves the new fields

- **GIVEN** the deterministic eval `exam_module_code_consistency` runs over
  20 hand-graded papers in `tests/uog_exam/fixtures/`
- **WHEN** each paper is run through `ExtractUoGExamPaper`
- **THEN** 100 % of rows SHALL have `module_code` matching the regex
  `^[A-Z]{2,4}\d{3,4}$`
- **AND** 100 % of rows SHALL have `programme_code` ∈ {`MSCAI`,`MSCCS`,
  `BScCS`,`BScMath`,`BScStats`,...} (a permitted-programme whitelist)

### Requirement: 5 Dagster assets in the `uog_exam_papers` group

The system SHALL provide 5 Dagster assets in
`dlt_sources/.../university/exam_papers/uog_exam_assets.py` under
group_name `"uog_exam_papers"`:

1. `uog_exam_login_health` (compute_kind=`"sensor"`) — `@asset_check`-style
   asset that pings the authenticated index, no-op'd when
   `UoGSsoConfig.has_real_credentials() == False`.
2. `uog_exam_module_discovery` (compute_kind=`"scrape"`) — drives
   `UoGExamScraper.discover_module_codes(school_slug)`.
3. `uog_exam_papers_download` (compute_kind=`"scrape"`) — drives
   `list_papers` + `download`, persists to `downloads/uog_exam_papers/`.
4. `uog_exam_papers_ocr_extract` (compute_kind=`"baml"`) — invokes
   `b.ExtractUoGExamPaper` on each downloaded PDF, persists to
   `cianfhoghlaim.education.ie.uog_exam_papers` DuckLake table.
5. `uog_exam_los_map` (compute_kind=`"baml"`) — runs
   `b.MapUoGExamQuestionsToLOs`, persists to
   `cianfhoghlaim.education.ie.uog_exam_lo_map`.

#### Scenario: Asset ordering follows discovery → download → extract → map

- **WHEN** Dagster executes the `uog_exam_papers` group
- **THEN** `uog_exam_login_health` runs first
- **AND** `uog_exam_module_discovery` runs after the health check
- **AND** `uog_exam_papers_download` runs after discovery
- **AND** `uog_exam_papers_ocr_extract` runs after download
- **AND** `uog_exam_los_map` runs after `uog_exam_papers_ocr_extract`
  and the existing `uog_extract_modules` asset (cross-group dep)

### Requirement: Secret backend doctest gates the asset

The asset `uog_exam_login_health` SHALL short-circuit when
`UoGSsoConfig.has_real_credentials() == False`. The "real credentials" check
SHALL be:

1. `SecretsResolver.get("OOG_STUDENT_ID") is not None`, AND
2. `SecretsResolver.get("OOG_STUDENT_PASSWORD") is not None`, AND
3. The resolved password is **not** the placeholder value
   `"fixture-only"` (or any value in the `UoGSsoConfig.fixture_only_passwords`
   set).

#### Scenario: A cloned repo without Infisical falls back to `.env`

- **GIVEN** a fresh clone of the repo without Infisical configured
- **AND** the developer has copied `.env.template` → `.env` and left
  `OOG_STUDENT_PASSWORD=fixture-only`
- **WHEN** `dagster asset materialize uog_exam_login_health` runs
- **THEN** `UoGSsoConfig.has_real_credentials() == False`
- **AND** the asset materialises with `metadata={"status": "skipped_fixture"}`
- **AND** no HTTP call to Infisical is made

