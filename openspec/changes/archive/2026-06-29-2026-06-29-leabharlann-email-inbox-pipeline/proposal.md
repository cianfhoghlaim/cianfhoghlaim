# Change: 2026-06-29-leabharlann-email-inbox-pipeline

## Why

The Cianfhoghlaim platform can ingest the **leabharlann** personal archive
(225 Gemini Deep Research PDFs across 6 subdirs) into the lakehouse
(DuckLake + LanceDB) and the cognify graph, but the user's actual
working context — **personal + professional email** across 4 accounts
(DKIT.ie Microsoft 365, 2 Gmail, Hotmail) — sits outside the system
entirely. The platform can answer "what does my leabharlann say about
HSE Ireland malpractice?" but cannot answer "which email thread about
HSE Ireland malpractice do I still owe a reply on?".

This change closes that loop by adding an end-to-end **email inbox
pipeline** that:

1. Pulls mail from all 4 external accounts into a **Mailcow
   self-hosted** IMAP server (`bonneagar/stacks/mailcow-dockerized/` —
   already provisioned), via the built-in `dovecot_imapsync_runner`
   ofelia job (no new sync code, just per-account credentials in
   Infisical).
2. Exposes the MBOX exports to the data plane via a new
   `leabharlann.email_inbox` DLT source that reuses the existing
   `_scanner.py` PathGrammar + adds Python `mailbox`-stdlib MBOX
   parsing + `In-Reply-To` thread reconstruction + a 4-account
   `account` partition key + a `legal_flag` heuristic.
3. Embeds messages into LanceDB via a 4th v1 CocoIndex App
   (`leabharlann_inbox_embedding`) using BAAI/bge-large-en-v1.5
   (1024-d cosine) — same shared `EMBEDDER` / `LANCE_DB` ContextKey
   as the existing 3 Apps.
4. Adds 5 new Dagster assets to the `leabharlann_ingestion` group
   (raw + BAML classify + BAML thread extract + CocoIndex embed +
   research-link), growing the group from 7 → 12 assets.
5. Adds a new BAML file `email.baml` with 3 functions
   (`ClassifyEmail`, `ExtractEmailThread`, `LinkEmailToResearch`)
   that auto-categorise the 9 EmailClass labels and link each legal
   thread to the top-3 Gemini Deep Research PDFs (from
   `leabharlann/gemini_deep_research/law/` + `/medical/` for the
   example flows).
6. Adds a **new Google ADK `email_triage` agent** on the oideachais
   stack (port 7778) with 4 tools
   (`classify_email_thread`, `summarise_thread`,
   `link_thread_to_research`, `find_loose_threads`) that the
   marimo notebook + the openclaw WebChat both call.
7. Adds a marimo notebook `email_inbox_triage.py` with 5 sections
   (loose threads, legal prioritisation, medical prioritisation,
   thread explorer, hybrid search) — the primary dev surface, per
   the user's preference for marimo over WebChat for dev work.
8. Adds a lightweight **openclaw WebChat** `email` sub-UI
   (`openclaw.cianfhoghlaim.ie/email`) for ad-hoc manual tagging
   from a phone or a chat window — secondary surface.

The end-to-end demo exercises 1 sample legal thread (DKIT.ie
Microsoft 365 → Mailcow → MBOX → DLT → BAML → 3 Gemini PDFs from
`gemini_deep_research/law/` linked) on the live lakehouse stack
(Garage S3 + Lakekeeper + Lance Namespace) and surfaces the result
in the marimo notebook.

## What Changes

### 1. New DLT source `leabharlann/email_inbox.py`

`@dlt.source(name="leabharlann_email_inbox")` yields 4 resources:
`inbox_index`, `inbox_threads`, `inbox_attachments`,
`inbox_legal_threads`. MBOX parsing via Python's `mailbox` stdlib
(single-pass `mailbox.mbox(path)` iterator). Thread reconstruction
via `In-Reply-To` + `References` chain + normalised `Subject`
(strips `Re:`, `Fwd:`, `Fwd: Re:`, `[list-tag]`). Partition keys:
`account` (DynamicPartitionsDefinition from
`author_archive_accounts.yaml`), `year` (4-digit from `Date`),
`legal_flag` (boolean from first 500-char keyword + sender-domain
regex). GPG-at-rest opt-in for `legal/`, `medical/`, `hsc/`, `nhs/`
prefixes — reuses `_takeout_paths.TakeoutAccountConfig.gpg_encrypt_paths`.
LBYL exception handling per `dignified-python` skill.

### 2. New BAML file `email.baml`

3 classes + 3 functions:
- `EmailClassificationResult` (class_label ∈ EmailClass,
  confidence, urgency_score 0-1, summary_5_words, suggested_action)
  + `ClassifyEmail(email_subject, email_body, sender_domain,
  recipient_domain) -> EmailClassificationResult`
- `EmailThread` (participants, topic_summary, action_items,
  decision_points, dates_mentioned, key_quotes)
  + `ExtractEmailThread(thread_messages: list<string>,
  thread_subject: string) -> EmailThread`
- `ResearchLink` (linked_pdf_id, link_reason, link_confidence,
  snippet) + `LinkEmailToResearch(email_body, candidate_pdfs:
  list<{pdf_id, pdf_title, pdf_summary}>) -> list<ResearchLink>`

`ClassifyEmail` + `ExtractEmailThread` use the `extract_en` client
alias; `LinkEmailToResearch` uses `extract_en_strong` (more
reasoning). Regenerated via `baml_cli generate`.

### 3. New v1 CocoIndex App `leabharlann_inbox_embedding`

4th App alongside `leabharlann_books_embedding`,
`leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`.
Source: `localfs.walk_dir("/srv/mailcow-exports", recursive=True,
path_matcher=PatternFilePathMatcher(included_patterns=["**/*.mbox"],
excluded_patterns=["**/.*"]), live=True)`. Recurses into each MBOX
file via `mailbox.mbox()`, yields one chunk per message
(`from + subject + first 2000 chars of body`). Embeds with
BAAI/bge-large-en-v1.5 (1024-d) via the shared `EMBEDDER`
ContextKey from `_lifespan.py`. Mounts LanceDB target table
`oideachais_inbox_messages` with columns
`(id, account, year, date_iso, subject, sender, recipients,
body_excerpt, embedding, baml_class, baml_urgency, thread_id)`.
Primary key: `id` from `IdGenerator()`. Declares a cosine vector
index on `embedding` AND an FTS index on `subject + body_excerpt`
for hybrid search. Adds `@query_handler` named `search_inbox(query,
account=None, year=None, baml_class=None, urgency_min=None,
limit=20)`.

### 4. 5 new Dagster assets (leabharlann_ingestion group: 7 → 12)

- `leabharlann_inbox_raw` (dlt.run, partition `account`)
- `leabharlann_inbox_baml_classify` (depends on
  `leabharlann_inbox_raw`; invokes `b.ClassifyEmail` per row)
- `leabharlann_inbox_baml_thread_extract` (depends on
  `leabharlann_inbox_raw`; calls `b.ExtractEmailThread` per thread)
- `leabharlann_inbox_embeddings` (depends on
  `leabharlann_inbox_baml_classify`; runs
  `cocoindex update leabharlann_inbox_embedding` via subprocess)
- `leabharlann_inbox_research_links` (depends on
  `leabharlann_inbox_baml_classify` AND
  `leabharlann_gemini_deep_research_raw`; calls
  `b.LinkEmailToResearch` with the top-20 candidate PDFs from
  LanceDB vector search)

Plus an end-to-end demo asset `leabharlann_email_full_stack_demo`
on 1 sample legal thread (dlt → BAML classify → 3 PDF link
candidates from `gemini_deep_research/law/` → CocoIndex update →
marimo) and a 60-second directory-watch sensor updated to
include the `leabharlann_inbox_accounts` dynamic partitions.

### 5. New Google ADK `email_triage` agent (port 7778)

`LlmAgent(name="email_triage", model="gemini-2.5-pro", ...)` with
4 tools:
- `classify_email_thread(thread_id: str) -> EmailClassificationResult`
- `summarise_thread(thread_id: str, max_chars: int = 500) -> str`
- `link_thread_to_research(thread_id: str, k: int = 5) -> list[ResearchLink]`
- `find_loose_threads(account: str, days_idle_min: int = 7) -> list[ThreadSummary]`

All 4 tools are read-only against DuckLake + Lance namespace. The
existing `agents/adk/callbacks/citation_callbacks.py` auto-injects
LanceDB vector-search citations into every tool response. The
oideachais compose service already runs on port 7778 — only the
`email_triage_agent.py` module needs adding (the ADK container
auto-imports it from `agents/adk/__init__.py`). Langfuse auto-traces
every tool call (the existing `LANGFUSE_*` env vars on the
oideachais stack are reused).

### 6. New marimo notebook `email_inbox_triage.py`

5 sections: (1) Loose threads sorted by urgency, (2) Legal-case
prioritisation with linked Gemini PDFs, (3) Medical-access
prioritisation with linked Gemini PDFs, (4) Thread explorer
(`mo.ui.tree`), (5) Hybrid search via the new `search_inbox`
query handler (RRF-fused cosine + BM25). The notebook is the
primary manual-tagging + dev surface (per the user's preference).

### 7. New Cognee cognify stage + cross-archive edges

New dataset `oideachais_email_inbox` with 4 node types:
`EmailThread`, `EmailAccount`, `LegalCase`, `ResearchLink`. New
edge rules in `cognify/rules/leabharlann_cross_archive.py`:
- `EmailThread → LegalCase` (when `baml_class == "legal_case"`)
- `EmailThread → ResearchPDF` (from `LinkEmailToResearch` results)
- `EmailAccount → Person` (from sender full-name resolution)

### 8. New `search_emails` cross-corpus search helper

Extends the `oideachais-semantic-search` capability with a
`search_emails(query, account=None, legal_case=None, status=None)`
helper that queries the new `oideachais_inbox_messages` LanceDB
table and joins results with the cognify graph for richer context
(e.g. "show me emails that link to the `HSE-Ireland-psychiatrist`
legal case from the cognify graph").

### 9. Mailcow wiring (the export spine)

The `bonneagar/stacks/mailcow-dockerized/` stack is already
provisioned (Postfix + Dovecot + SOGo + Rspamd + ClamAV + the
built-in `dovecot_imapsync_runner` ofelia job). The change:

1. Moves the stack from `bonneagar/stacks/mailcow-dockerized/` to
   `cianfhoghlaim/stacks/mailcow-dockerized/` (the v4
   consolidation finished the move for other stacks but Mailcow
   is still in bonneagar).
2. Adds the missing 3 of 6 GOLD_STANDARD files
   (`pangolin.yaml`, `blueprint.yaml`, `.env.example`) — the
   current state has only 5 of 6.
3. Adds 4 per-account IMAP credentials to
   `mailcow-dockerized/secrets.env` referencing
   `infisical://dev-baile/mailcow/imap_credentials/<account>`
   (DKIT.ie M365, gmail_personal, gmail_academic,
   hotmail_legacy).
4. Configures the `dovecot_imapsync_runner` to poll all 4
   external accounts and sync into a Mailcow mailbox
   `inbox-<account>@cianfhoghlaim.ie`.
5. Adds a `mailcow-export` companion container (5-line service
   in `compose.yaml`) that runs `doveadm export` every 6 hours
   and writes `mailbox-<account>-<date>.mbox` to a shared volume
   mounted into the Dagster container.
6. Adds Pangolin private resources for `mail.cianfhoghlaim.ie`
   (webmail), `imap.cianfhoghlaim.ie` (port 993, internal),
   `smtp.cianfhoghlaim.ie` (port 587, internal).
7. Adds a Komodo procedure
   `deploy-mailcow-dockerized-bunchloch.toml` (5-stage:
   prereqs → locket volume → compose up → pangolin routes →
   health check `curl https://mail.cianfhoghlaim.ie/SOGo`).
8. Adds the stack to `bonneagar/iac/komodo/deploy-stacks.ts`
   so the TypeScript IaC knows about the deployment.

**Outbound email is NOT provisioned in v1** (no MX / SPF / DKIM
records needed) — the change is receive-only for IMAP sync. The
Pangolin routes for port 25 / 587 are bound to `127.0.0.1` only
so they cannot relay externally.

### 10. openclaw WebChat `email` sub-UI (secondary surface)

A lightweight `email` sub-UI on `openclaw.cianfhoghlaim.ie/email`
that loads the next loose thread and asks the user to
confirm/override the BAML classification. The confirm/override
writes back to a new `leabharlann_inbox_user_overrides` DuckLake
table (so a future `cocoindex update` picks up the manual tag).
The 10 → 11 curated skills subset grows by 1 symlink to the new
`oideachais-email-triage` skill. The marimo notebook is the
primary manual surface; the WebChat sub-UI is a phone-friendly
secondary surface.

### 11. Phase 0 — fix the `gemini_deep_research` v4 path resolution

`gemini_deep_research.py` resolves `DEFAULT_GEMINI_PATH` to
`parents[3] / "leabharlann" / "gemini_deep_research"`, which
yields `cianfhoghlaim/pipelines/ingest/leabharlann/gemini_deep_research/`
— a path that **does not exist on disk** (the 225 PDFs live at
`/Users/.../kings_college_galway/leabharlann/gemini_deep_research/`).
The current source logs `directory_not_found` and yields 0 rows.

The change adds `AUTHOR_ARCHIVE_GEMINI_PATH` to `.infisical.env`
+ `.env.example` pointing at the on-disk corpus, mirroring the
existing `USE_LOCAL_SCRAPES` + `LEABHARLANN_TAKEOUT_ROOT` patterns.
This unblocks every downstream leabharlann asset
(`leabharlann_gemini_deep_research_raw`,
`leabharlann_full_stack_demo`, the new
`leabharlann_inbox_research_links`).

### 12. `identity/` subdir handling

`identity/` is in the `GEMINI_DOMAINS` set but the on-disk
directory is empty (0 files). The dlt source's PathGrammar
already no-ops on missing subdirs (because `iterdir()` skips
missing children). The spec's "12 + 45 + 11 + 20 + 8 + 120 =
216" document count is **stale**; the actual on-disk totals
are 31 + 57 + 54 + 47 + 24 + 12 = **225** across 6 subdirs. The
change updates the `oideachais-leabharlann` spec to reflect
the new totals (a small spec correction that rides along).

### 13. 10 appropriate PDFs per subdir (for the e2e demo)

For the end-to-end demo (1 legal thread → 3 PDFs), the highest-
yield picks are:

- **`law/`** (10): `medical_malpractice_lawsuit_against_irish_psychiatrist.pdf`
  (HSE Ireland), `qub_royal_victoria_malpractice.pdf` (QUB +
  HSC NI), `cross_border_medical_malpractice_and_data_breach.pdf`
  (HSE + NHS), `discrimination_case_strategy_university_of_galway.pdf`
  (UoG), `qub_discrimination_and_eviction_investigation.pdf` (QUB),
  `english_noise_tenancy_and_discrimination_laws.pdf` (UoG),
  `maximizing_civil_suit_damages_against_qub.pdf` (QUB),
  `data_request_for_university_records.pdf` (UoG),
  `damages_estimates_tax_plannings.pdf`,
  `medical_malpractice_lawsuit_against_irish_psychiatrist.pdf` (HSE).
- **`medical/`** (10): `hse_malpractice.pdf` (HSE),
  `hse_trauma.pdf` (HSE), `british_isles_treatment_dual_citizen.pdf`
  (HSE + NHS), `accessing_medical_cannabis_across_british_isles.pdf`
  (HSE + NHS), `cptsd_summary.pdf`,
  `disability_allowance_application_assistance.pdf` (HSE),
  `disability_allowance_and_medical_records_dispute.pdf` (HSE),
  `malpractice_belfast.pdf` (HSC NI), `sodium_valproate_lawsuits_and_inquiries.pdf`
  (HSE), `mental_health_misdiagnosis_and_damages.pdf` (HSE).
- **`culture/`** (10): `ireland_uk_education_policy_comparison.pdf`,
  `reclaiming_education_access_and_funding.pdf` (SUSI),
  `university_galway_irish_language_resources.pdf` (UoG),
  `celtic_language_learning_for_gaeilgeoir.pdf` (UoG Acadamh),
  `celtic_language_digital_revitalization_strategy.pdf`,
  `digital_resources_for_celtic_languages.pdf`,
  `irish_language_copyright_and_education_2.pdf`,
  `irish_traveller_identity_prejudice_and_travel.pdf`,
  `bridging_divides_through_shared_culture.pdf`,
  `the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf`.
- **`politics/`** (10): `fine_gael_coalition_strategy_analysis.pdf`,
  `farrell_sinn_f_in_and_united_ireland_rhetoric.pdf`,
  `galway_west_election_candidate_analysis.pdf`,
  `galway_by_election_media_analysis.pdf`,
  `housing_policy_infrastructure_and_cost_analysis.pdf`,
  `uk_ireland_social_media_regulation_child_safety.pdf`,
  `irish_neutrality_and_us_military_transit.pdf`,
  `fiscal_stasis_consociational_dysfunction_and_the.pdf`,
  `intelligence_disinformation_and_geopolitics.pdf`,
  `whistleblower_investigates_scottish_officials.pdf`.
- **`technology/`** (10): `ai_for_exam_paper_analysis.pdf`,
  `regulating_big_tech_in_british_isles.pdf`,
  `gemini_s_safety_privacy_and_origins.pdf`,
  `google_s_ai_regulation_and_competitors.pdf`,
  `openai_controversies_and_criticisms_research.pdf`,
  `musk_s_ventures_failures_risks_and_neuralink.pdf`,
  `instagram_data_regulation_and_influence.pdf`,
  `russia_us_cyber_influence_comparison.pdf`,
  `crypto_assault_and_legal_recourse.pdf`,
  `uk_security_job_eligibility_research.pdf`.
- **`other/`** (10): `irish_public_service_disability_accommodation.pdf`
  (HSE), `uk_vs_ireland_surrogacy_and_ivf.pdf` (HSE + NHS),
  `russell_group_whistleblower_protocol_inquiry.pdf` (QUB),
  `reclaiming_irish_monetary_sovereignty.pdf`,
  `investigating_radicalization_and_venues.pdf`,
  `radicalization_manipulation_and_prevention_strategies.pdf`,
  `london_boroughs_funding_and_cleanliness_investigation.pdf`,
  `veolia_outsourcing_and_neglect_investigation.pdf` (HSE),
  `irish_rail_investment_and_connectivity.pdf`,
  `british_isles_future_tech_culture_commonwealth.pdf`.
- **`identity/`** (0): empty on disk; the `gemini_deep_research.py`
  PathGrammar already no-ops. Best substitute for the `identity/`
  theme is `culture/irish_traveller_identity_prejudice_and_travel.pdf`
  + `culture/claiming_irish_kingship_through_lineage.pdf`.

## Impact

### Affected specs (MODIFIED)
- `oideachais-leabharlann` — +3 Requirements (email_inbox source,
  MBOX CocoIndex App, email inbox Dagster assets) + 1 spec
  correction (225 docs / 6 subdirs)
- `oideachais-baml-schemas` — +1 BAML file `email.baml`
- `oideachais-cocoindex-v1-migration` — +1 v1 App
  `leabharlann_inbox_embedding`
- `oideachais-cognify-knowledge-graph` — +1 cognify stage
  (`oideachais_email_inbox`) + 3 cross-archive edge types
- `oideachais-marimo-dashboards` — +1 notebook
  `email_inbox_triage.py`
- `oideachais-semantic-search` — +1 cross-corpus helper
  `search_emails`
- `infrastructure-stacks` — +1 stack row for the
  `mailcow-dockerized` move + wiring
- `meaisinfhoghlaim-agent-frameworks` — +1 ADK agent row
  (`email_triage`)
- `author-archive-pipeline` — cross-references the new inbox
  assets
- `author-archive-cross-corpus-kg` — +3 edge types
  (`EmailThread → LegalCase`, `EmailThread → ResearchPDF`,
  `EmailAccount → Person`)

### New capability (NEW)
- `oideachais-email-triage` — the dedicated email-triage
  surface (BAML + marimo + openclaw + ADK)

### New files
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/_email_accounts.example.yaml`
- `cianfhoghlaim/core/baml/_oideachais_src/email.baml`
- `cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py`
  (+ `leabharlann_inbox_embedding` App)
- `cianfhoghlaim/agents/adk/email_triage_agent.py`
- `cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`
- `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py`
- `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py`
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leabharlann_inbox_assets.py`
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leabharlann_email_full_stack_demo.py`
- `cianfhoghlaim/assets/_oideachais_dagster_defs/sensors/leabharlann_inbox_sensors.py`
- `cianfhoghlaim/stacks/mailcow-dockerized/{compose,sidecar,secrets.env,pangolin.yaml,blueprint.yaml,.env.example}.yaml`
- `cianfhoghlaim/stacks/mailcow-dockerized/README.md`
- `infrastructure/komodo/stacks/mailcow-dockerized-bunchloch.toml`
- `infrastructure/komodo/procedures/deploy-mailcow-dockerized-bunchloch.toml`
- `infrastructure/komodo/procedures/deploy-leabharlann-email-inbox-bunchloch.toml`
- `infrastructure/stacks/openclaw/skills-curated/oideachais-email-triage`
  (1 new symlink — 10 → 11)
- `.agents/skills/oideachais-email-triage/SKILL.md`
- `openspec/specs/oideachais-email-triage/spec.md` (canonical home)

### Modified files
- `openspec/specs/oideachais-leabharlann/spec.md` — +3 Requirements,
  1 spec correction
- `openspec/project.md` — +1 capability row
- `.infisical.env` — +7 vault refs
  (`mailcow/db_root`, `mailcow/db_pass`, `mailcow/hostname`,
  `mailcow/admin_pass`, `imapsync/<account>/user`,
  `imapsync/<account>/app_password` × 4 accounts)
- `infrastructure/AGENTS.md` — +1 stack row
- `bonneagar/iac/komodo/deploy-stacks.ts` — +2 stack entries
- `cianfhoghlaim/stacks/openclaw/config/openclaw.json` — +1
  `channel_overrides` entry for `email_triage`
- `infrastructure/stacks/openclaw/config/openclaw.json` — same

### Affected agent skills
- `.agents/skills/oideachais-email-triage/SKILL.md` (NEW)
- `.agents/skills/oideachais-leabharlann/SKILL.md` — +1 section
  on the email_inbox source
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` — +1 v1 App
  pattern in the "9 v1 Apps" list
- `.agents/skills/google-adk/SKILL.md` — +1 agent in the
  "10 ADK agents" list
- `.agents/skills/agent-fleet-orchestration/SKILL.md` —
  +1 paragraph on the `email_triage` agent
- `.agents/skills/infrastructure-stacks/SKILL.md` — +1 row in
  the 90-stack inventory for mailcow-dockerized

### Affected CI
- `bun run validate-stacks` (stack-doctor 4-gate check) — the
  mailcow-dockerized stack must pass all 4 gates
- `mise run lint:skills` — the new SKILL.md must pass the
  4 metadata rules
- `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict` — every `### Requirement:` must
  have at least one `#### Scenario:`

### Affected workflows
- `komodo run procedure deploy-mailcow-dockerized-bunchloch` —
  new 5-stage procedure
- `komodo run procedure deploy-leabharlann-email-inbox-bunchloch` —
  new 6-stage procedure
- `bun run secrets:init` — pulls 7 new vault refs into the
  hydrated `.env`

## Non-Goals

- This change does **NOT** provision outbound email (no MX / SPF /
  DKIM records). v1 is **receive-only** for IMAP sync.
- This change does **NOT** add a new LLM provider. The ADK agent
  uses the existing `gemini-2.5-pro` model via LiteLLM. The
  BAML functions use the existing `extract_en` + `extract_en_strong`
  clients.
- This change does **NOT** add a new CocoIndex target. The new
  App uses the existing LanceDB target via the shared `LANCE_DB`
  ContextKey.
- This change does **NOT** add a new MBOX parser library. Python's
  `mailbox` stdlib is sufficient.
- This change does **NOT** add a new OCR backend. The 11 OCR
  models + 4 classical OCR stacks are sufficient for the
  attachment OCR if any (most attachments are PDF/DOCX already).
- This change does **NOT** provision Signal / iMessage / Matrix
  for the openclaw channels — those stay `enabled: false`.
- This change does **NOT** add a new `identity/` subdir file
  count. The subdir is empty on disk; the change documents the
  state and the dlt source no-ops gracefully.
- This change does **NOT** introduce a new namespace for the
  MBOX data. It reuses `ducklake_oideachais.inbox_*` and
  `oideachais_inbox_*` LanceDB tables per the v4 storage
  contract.
- This change does **NOT** re-architect the existing
  `google_takeout.py` Phase 2 stubs (OAuth + Drive API + Gmail
  export). The new `email_inbox.py` complements the Phase 1
  filesystem source.
- This change does **NOT** rewrite the openclaw upstream
  Dockerfile; the WebChat `email` sub-UI uses the existing
  upstream image with a single 11th curated skills symlink.
- This change does **NOT** ship the actual leabharlann
  gemini_deep_research PDFs as binary content in the repo. The
  PDFs already live on disk (225 files) and are accessed via the
  `AUTHOR_ARCHIVE_GEMINI_PATH` env var override.

## Risk Assessment

- **Risk: Mailcow is heavy (15 containers, ~3 GB RAM).** arm1-oci
  is at 70% utilization per the 2026-06 audit and would not
  survive. bunchloch (M4 Max) is fine. **Mitigation:** the Komodo
  procedure targets `bunchloch` only; the `infrastructure/audit/scripts/inventory-arm1-oci.sh`
  pre-flight rejects the deploy if utilization exceeds 80%.
- **Risk: Gmail + Microsoft 365 OAuth token rotation.** App
  passwords are the fallback. **Mitigation:** the change uses
  the `dovecot_imapsync_runner` Mailcow-native job with Google
  App Passwords + Microsoft "App Password" for DKIT.ie M365; no
  full OAuth flow in v1. The pre-flight task 0.3 documents the
  per-account credential setup (Google account → Security → App
  passwords; Microsoft account → Security → App passwords).
- **Risk: MBOX parsing is slow at scale** (a 2 GB MBOX with 200k
  messages). **Mitigation:** stream-parse via
  `mailbox.mbox(path)` iterator (never loads full file). The
  CocoIndex App processes one message at a time (memoised via
  `@coco.fn(memo=True)`). The end-to-end demo runs on a
  representative sample, not the full mailbox.
- **Risk: BAML `LinkEmailToResearch` is expensive** (LLM call
  per (email, k) pair). **Mitigation:** memoise on
  `(email_id, candidate_pdf_id)` via `@coco.fn(memo=True)`;
  re-evaluate only when either side changes. The dagster asset
  defaults to top-k=20 candidate PDFs (configurable).
- **Risk: Privacy** — emails are highly sensitive (HSE Ireland
  medical case content, QUB discrimination case content). **Mitigation:**
  the 6-file GOLD_STANDARD is enforced; GPG-at-rest opt-in for
  `legal/`, `medical/`, `hsc/`, `nhs/` prefixes; Lakehouse is
  Pangolin-private; Locket sidecar restricts secret access;
  the oideachais ADK agent uses the existing Pocket ID SSO.
- **Risk: openclaw WebChat becomes a PII surface** (the user
  pastes thread content in chat). **Mitigation:** `dmPolicy: "pairing"`
  (existing openclaw contract) + Pocket ID SSO + the curated
  10 → 11 skill subset keeps the surface narrow. The marimo
  notebook is the primary manual surface.
- **Risk: marimo notebook can grow unwieldy** (5 sections ×
  DuckDB + Lance + BAML + ADK). **Mitigation:** each section is
  its own `@app.function` cell; only re-runs dirty cells
  (marimo's reactivity). The notebook is split into 5
  sub-notebooks via marimo's `mo.ui.tabs` for production.
- **Risk: v4 path resolution bug for `gemini_deep_research`**
  (the 225 PDFs on disk are not at the path the dlt source
  resolves to). **Mitigation:** Phase 0 task 0.1 sets
  `AUTHOR_ARCHIVE_GEMINI_PATH` in `.infisical.env` + `.env.example`,
  unblocking every downstream leabharlann asset.

## Validation

1. `docker compose -f cianfhoghlaim/stacks/mailcow-dockerized/compose.yaml config`
   parses successfully.
2. `docker compose -f cianfhoghlaim/stacks/mailcow-dockerized/compose.yaml -f cianfhoghlaim/stacks/mailcow-dockerized/sidecar.yaml config`
   parses successfully and shows `locket` as `service_healthy`
   dependency.
3. `cianfhoghlaim/stacks/mailcow-dockerized/pangolin.yaml` matches
   the 6-label shape.
4. `bun run validate-stacks` (stack-doctor) passes all 4 gates
   with mailcow-dockerized present.
5. `baml_cli generate` succeeds with the new `email.baml`.
6. `bun run ccc:index` succeeds after the new source + agent
   + notebook files land.
7. `mise run lint:skills` passes (the new
   `oideachais-email-triage` SKILL.md plus the 5 updated skills
   all pass the 4 metadata rules).
8. `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict`
   passes — every `### Requirement:` has at least one
   `#### Scenario:`, and every `#### Scenario:` uses the
   WHEN / THEN / AND structure.
9. (post-deploy) The end-to-end demo asset
   `leabharlann_email_full_stack_demo` materialises successfully
   in the Dagster UI at `oideachais.cianfhoghlaim.ie/dagster`
   and produces ≥ 1 legal-case thread with 3 linked Gemini PDFs.
10. (post-deploy) The marimo notebook
    `email_inbox_triage.py` launches at
    `marimo.cianfhoghlaim.ie/email-inbox-triage` and renders
    the 5 sections against the live LanceDB + DuckLake data.
