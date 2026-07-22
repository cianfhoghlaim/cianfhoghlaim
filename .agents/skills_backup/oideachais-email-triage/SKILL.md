---
name: cianfhoghlaim-email-triage
description: |
  This skill should be used when working on the email-triage pipeline
  that ingests the user's personal + professional email from 4 accounts
  (DKIT.ie Microsoft 365, 2 Gmail, Hotmail) into the leabharlann
  lakehouse. Covers the Mailcow IMAP-sync stack, the MBOX DLT source,
  the email.baml BAML functions (ClassifyEmail / ExtractEmailThread /
  LinkEmailToResearch), the 4th v1 CocoIndex App
  `leabharlann_inbox_embedding`, the 5 new Dagster inbox assets, the
  Google ADK `email_triage` agent (port 7778), the marimo notebook
  (primary manual surface), the openclaw WebChat sub-UI (secondary),
  the Cognee cognify dataset + 3 cross-archive edge types, and the
  `cianfhoghlaim-email-triage` openspec capability. Trigger phrases
  include 'email inbox', 'MBOX', 'Mailcow', 'email_triage', 'classify
  email', 'link thread to research', 'find loose threads', 'IMAP
  sync', 'leabharlann inbox', 'email.baml', 'email_full_stack_demo',
  'cianfhoghlaim-email-triage', 'dovecot_imapsync_runner'.
when_to_load: |
  Load when adding/modifying the MBOX DLT source, the email.baml
  schema, the CocoIndex `leabharlann_inbox_embedding` App, the
  Dagster `leabharlann_inbox_*` assets, the Google ADK
  `email_triage` agent, the marimo `email_inbox_triage.py` notebook,
  the Cognee inbox cognify + cross-archive edges, the Mailcow stack
  wiring, the openclaw email sub-UI, or the `cianfhoghlaim-email-triage`
  openspec capability.
location: .agents/skills/cianfhoghlaim-email-triage/SKILL.md
---

# Oideachais Email Triage

## Overview

The `cianfhoghlaim-email-triage` capability ingests the user's actual
email mailbox (not just the static leabharlann PDFs) and links it to
the Gemini Deep Research corpus so the user can answer questions like
"which email thread about HSE Ireland malpractice do I still owe a
reply on?".

It composes 8 sub-systems:

1. **Mailcow stack** (`cianfhoghlaim/stacks/mailcow-dockerized/`) —
   self-hosted Postfix + Dovecot + SOGo + Rspamd + ClamAV with the
   built-in `dovecot_imapsync_runner` ofelia job.
2. **MBOX DLT source**
   (`cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/leabharlann/email_inbox.py`)
   — reads MBOX files from `/srv/mailcow-exports/`, parses with
   Python's `mailbox` stdlib, reconstructs threads via `In-Reply-To`
   + normalised subject.
3. **BAML `email.baml`**
   (`cianfhoghlaim/core/baml/_cianfhoghlaim_src/email.baml`) —
   `ClassifyEmail` (9-label enum), `ExtractEmailThread`,
   `LinkEmailToResearch`.
4. **CocoIndex v1 App `leabharlann_inbox_embedding`** (4th App
   alongside books/zotero/takeout) — embeds with
   BAAI/bge-large-en-v1.5 (1024-d) into
   `cianfhoghlaim_inbox_messages` LanceDB table.
5. **Dagster assets** — 5 new in the `leabharlann_ingestion` group
   (7 → 12) + 1 full-stack demo asset
   (`leabharlann_email_full_stack_demo`).
6. **Google ADK `email_triage` agent** (port 7778) — 4 tools
   (`classify_email_thread`, `summarise_thread`,
   `link_thread_to_research`, `find_loose_threads`).
7. **Marimo notebook `email_inbox_triage.py`** — the primary
   manual-tagging + dev surface with 5 sections.
8. **Cognee cognify + 3 cross-archive edges** — `EmailThread →
   LegalCase`, `EmailThread → ResearchPDF`, `EmailAccount → Person`.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│ DKIT.ie M365    │    │ Gmail personal  │    │ Gmail academic   │
│ (app password)  │    │ (app password)  │    │ (app password)   │
└────────┬────────┘    └────────┬────────┘    └─────────┬────────┘
         │                      │                       │
         │   IMAP (993)        │                       │
         └──────────┬───────────┴───────────────────────┘
                    ▼
        ┌──────────────────────────────────┐
        │ Mailcow (cianfhoghlaim/stacks/   │
        │ mailcow-dockerized/)             │
        │  - dovecot_imapsync_runner       │
        │  - mailcow-export (6h cron)      │
        │    → /srv/mailcow-exports/*.mbox │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ leabharlann_email_inbox (DLT)    │
        │  - Python mailbox stdlib         │
        │  - thread reconstruction         │
        │  - 4 resources (index, threads,  │
        │    attachments, legal_threads)   │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ Dagster leabharlann_inbox_*      │
        │  1. inbox_raw                    │
        │  2. inbox_baml_classify          │
        │  3. inbox_baml_thread_extract    │
        │  4. inbox_embeddings             │
        │  5. inbox_research_links         │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ CocoIndex                       │
        │ leabharlann_inbox_embedding     │
        │  → cianfhoghlaim_inbox_messages    │
        │    (LanceDB, 1024-d, cosine+FTS)│
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ Cognee (4th leabharlann dataset) │
        │  - EmailThread                  │
        │  - EmailAccount                 │
        │  - LegalCase                    │
        │  - ResearchLink                 │
        │  + 3 cross-archive edges        │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ Google ADK email_triage (7778)   │
        │  - classify_email_thread        │
        │  - summarise_thread             │
        │  - link_thread_to_research      │
        │  - find_loose_threads           │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ Marimo notebook (primary UI)    │
        │ email_inbox_triage.py           │
        │  - 5 sections                   │
        │  - marimo.cianfhoghlaim.ie      │
        └──────────────┬───────────────────┘
                       ▼
        ┌──────────────────────────────────┐
        │ openclaw WebChat (secondary UI)  │
        │ openclaw.cianfhoghlaim.ie/email │
        └──────────────────────────────────┘
```

## Components

### Mailcow stack

- **Path**: `cianfhoghlaim/stacks/mailcow-dockerized/`
- **GOLD_STANDARD files** (7): `compose.yaml`, `sidecar.yaml`,
  `secrets.env`, `pangolin.yaml`, `blueprint.yaml`,
  `.env.example`, `README.md`.
- **Pangolin routes**: `mail.cianfhoghlaim.ie` (webmail/IMAPS),
  `imap.cianfhoghlaim.ie` (port 993, internal),
  `smtp.cianfhoghlaim.ie` (port 587, internal).
- **Infisical refs**: 12 vault refs (4 base + 4 accounts × 2
  credentials each).
- **`dovecot_imapsync_runner` config**:
  `data/conf/dovecot/imapsync_runner.conf` with 4 per-account
  sync mappings.
- **`mailcow-export` companion container**: 5-line service that
  runs `doveadm export` every 6 hours.

### MBOX DLT source

- **Path**: `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/leabharlann/email_inbox.py`
- **Source name**: `leabharlann_email_inbox`
- **Resources**: `inbox_index`, `inbox_threads`,
  `inbox_attachments`, `inbox_legal_threads`
- **MBOX parser**: Python `mailbox` stdlib (single-pass
  `mailbox.mbox(path)` iterator — never loads full file).
- **Thread reconstruction**: `In-Reply-To` chain + normalised
  subject (strip `Re:`, `Fwd:`, `Fwd: Re:`, `[list-tag]`).
- **Partition keys**: `account` (DynamicPartitionsDefinition),
  `year`, `legal_flag`.
- **GPG-at-rest**: opt-in for `legal/`, `medical/`, `hsc/`,
  `nhs/` prefixes.

### BAML `email.baml`

- **Path**: `cianfhoghlaim/core/baml/_cianfhoghlaim_src/email.baml`
- **3 classes**: `EmailClassificationResult`, `EmailThread`,
  `ResearchLink`.
- **3 functions**:
  - `ClassifyEmail(email_subject, email_body, sender_domain,
    recipient_domain) -> EmailClassificationResult` (uses
    `extract_en`)
  - `ExtractEmailThread(thread_messages: list<string>,
    thread_subject: string) -> EmailThread` (uses `extract_en`)
  - `LinkEmailToResearch(email_body, candidate_pdfs:
    list<{pdf_id, pdf_title, pdf_summary}>) ->
    list<ResearchLink>` (uses `extract_en_strong`)
- **9-class enum**: `legal_case`, `medical_access`,
  `academic_admin`, `personal_correspondence`,
  `institutional_correspondence`, `spam_or_marketing`,
  `newsletter`, `automated_notification`, `other`.

### CocoIndex `leabharlann_inbox_embedding`

- **Path**: 4th App in
  `cianfhoghlaim/embeddings/_cianfhoghlaim_src/leabharlann_embedding.py`
- **Source**: `localfs.walk_dir("/srv/mailcow-exports",
  recursive=True, path_matcher=...,
  included_patterns=["**/*.mbox"], live=True)`.
- **Per-message embedding**: BAAI/bge-large-en-v1.5 (1024-d) via
  the shared `EMBEDDER` ContextKey from `_lifespan.py`.
- **LanceDB target**: `cianfhoghlaim_inbox_messages` with columns
  `(id, account, year, date_iso, subject, sender, recipients,
  body_excerpt, embedding, baml_class, baml_urgency, thread_id)`.
- **Indexes**: cosine vector index on `embedding` + FTS index on
  `subject + body_excerpt` (RRF-fused in `search_inbox`).
- **`@query_handler`**: `search_inbox(query, account=None,
  year=None, baml_class=None, urgency_min=None, limit=20)`.

### Dagster assets (5 new + 1 demo)

- **Path**: `cianfhoghlaim/assets/_cianfhoghlaim_dagster_defs/assets/leabharlann_inbox_assets.py`
  + `leabharlann_email_full_stack_demo.py`
- **Assets** (in `group_name="leabharlann_ingestion"`):
  1. `leabharlann_inbox_raw` (dlt.run, partition `account`)
  2. `leabharlann_inbox_baml_classify` (BAML `ClassifyEmail`)
  3. `leabharlann_inbox_baml_thread_extract` (BAML
     `ExtractEmailThread`)
  4. `leabharlann_inbox_embeddings` (CocoIndex update)
  5. `leabharlann_inbox_research_links` (BAML
     `LinkEmailToResearch` + top-20 LanceDB neighbours)
- **Demo asset**:
  `leabharlann_email_full_stack_demo` — end-to-end on 1 sample
  legal thread.
- **Sensor**:
  `cianfhoghlaim/assets/_cianfhoghlaim_dagster_defs/sensors/leabharlann_inbox_sensors.py`
  — 60s poll on `/srv/mailcow-exports/`.

### Google ADK `email_triage` agent

- **Path**: `cianfhoghlaim/agents/adk/email_triage_agent.py`
- **Model**: `gemini-2.5-pro` (via LiteLLM)
- **Tools**:
  - `classify_email_thread(thread_id: str) ->
    EmailClassificationResult`
  - `summarise_thread(thread_id: str, max_chars: int = 500) -> str`
  - `link_thread_to_research(thread_id: str, k: int = 5) ->
    list[ResearchLink]`
  - `find_loose_threads(account: str, days_idle_min: int = 7)
    -> list[ThreadSummary]`
- **Container**: `adk_agents` on oideachais stack (port 7778).
- **Langfuse**: auto-traces via the existing `LANGFUSE_*` env
  vars on the oideachais stack.

### Marimo notebook (primary manual surface)

- **Path**:
  `cianfhoghlaim/notebooks/_cianfhoghlaim/dashboards/email_inbox_triage.py`
- **5 sections**:
  1. Loose threads sorted by urgency
  2. Legal-case prioritisation with linked Gemini PDFs
  3. Medical-access prioritisation with linked Gemini PDFs
  4. Thread explorer (`mo.ui.tree`)
  5. Hybrid search via `search_inbox`
- **Style**: numbered `1_*`, `2_*`… sections + `mo.sql` for
  DuckLake reads + altair for charts (adopted from
  `spaces/anti-phish/2_Classical_Machine_Learning_Models.ipynb`).

### Cognee cognify + 3 cross-archive edges

- **Path**:
  `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py`
  + `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py`
- **4 node types**: `EmailThread`, `EmailAccount`,
  `LegalCase`, `ResearchLink`.
- **3 edge types**:
  - `EmailThread → LegalCase` (when `baml_class ==
    "legal_case"`)
  - `EmailThread → ResearchPDF` (from
    `LinkEmailToResearch`)
  - `EmailAccount → Person` (from sender full-name
    resolution)

### openclaw WebChat sub-UI (secondary)

- **Path**: `openclaw.cianfhoghlaim.ie/email` (1 sub-UI
  mounted in the existing openclaw stack).
- **Curated skills**: 10 → 11 (1 new symlink to
  `cianfhoghlaim-email-triage`).
- **openclaw.json**: +1 `channel_overrides` entry for
  `email_triage` agent.

## Workflow

### Daily use (operator / user)

1. Receive an email on DKIT.ie M365 / Gmail / Hotmail.
2. Mailcow's `dovecot_imapsync_runner` syncs the email into a
   Mailcow mailbox within 1 minute.
3. The 6-hour `mailcow-export` cron writes a MBOX file to
   `/srv/mailcow-exports/`.
4. The 60-second Dagster sensor picks up the new MBOX file
   and materialises the 5 inbox assets.
5. BAML `ClassifyEmail` categorises the email.
6. BAML `LinkEmailToResearch` links legal threads to the
   top-3 Gemini PDFs.
7. The user opens the marimo notebook
   `email_inbox_triage.py` and sees the new email in the
   appropriate section (loose threads / legal / medical).
8. The user clicks "Summarise" or "Link to research" to
   interact with the ADK `email_triage` agent.
9. The user can also use the openclaw WebChat
   `openclaw.cianfhoghlaim.ie/email` from a phone for ad-hoc
   tagging.

### Development workflow

1. Edit any of the 8 sub-systems.
2. Run `mise run lint:skills` to validate the SKILL.md
   frontmatter.
3. Run `bun run ccc:index` to refresh the code index.
4. Run `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict` to validate the openspec
   change.
5. Run `bun run validate-stacks` to validate the Mailcow
   stack.
6. Run `baml_cli generate` if `email.baml` changed.
7. Run `dagster dev` and trigger the
   `leabharlann_email_full_stack_demo` asset to verify
   end-to-end.

## Cross-references

- [`.agents/skills/cianfhoghlaim-leabharlann/SKILL.md`](../cianfhoghlaim-leabharlann/SKILL.md) —
  the upstream leabharlann capability
- [`.agents/skills/cianfhoghlaim-baml-schemas/SKILL.md`](../cianfhoghlaim-baml-schemas/SKILL.md) —
  the 6 existing BAML files + the new `email.baml`
- [`.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md`](../cianfhoghlaim-cocoindex-v1/SKILL.md) —
  the v1 App convention + the 4 v1 Apps
- [`.agents/skills/cianfhoghlaim-cognify-knowledge-graph/SKILL.md`](../cianfhoghlaim-cognify-knowledge-graph/SKILL.md) —
  the cognify + cross-archive edges
- [`.agents/skills/cianfhoghlaim-marimo-dashboards/SKILL.md`](../cianfhoghlaim-marimo-dashboards/SKILL.md) —
  the 11 existing Marimo notebooks + the new
  `email_inbox_triage.py`
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  source pattern
- [`.agents/skills/dagster/SKILL.md`](../dagster/SKILL.md) —
  the Dagster asset pattern
- [`.agents/skills/google-adk/SKILL.md`](../google-adk/SKILL.md) —
  the Google ADK agent pattern (10 agents)
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the CocoIndex v1 App pattern
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the
  Marimo notebook pattern
- [`.agents/skills/infrastructure-stacks/SKILL.md`](../infrastructure-stacks/SKILL.md) —
  the 94-stack inventory + 6-file GOLD_STANDARD pattern
- [`.agents/skills/lancedb/SKILL.md`](../lancedb/SKILL.md) —
  the LanceDB target pattern
- [`.agents/skills/iceberg-lakekeeper/SKILL.md`](../iceberg-lakekeeper/SKILL.md) —
  the Iceberg / Lakekeeper / Garage S3 pattern (used by the
  end-to-end demo)
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the
  BAML extraction pattern
- [`.agents/skills/cognee/SKILL.md`](../cognee/SKILL.md) —
  the Cognee cognify pattern
- [`.agents/skills/secrets-management/SKILL.md`](../secrets-management/SKILL.md) —
  the Infisical + Locket + mise 3-way contract (used for the
  12 new vault refs)
- [`openspec/specs/cianfhoghlaim-email-triage/spec.md`](../../openspec/specs/cianfhoghlaim-email-triage/spec.md) —
  the canonical capability spec
- [`openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/`](../../openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/) —
  the openspec change artifacts (proposal, tasks, 11 spec
  deltas)
