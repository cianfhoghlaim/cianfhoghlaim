# `oideachais-leabharlann` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-leabharlann` capability spec governs the leabharlann
personal archive (Gemini Deep Research PDFs + UoG artefacts + Zotero
papers + Google Takeout) and the 4 dlt sources + 3 v1 CocoIndex Apps
+ 7 Dagster assets in the `leabharlann_ingestion` group.

This delta adds the email-inbox pipeline (DLT MBOX source + v1
CocoIndex App + 5 new Dagster assets + BAML email.baml) and
corrects the document-count Requirement from the stale "216 across
6 subdirs" to the on-disk "225 across 6 subdirs; identity/ is
empty".

## ADDED Requirements

### Requirement: leabharlann email_inbox DLT source

The system SHALL provide a `leabharlann_email_inbox` dlt source
that scans `/srv/mailcow-exports/*.mbox` (populated by the
Mailcow `dovecot_imapsync_runner` + the new `mailcow-export`
companion container) and yields 4 resources: `inbox_index`,
`inbox_threads`, `inbox_attachments`, `inbox_legal_threads`.

#### Scenario: MBOX parsed

- **GIVEN** a file `mailbox-dkit_ie-2026-06-29.mbox` with N
  messages
- **WHEN** the `email_inbox_source()` source runs
- **THEN** the `inbox_index` resource yields N rows with
  `account`, `year`, `date_iso`, `from`, `to`, `subject`,
  `message_id`, `in_reply_to`, `references`, `dkim_signature`,
  `body_excerpt`, `legal_flag`
- **AND** the `inbox_threads` resource yields 1 row per
  reconstructed thread (grouped by normalised subject +
  `In-Reply-To` chain)

#### Scenario: 4 account partitions

- **GIVEN** 4 accounts in `author_archive_accounts.yaml`
  (`dkit_ie`, `gmail_personal`, `gmail_academic`,
  `hotmail_legacy`)
- **WHEN** the `leabharlann_inbox_accounts`
  DynamicPartitionsDefinition polls
- **THEN** 4 partitions are created and the
  `leabharlann_inbox_raw` asset is materialisable for each

#### Scenario: Empty MBOX yields 0 rows

- **GIVEN** a 0-byte `mailbox-empty.mbox` file
- **WHEN** the `email_inbox_source()` source runs
- **THEN** the source yields 0 rows and logs a `mailbox_empty`
  warning via `structlog`
- **AND** the source does NOT raise

#### Scenario: GPG-at-rest for sensitive threads

- **GIVEN** `gpg_encrypt_paths: ["legal/", "medical/", "hsc/",
  "nhs/"]` is set in `author_archive_accounts.yaml` for the
  `dkit_ie` account
- **WHEN** a scanned email's relative path matches one of
  those prefixes
- **THEN** the email's `body_excerpt` is encrypted with the
  workstation GPG key before yielding the row
- **AND** the `gpg_fingerprint` column records the recipient
  fingerprint

### Requirement: MBOX CocoIndex v1 embedding App

The system SHALL provide a v1 CocoIndex App
`leabharlann_inbox_embedding` that embeds the leabharlann
email-inbox messages into the `oideachais_inbox_messages`
LanceDB table with BAAI/bge-large-en-v1.5 (1024-d, cosine
+ FTS).

#### Scenario: 1 mbox → N vectors

- **GIVEN** a single mbox file with 50 messages
- **WHEN** `cocoindex update leabharlann_inbox_embedding` runs
- **THEN** the App yields 50 rows in the
  `oideachais_inbox_messages` table with stable `id`s (from
  `IdGenerator`)

#### Scenario: Hybrid search returns ranked results

- **GIVEN** 1,000 vectors in `oideachais_inbox_messages`
- **WHEN** the `@query_handler` `search_inbox("HSE Ireland
  malpractice appeal")` runs
- **THEN** it returns 20 rows ranked by RRF-fused cosine +
  BM25 score
- **AND** the top result is the email whose `baml_class ==
  "legal_case"` AND whose body mentions "HSE Ireland"

#### Scenario: Memoisation skips unchanged messages

- **GIVEN** a re-run of `cocoindex update
  leabharlann_inbox_embedding` after no new messages arrived
- **WHEN** the App re-runs
- **THEN** the `@coco.fn(memo=True)` per-message embed fn is
  NOT re-evaluated for any of the existing 50 rows
- **AND** only the manifest is updated

### Requirement: Email-inbox Dagster asset group extension

The system SHALL extend the `leabharlann_ingestion` asset group
from 7 to 12 assets: +5 new (`leabharlann_inbox_raw`,
`leabharlann_inbox_baml_classify`,
`leabharlann_inbox_baml_thread_extract`,
`leabharlann_inbox_embeddings`,
`leabharlann_inbox_research_links`) + 1 new full-stack demo
asset (`leabharlann_email_full_stack_demo`).

#### Scenario: 12 assets register

- **WHEN** the Dagster code-location is loaded
- **THEN** 12 assets appear in the `leabharlann_ingestion`
  group
- **AND** the `leabharlann_inbox_raw` asset depends on no
  other inbox asset
- **AND** the `leabharlann_inbox_research_links` asset depends
  on `leabharlann_inbox_baml_classify` AND
  `leabharlann_gemini_deep_research_raw`

#### Scenario: 60-second sensor fires on new MBOX

- **GIVEN** a new `mailbox-dkit_ie-2026-06-30.mbox` lands in
  `/srv/mailcow-exports/`
- **WHEN** the `leabharlann_inbox_sensors` directory-watch
  sensor polls (every 60 seconds)
- **THEN** a `RunRequest` is emitted for the
  `leabharlann_inbox_raw` asset with the affected
  `leabharlann_inbox_accounts` partition
- **AND** the asset materialises within 90 seconds of the
  file landing

## MODIFIED Requirements

### Requirement: Leabharlann Corpus Location (v4) — count correction

The system SHALL expose the on-disk corpus at
`/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/`
with a document count of **31 + 57 + 54 + 47 + 24 + 12 = 225**
across 6 subdirs (replacing the previous v4 figure of
"12 + 45 + 11 + 20 + 8 + 120 = 216"). The `identity/` subdir
SHALL be empty on disk and the dlt source SHALL no-op
gracefully on it. The corpus location SHALL remain unchanged.

#### Scenario: 225 PDFs discovered

- **WHEN** Dagster materialises `leabharlann_gemini_deep_research_raw`
- **THEN** the dlt source discovers 225 rows (31 in `culture/`,
  57 in `law/`, 54 in `medical/`, 47 in `politics/`, 24 in
  `technology/`, 12 in `other/`)
- **AND** the `identity/` subdir is skipped with a
  `directory_not_found` warning

#### Scenario: `identity/` subdir is empty

- **WHEN** the gemini_deep_research source's PathGrammar walks
  the corpus
- **THEN** the `identity/` subdir contributes 0 rows
- **AND** the existing `culture/irish_traveller_identity_prejudice_and_travel.pdf`
  + `culture/claiming_irish_kingship_through_lineage.pdf` are
  used as substitutes for the "identity" theme in
  `oideachais-semantic-search` queries

### Requirement: `gemini_deep_research` v4 path resolution (env-var override)

The system SHALL resolve the `gemini_deep_research` corpus
path via the `AUTHOR_ARCHIVE_GEMINI_PATH` environment variable
when set (overriding the v4 default of
`parents[3] / "leabharlann" / "gemini_deep_research"`, which
points to a non-existent path
`cianfhoghlaim/pipelines/ingest/leabharlann/gemini_deep_research/`).
The dlt source SHALL walk the override path when the env var
is set and SHALL fall back to the v4 default (with a
`directory_not_found` warning) when it is not.

#### Scenario: env-var override unblocks ingestion

- **GIVEN** `AUTHOR_ARCHIVE_GEMINI_PATH=/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research`
  is set in `.env`
- **WHEN** the `gemini_deep_research_source()` source runs
- **THEN** it walks the override path and discovers 225 rows
- **AND** the source logs `gemini_path_override_used` with the
  resolved path

## REMOVED Requirements

*(None — the change only ADDS the inbox pipeline and corrects
the count.)*
