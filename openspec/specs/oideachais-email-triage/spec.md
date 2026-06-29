# Oideachais Email Triage Capability

## Purpose

`oideachais-email-triage` is a capability of the Cianfhoghlaim
platform. It composes the leabharlann DLT + BAML + CocoIndex
+ Dagster + ADK + marimo + Cognee + Mailcow + openclaw
sub-systems into a single end-to-end email-triage surface
for the user's personal + professional email.

The corresponding source code lives at:

- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`
  (the MBOX DLT source)
- `cianfhoghlaim/core/baml/_oideachais_src/email.baml` (the
  ClassifyEmail / ExtractEmailThread / LinkEmailToResearch
  BAML functions)
- `cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py`
  (the 4th v1 CocoIndex App `leabharlann_inbox_embedding`)
- `cianfhoghlaim/agents/adk/email_triage_agent.py` (the
  Google ADK `email_triage` agent on port 7778)
- `cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`
  (the marimo notebook — the primary manual surface)
- `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py`
  (the 4th leabharlann cognify dataset)
- `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py`
  (the 3 new cross-archive edge types)
- `cianfhoghlaim/stacks/mailcow-dockerized/` (the Mailcow
  stack with 4 per-account IMAP credentials)

See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

## Background

The leabharlann (library) is the user's personal + academic
archive. The `oideachais-leabharlann` capability covers the
Gemini Deep Research PDFs (225 docs across 6 subdirs) + UoG
artefacts + Zotero papers + Google Takeout. The new
`oideachais-email-triage` capability extends this with a
live email pipeline that ingests the user's actual email
mailbox and links it to the leabharlann corpus.

The 4 source email accounts are:

- DKIT.ie Microsoft 365 (via Outlook IMAP)
- Gmail personal (via Gmail IMAP)
- Gmail academic (via Gmail IMAP)
- Hotmail legacy (via Outlook IMAP)

The pipeline:

1. Mailcow (`bonneagar/stacks/mailcow-dockerized/` → moved to
   `cianfhoghlaim/stacks/mailcow-dockerized/`) IMAP-syncs all
   4 accounts via the built-in `dovecot_imapsync_runner`
   ofelia job.
2. A `mailcow-export` companion container runs `doveadm
   export` every 6 hours, writing
   `mailbox-<account>-<date>.mbox` to
   `/srv/mailcow-exports/`.
3. The DLT source `leabharlann_email_inbox` reads every MBOX
   file (Python `mailbox` stdlib), reconstructs threads via
   `In-Reply-To` + normalised subject, and yields 4
   resources (`inbox_index`, `inbox_threads`,
   `inbox_attachments`, `inbox_legal_threads`).
4. BAML `ClassifyEmail` (extract_en) categorises every
   message into 1 of 9 `EmailClass` labels.
5. BAML `ExtractEmailThread` (extract_en) summarises every
   thread.
6. BAML `LinkEmailToResearch` (extract_en_strong) links every
   legal thread to the top-3 Gemini Deep Research PDFs.
7. CocoIndex `leabharlann_inbox_embedding` (4th v1 App) embeds
   every message with BAAI/bge-large-en-v1.5 (1024-d) and
   writes to the `oideachais_inbox_messages` LanceDB table
   (cosine + FTS).
8. Cognee cognify adds 4 node types (EmailThread,
   EmailAccount, LegalCase, ResearchLink) and 3
   cross-archive edge types.
9. The Google ADK `email_triage` agent (port 7778) exposes
   4 tools (`classify_email_thread`, `summarise_thread`,
   `link_thread_to_research`, `find_loose_threads`).
10. The marimo notebook `email_inbox_triage.py` is the
    primary manual surface (5 sections).
11. The openclaw WebChat sub-UI at
    `openclaw.cianfhoghlaim.ie/email` is the secondary
    phone-friendly manual surface.

The end-to-end demo (`leabharlann_email_full_stack_demo`)
exercises 1 sample legal thread (DKIT.ie → Mailcow → MBOX →
DLT → BAML → 3 Gemini PDFs linked) on the live lakehouse
stack.

## Requirements

The full Requirements + Scenarios are in the change-side
delta file
`openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/specs/oideachais-email-triage/spec.md`.

## Cross-references

- [`oideachais-leabharlann`](../oideachais-leabharlann/spec.md) — the
  upstream leabharlann capability (6 dlt sources + 3 v1 Apps
  + 7 Dagster assets)
- [`oideachais-baml-schemas`](../oideachais-baml-schemas/spec.md) —
  the 6 existing BAML files (clients.baml, curriculum.baml,
  culture.baml, document.baml, gaois.baml, code_intel.baml)
  + the new email.baml
- [`oideachais-cocoindex-v1-migration`](../oideachais-cocoindex-v1-migration/spec.md) —
  the v1 App convention (3 existing Apps + the new
  `leabharlann_inbox_embedding`)
- [`oideachais-cognify-knowledge-graph`](../oideachais-cognify-knowledge-graph/spec.md) —
  the 5-stage cross-stage cognify + 3 leabharlann cognify
  datasets + 3 cross-archive edges + the new
  `oideachais_email_inbox` dataset
- [`oideachais-marimo-dashboards`](../oideachais-marimo-dashboards/spec.md) —
  the 11 existing Marimo notebooks + the new
  `email_inbox_triage.py`
- [`oideachais-semantic-search`](../oideachais-semantic-search/spec.md) —
  the 5 existing search helpers + the new `search_emails`
  helper
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 93 other stacks + the new `mailcow-dockerized` stack
- [`meaisinfhoghlaim-agent-frameworks`](../meaisinfhoghlaim-agent-frameworks/spec.md) —
  the 12-agent meaisínfhoghlaim fleet + the 9 existing ADK
  agents + the new `email_triage` ADK agent
- [`author-archive-pipeline`](../author-archive-pipeline/spec.md) —
  cross-references the new inbox assets
- [`author-archive-cross-corpus-kg`](../author-archive-cross-corpus-kg/spec.md) —
  the 3 existing cross-archive edges + the 3 new edges
