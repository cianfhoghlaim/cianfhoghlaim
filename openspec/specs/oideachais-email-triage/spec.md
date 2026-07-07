# Oideachais Email Triage Capability

## Purpose

`oideachais-email-triage` is a capability of the Cianfhoghlaim
platform. It composes the leabharlann DLT + BAML + CocoIndex + Dagster +
ADK + marimo + Cognee + Mailcow + openclaw sub-systems into a single
end-to-end email-triage surface for the user's personal + professional
email (4 accounts: DKIT.ie M365, 2 Gmail, Hotmail).

The corresponding source code lives at:

- `cianfhoghlaim/dlt/leabharlann/email_inbox.py` (the MBOX DLT source `leabharlann_email_inbox`)
- `cianfhoghlaim/baml/email.baml` (the `ClassifyEmail`, `ExtractEmailThread`, `LinkEmailToResearch` BAML functions)
- `cianfhoghlaim/cocoindex/leabharlann_inbox_embedding.py` (the 4th v1 CocoIndex App `leabharlann_inbox_embedding`)
- `cianfhoghlaim/agents/adk/email_triage_agent.py` (the Google ADK `email_triage` agent on port 7778)
- `cianfhoghlaim/notebooks/dashboards/email_inbox_triage.py` (the marimo notebook — the primary manual surface)
- `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py` (the 4th leabharlann cognify dataset)
- `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py` (the 3 new cross-archive edge types)
- `cianfhoghlaim/stacks/mailcow-dockerized/` (the Mailcow stack with 4 per-account IMAP credentials)

## Background

Before this capability, the user maintained their 4 inboxes manually.
The pipeline turns those inboxes into a single searchable, classified,
cognified, agent-routable stream that joins the existing 6 leabharlann
corpora (aigne, gaeilge, gemini_deep_research, mata, ollscoil_na_gaillimhe,
zotero) + the email inbox corpus via Cognee cross-archive edges.

## Requirements

### Requirement: 4-account MBOX DLT source

The system SHALL provide an MBOX DLT source `leabharlann_email_inbox`
that loads the 4 IMAP accounts (DKIT.ie M365, Gmail × 2, Hotmail) into
the lakehouse. Mailcow fetches mail via IMAP and writes MBOX files;
the DLT source reads the MBOX and yields one row per email.

#### Scenario: First-run MBOX load

- **WHEN** the developer runs `dagster asset materialize leabharlann_email_inbox`
- **THEN** the source SHALL fetch all 4 accounts via Mailcow IMAP
- **AND** yield one row per email with `(account, message_id, from, to, subject, body, received_at, attachments)`
- **AND** dedupe by `(account, message_id)` so re-runs are idempotent

#### Scenario: Incremental load

- **WHEN** the developer runs `dagster asset materialize leabharlann_email_inbox` on a non-empty lakehouse
- **THEN** the source SHALL only yield emails with `received_at` > the previous high-water mark
- **AND** the previous high-water mark SHALL be persisted in `leabharlann_email_inbox._dlt_loads`

### Requirement: email.baml classification + extraction + linking

The system SHALL provide 3 BAML functions in `email.baml`:

- `ClassifyEmail(input: EmailInput) -> EmailClass` — one of `PERSONAL`,
  `WORK_DKIT`, `WORK_RESEARCH`, `WORK_CLIENT`, `NOTIFICATION`, `SPAM`,
  `NEWSLETTER`, `OTHER`. Returns structured fields
  `priority ∈ {LOW, MEDIUM, HIGH, CRITICAL}`, `requires_response: bool`,
  `estimated_response_time_min: int`.
- `ExtractEmailThread(input: EmailInput) -> EmailThread` — extracts the
  thread (subject normalization, body cleanup, signature stripping,
  quoted-reply detection) and the actionable ask.
- `LinkEmailToResearch(input: EmailInput) -> ResearchLink[]` — links
  the email to existing leabharlann corpus records via
  `oideachais_email.*` cross-archive edges (3 new edge types).

#### Scenario: ClassifyEmail triage

- **WHEN** the agent calls `ClassifyEmail` on an incoming email
- **THEN** the function SHALL return an `EmailClass` with one of the 7 categories
- **AND** `priority` SHALL reflect the combined signal of category + sender domain + keyword presence

#### Scenario: Thread extraction

- **WHEN** the agent calls `ExtractEmailThread` on a forwarded email
- **THEN** the function SHALL strip quotes (`>`-prefixed lines + attribution header)
- **AND** detect the actionable ask in the most recent message
- **AND** return a `EmailThread` with `subject_canonical`, `latest_message_body`, `actionable_ask`

#### Scenario: Cross-corpus link

- **WHEN** the email body contains a known phrase ("UCCIX", "Caighdeán", "BGE-M3", "ncca.ie", "teanglann.ie") matching a leabharlann record
- **THEN** `LinkEmailToResearch` SHALL return a `ResearchLink[]` with the matching corpus names + record IDs

### Requirement: 4th v1 CocoIndex App for the inbox

The system SHALL provide a 4th v1 CocoIndex App
`leabharlann_inbox_embedding` that embeds the cleaned email body via
`BAAI/bge-m3` (1024-dim) and lands it in a LanceDB table
`leabharlann_inbox_chunks`. The App SHALL conform to the v1 R1-R4 rules
(lifespan + fn + mount_table_target + 100-batch minimum).

#### Scenario: First-run inbox embedding

- **WHEN** the developer runs `cocoindex update leabharlann_inbox_embedding`
- **THEN** the App SHALL embed all rows from `leabharlann_inbox` >= 100 batch
- **AND** produce one `leabharlann_inbox_chunks` row per email-batch
- **AND** pass `cocoindex_v1_conformance`

### Requirement: Google ADK email_triage agent

The system SHALL provide a Google ADK agent `email_triage` on port 7778
that, given a natural-language query, returns the top-5 matching emails
semantically (using `leabharlann_inbox_chunks` LanceDB) with
classification + thread extraction + cross-corpus links.

#### Scenario: Agent triage query

- **WHEN** the user asks the agent "show me my urgent DKIT emails about UL recommendations"
- **THEN** the agent SHALL call `leabhann_semantic_search("urgent DKIT UL recommendations", top_k=5)`
- **AND** filter by `account == "dkit.ie" AND class == WORK_DKIT AND priority >= HIGH`
- **AND** return 5 rows with `subject`, `from`, `received_at`, `priority`, `thread_summary`, `corpus_links`

### Requirement: marimo primary surface

The system SHALL provide a marimo notebook
`notebooks/dashboards/email_inbox_triage.py` that is the primary manual
surface for email triage. The notebook SHALL:

- Use `mo.sql(engine=md:oideachais)` to query `leabharlann_inbox` directly
- Display a `mo.ui.table` of recent emails with class + priority + thread summary
- Filter controls for account, class, priority, date range
- A semantic-search `mo.ui.text` bar that calls `leabhann_semantic_search`
- A `mo.ui.table` of `corpus_links` (the cross-archive edge results)

#### Scenario: Triage workflow

- **WHEN** the user opens `email_inbox_triage.py`
- **THEN** the notebook SHALL display the last 7 days of email summary
- **AND** the user can click an email to expand the `EmailThread`
- **AND** click a `corpus_link` to jump to the linked research record

## Cross-references

- [`oideachais-leabharlann`](../oideachais-leabharlann/spec.md) — the parent capability (6-source leabharlann corpus)
- [`oideachais-cognify-knowledge-graph`](../oideachais-cognify-knowledge-graph/spec.md) — the cognify + cross-archive rules
- [`agent-fleet-orchestration`](../../../.agents/skills/agent-fleet-orchestration/SKILL.md) — the 12-agent fleet
- [`mailcow-dockerized`](../../../bonneagar/stacks/mailcow-dockerized/) — the Mailcow stack

## Migrated from: *(none)*
