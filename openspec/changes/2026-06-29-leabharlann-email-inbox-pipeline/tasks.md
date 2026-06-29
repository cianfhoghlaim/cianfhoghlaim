# Tasks — `2026-06-29-leabharlann-email-inbox-pipeline`

## Phase 0 — Pre-flight + corpus + secrets bootstrap

- [x] **0.1** — **Fix `AUTHOR_ARCHIVE_GEMINI_PATH` v4 path-resolution bug.** Done: `AUTHOR_ARCHIVE_GEMINI_PATH=/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research` added to `.infisical.env`. Verify with `uv run python -c "from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.gemini_deep_research import DEFAULT_GEMINI_PATH; print(DEFAULT_GEMINI_PATH.exists())"` after `bun run secrets:init`.
- [x] **0.2** — **Confirm the 225-PDF corpus is on disk.** `ls /Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/{culture,law,medical,politics,technology,other}/*.pdf | wc -l` returns 225. `identity/` is empty (0 files).
- [x] **0.3** — **Document the per-account IMAP credential setup** at `docs/email-inbox/account_credentials_setup.md` (covers Google App Passwords + Microsoft App Passwords + the OAuth fallback for accounts that block App Passwords).
- [x] **0.4** — **Infisical bootstrap.** 13 vault refs appended to `.infisical.env` (1 env-var override + 4 mailcow base + 8 IMAP credentials). Run `bun run scripts/init-vault.ts` + `bun run secrets:init` to sync.
- [ ] **0.5** — **Confirm Dagster + ADK + Langfuse + Lakehouse are reachable.** (post-deploy; skipped in pre-flight)
- [ ] **0.6** — **CCC index refresh** after the new source + agent + notebook + BAML files land. (skipped — pre-existing `codebase_indexing` load error; not blocking this change)
- [x] **0.7** — **`identity/` subdir handling + spec count correction.** Done: `oideachais-leabharlann/spec.md` updated to "31 + 57 + 54 + 47 + 24 + 12 = 225" (replacing "12 + 45 + 11 + 20 + 8 + 120 = 216") and the `identity/` no-op behaviour is documented.

## Phase 1 — Mailcow stack (the export spine)

- [ ] **1.1** — **Move `bonneagar/stacks/mailcow-dockerized/` to `cianfhoghlaim/stacks/mailcow-dockerized/`** (the v4 consolidation move). Preserve all 5 existing files (compose.yaml, secrets.env, sidecar.yaml, blueprint.yaml, README.md) and add 2 new files (pangolin.yaml, .env.example) so the full 6-file + README set is in place.
- [ ] **1.2** — **Add `pangolin.yaml`** to `cianfhoghlaim/stacks/mailcow-dockerized/` matching the 6-label shape (`name`, `mode`, `full-domain`, `destination-port`, `protocol`, `roles`). 3 routes: `mail.cianfhoghlaim.ie` → port 443 (webmail/IMAPS), `imap.cianfhoghlaim.ie` → port 993 bound to `127.0.0.1` only, `smtp.cianfhoghlaim.ie` → port 587 bound to `127.0.0.1` only.
- [ ] **1.3** — **Add `blueprint.yaml`** with Komodo stack metadata (name `mailcow-dockerized-bunchloch`, tags `host:bunchloch`, `tier:data-plane`, `type:email`, `domain:mail.cianfhoghlaim.ie`, `depends_on:[lakehouse]`).
- [ ] **1.4** — **Add `.env.example`** with non-secret defaults: `MAILCOW_HOSTNAME=mail.cianfhoghlaim.ie`, `MAILCOW_TZ=Europe/Dublin`, `SKIP_OLEFY=y`, `SKIP_CLAMD=y` (we trust upstream scanners), `HTTP_REDIRECT=n`, `ACME_CONTACT=admin@cianfhoghlaim.ie`.
- [ ] **1.5** — **Update `secrets.env`** with the 4 per-account IMAP credentials as `infisical://dev-baile/mailcow/imap_credentials/<account>` references (1 row per account, containing `IMAP_USER_<ACCOUNT>` and `IMAP_PASS_<ACCOUNT>`). Keep the existing `MAILCOW_DB_PASSWORD`, `MAILCOW_PASS`, `DBROOT` etc. as-is.
- [ ] **1.6** — **Add a `mailcow-export` companion container** to `compose.yaml`: 5-line service that runs `doveadm expunge -A && doveadm -A export mailbox:/srv/mailcow-exports/mailbox-$(date +%Y-%m-%d).mbox` every 6 hours via ofelia. Mount `/srv/mailcow-exports` as a shared volume that the Dagster container also mounts (read-only) at `/srv/mailcow-exports`.
- [ ] **1.7** — **Configure `dovecot_imapsync_runner`** by writing `data/conf/dovecot/imapsync_runner.conf` with 4 per-account sync mappings: `dkit_ie → imap.outlook.com:993`, `gmail_personal → imap.gmail.com:993`, `gmail_academic → imap.gmail.com:993`, `hotmail_legacy → outlook.office365.com:993`. Each mapping references the Infisical-resolved `IMAP_USER_<ACCOUNT>` and `IMAP_PASS_<ACCOUNT>` env vars.
- [ ] **1.8** — **Pangolin private resources** — add 3 entries to `infrastructure/pangolin.yaml` (or the v4 equivalent): `mail.cianfhoghlaim.ie` (TinyAuth required, Member role), `imap.cianfhoghlaim.ie` (TinyAuth + SDP-MFA), `smtp.cianfhoghlaim.ie` (TinyAuth + SDP-MFA).
- [ ] **1.9** — **Komodo procedure** `infrastructure/komodo/procedures/deploy-mailcow-dockerized-bunchloch.toml` (5-stage: prereqs → locket volume + mailcow data dirs → compose up → pangolin routes → health check `curl https://mail.cianfhoghlaim.ie/SOGo`).
- [ ] **1.10** — **Komodo stack** `infrastructure/komodo/stacks/mailcow-dockerized-bunchloch.toml` referencing the 6-file compose set with the tags above.
- [ ] **1.11** — **TypeScript IaC** — add the mailcow-dockerized entry to `bonneagar/iac/komodo/deploy-stacks.ts` so `bun run deploy-stacks.ts` knows about the deployment. Add the 3 Pangolin resources to `bonneagar/iac/komodo/create-resources.ts`.
- [ ] **1.12** — **Add to `infrastructure/AGENTS.md`** +1 row in the Stack Inventory table for `mailcow-dockerized/`.

## Phase 2 — New DLT source `leabharlann/email_inbox.py`

- [ ] **2.1** — **Create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`** with `@dlt.source(name="leabharlann_email_inbox")` yielding 4 resources: `inbox_index`, `inbox_threads`, `inbox_attachments`, `inbox_legal_threads`.
- [ ] **2.2** — **MBOX parsing** via Python's `mailbox` stdlib (`mailbox.mbox(path)` iterator — never loads full file). Normalise headers via `email.policy.default`; expose `Date`, `From`, `To`, `Cc`, `Subject`, `Message-ID`, `In-Reply-To`, `References`, `DKIM-Signature`, `ARC-Authentication-Results`, `body_excerpt` (first 2000 chars).
- [ ] **2.3** — **Thread reconstruction** — group by normalised subject (strip `Re:`, `Fwd:`, `Fwd: Re:`, `[list-tag]`, `(External)`) AND by `In-Reply-To` chain. Use the `python-email-threading` lib (Stanford `mod_mailbox` style) or write a 30-line replacement.
- [ ] **2.4** — **Partition keys**: `account` (DynamicPartitions from `author_archive_accounts.yaml`), `year` (4-digit from `Date`), `legal_flag` (boolean from first 500-char keyword + sender-domain regex).
- [ ] **2.5** — **GPG-at-rest knob** — reuse `_takeout_paths.TakeoutAccountConfig.gpg_encrypt_paths` for sensitive threads (default: opt-in only, prefixes `legal/`, `medical/`, `hsc/`, `nhs/`). Empty list by default.
- [ ] **2.6** — **LBYL exception handling** per `dignified-python` skill — `os.error` + `mailbox.Error` caught at every `next()` boundary; never crash the source. Empty mbox → 0 rows + `mailbox_empty` log warning.
- [ ] **2.7** — **Account config schema** — create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/_email_accounts.example.yaml` with 4 example accounts (dkit_ie, gmail_personal, gmail_academic, hotmail_legacy) and the per-account `gpg_encrypt_paths` knob.
- [ ] **2.8** — **Unit tests** — `tests/leabharlann/test_email_inbox.py` with 5 tests: (a) mbox parsed, (b) thread reconstructed from `In-Reply-To`, (c) thread reconstructed from normalised subject, (d) `legal_flag` correctly set, (e) empty mbox yields 0 rows.
- [ ] **2.9** — **Dagster partition** — add `leabharlann_inbox_accounts = dg.DynamicPartitionsDefinition(name="leabharlann_inbox_accounts")` to `leabharlann_inbox_assets.py`.

## Phase 3 — New BAML file `email.baml`

- [ ] **3.1** — **Create `cianfhoghlaim/core/baml/_oideachais_src/email.baml`** with 3 classes + 3 functions:
  - `EmailClass` enum: `["legal_case", "medical_access", "academic_admin", "personal_correspondence", "institutional_correspondence", "spam_or_marketing", "newsletter", "automated_notification", "other"]`
  - `EmailClassificationResult` (class_label, confidence, urgency_score 0-1, summary_5_words, suggested_action) + `ClassifyEmail(email_subject, email_body, sender_domain, recipient_domain) -> EmailClassificationResult`
  - `EmailThread` (participants, topic_summary, action_items, decision_points, dates_mentioned, key_quotes) + `ExtractEmailThread(thread_messages: list<string>, thread_subject: string) -> EmailThread`
  - `ResearchLink` (linked_pdf_id, link_reason, link_confidence, snippet) + `LinkEmailToResearch(email_body, candidate_pdfs: list<{pdf_id, pdf_title, pdf_summary}>) -> list<ResearchLink>`
- [ ] **3.2** — **Wire** `ClassifyEmail` + `ExtractEmailThread` under the `extract_en` client alias; `LinkEmailToResearch` under `extract_en_strong`. Run `baml_cli generate`. Verify the Python client has `b.ClassifyEmail`, `b.ExtractEmailThread`, `b.LinkEmailToResearch`.
- [ ] **3.3** — **BAML test cases** in `email.baml` test block: 4 example threads (1 legal HSE, 1 medical CPTSD, 1 academic QUB admin, 1 spam). `baml_cli test email.baml` should pass all 4.

## Phase 4 — CocoIndex v1 App `leabharlann_inbox_embedding`

- [ ] **4.1** — **Add `leabharlann_inbox_embedding`** to `cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py` (4th App alongside books/zotero/takeout). Source: `localfs.walk_dir("/srv/mailcow-exports", recursive=True, path_matcher=PatternFilePathMatcher(included_patterns=["**/*.mbox"], excluded_patterns=["**/.*"]), live=True)`.
- [ ] **4.2** — **Per-message embedding** — for each mbox file, open with `mailbox.mbox(path)`, yield one chunk per message (`from + subject + first 2000 chars of body`). Embed with BAAI/bge-large-en-v1.5 (1024-d) via the shared `EMBEDDER` ContextKey.
- [ ] **4.3** — **Mount the LanceDB target** with new table `oideachais_inbox_messages` + columns `(id, account, year, date_iso, subject, sender, recipients, body_excerpt, embedding, baml_class, baml_urgency, thread_id)`. Primary key: `id` from `IdGenerator()`.
- [ ] **4.4** — **Declare a cosine vector index** on `embedding` AND a `declare_fts_index` on `subject + body_excerpt` for hybrid search.
- [ ] **4.5** — **Memoisation** — `@coco.fn(memo=True)` on the per-message embed fn so re-runs are O(new messages).
- [ ] **4.6** — **Add `@query_handler`** named `search_inbox(query, account=None, year=None, baml_class=None, urgency_min=None, limit=20)` that returns ranked (cosine + BM25 fused via RRF) rows.
- [ ] **4.7** — **Verify** — `cocoindex update leabharlann_inbox_embedding` runs successfully against the live mailbox MBOX file; the table `oideachais_inbox_messages` is visible in the LanceDB viewer at `http://localhost:8081`.

## Phase 5 — Dagster asset group extension (7 → 12 assets)

- [ ] **5.1** — **Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leabharlann_inbox_assets.py`** with 5 new `@asset`s in `group_name="leabharlann_ingestion"`:
  - `leabharlann_inbox_raw` (dlt.run, partition `account`)
  - `leabharlann_inbox_baml_classify` (depends on `leabharlann_inbox_raw`; invokes `b.ClassifyEmail` per row)
  - `leabharlann_inbox_baml_thread_extract` (depends on `leabharlann_inbox_raw`; calls `b.ExtractEmailThread` per thread)
  - `leabharlann_inbox_embeddings` (depends on `leabharlann_inbox_baml_classify`; runs `cocoindex update leabharlann_inbox_embedding` via subprocess)
  - `leabharlann_inbox_research_links` (depends on `leabharlann_inbox_baml_classify` AND `leabharlann_gemini_deep_research_raw`; calls `b.LinkEmailToResearch` with the top-20 candidate PDFs from LanceDB vector search)
- [ ] **5.2** — **Add `leabharlann_email_full_stack_demo` asset** — end-to-end on 1 sample legal thread: dlt → BAML classify → thread extract → 3 PDF link candidates from `gemini_deep_research/law/*.pdf` → CocoIndex update → marimo. 5 asset checks pass (raw OK, classify OK, thread OK, link OK, embedding OK).
- [ ] **5.3** — **Update `leabharlann_sensors.py`** to include `leabharlann_inbox_accounts` dynamic partitions. The sensor polls every 60s and emits `RunRequest`s for the affected partitions.
- [ ] **5.4** — **Register the 5 new assets** in `cianfhoghlaim/assets/definitions.py` (the `get_definitions()` function that loads all asset groups into the Dagster code-location).
- [ ] **5.5** — **Verify** — `bun run dagster` and check that 12 assets appear in the `leabharlann_ingestion` group in the Dagster UI.

## Phase 6 — Google ADK `email_triage` agent

- [ ] **6.1** — **Create `cianfhoghlaim/agents/adk/email_triage_agent.py`** alongside the 9 existing agents. ADK class `LlmAgent(name="email_triage", model="gemini-2.5-pro", instruction=..., tools=[...])`.
- [ ] **6.2** — **Wire 4 tools** (all async, all read-only against DuckLake + Lance namespace):
  - `classify_email_thread(thread_id: str) -> EmailClassificationResult` (calls BAML `ClassifyEmail` via the BAML client)
  - `summarise_thread(thread_id: str, max_chars: int = 500) -> str` (calls BAML `ExtractEmailThread`)
  - `link_thread_to_research(thread_id: str, k: int = 5) -> list[ResearchLink]` (calls BAML `LinkEmailToResearch` against the top-k LanceDB neighbours)
  - `find_loose_threads(account: str, days_idle_min: int = 7) -> list[ThreadSummary]` (queries DuckLake for threads where the user has not replied in ≥ N days, sorted by urgency)
- [ ] **6.3** — **Citation callbacks** — reuse `agents/adk/callbacks/citation_callbacks.py` to inject LanceDB vector-search citations into every tool response.
- [ ] **6.4** — **Add the agent to the oideachais compose** — `compose.yaml` already has `adk_agents` on port 7778; just add `email_triage_agent` to its startup list (the agent file gets imported by `agents/adk/__init__.py`).
- [ ] **6.5** — **Verify** — `curl http://localhost:7778/agents/email_triage/health` returns 200; `curl -X POST http://localhost:7778/agents/email_triage/invocations -d '{"message": "summarise thread dkit_ie/thread-123"}'` returns a summary.

## Phase 7 — Marimo notebook + Cognee edges

- [ ] **7.1** — **Create `cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`** — marimo notebook with 5 sections:
  - **Section 1: Loose threads** — `find_loose_threads(account, days_idle_min=7)` → table sorted by urgency, with "Open thread" button that calls ADK `/agents/email_triage` to summarise
  - **Section 2: Legal-case prioritisation** — filter `baml_class == "legal_case"` → table with linked `gemini_deep_research` PDFs in a 2nd column. Click a row → ADK `link_thread_to_research`
  - **Section 3: Medical-access threads** — same shape, filtered to `baml_class == "medical_access"`, links to `gemini_deep_research/medical/*.pdf`
  - **Section 4: Thread explorer** — pick an account, a date range, see thread trees (`mo.ui.tree`)
  - **Section 5: Hybrid search** — `search_inbox(query)` with RRF-fused cosine + BM25 against the LanceDB table
- [ ] **7.2** — **Adopt the ANTI-PHISH notebook layout** as the marimo style template (numbered `1_*`, `2_*`… sections; `mo.sql` for DuckLake reads; altair for charts).
- [ ] **7.3** — **Cognee dataset** `oideachais_email_inbox` — adds 4 node types: `EmailThread`, `EmailAccount`, `LegalCase`, `ResearchLink`. Create `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py` mirroring the existing leabharlann cognify module.
- [ ] **7.4** — **Cross-archive edges** in `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py`:
  - `EmailThread → LegalCase` (when `baml_class == "legal_case"`)
  - `EmailThread → ResearchPDF` (from `LinkEmailToResearch` results)
  - `EmailAccount → Person` (from sender full-name resolution)
- [ ] **7.5** — **Verify** — `marimo run email_inbox_triage.py` launches at `http://localhost:2718` and renders the 5 sections against the live LanceDB + DuckLake data.

## Phase 8 — openclaw WebChat email sub-UI (secondary surface)

- [ ] **8.1** — **Add 1 symlink to `infrastructure/stacks/openclaw/skills-curated/`** pointing at the new `oideachais-email-triage` skill (curated subset grows from 10 → 11).
- [ ] **8.2** — **Wire the `email_triage` ADK agent into the openclaw `routing.channel_overrides`** section of `config/openclaw.json`. The gateway's `default_agent: "celtic-tutor"` stays; `email_triage` is invoked by name (e.g. `/agent email_triage` or `agent:email_triage` prefix).
- [ ] **8.3** — **WebChat "Email triage" mode** — a 2nd WebChat sub-UI on `openclaw.cianfhoghlaim.ie/email` that loads the next loose thread and asks the user to confirm/override the BAML classification. The confirm/override writes back to a new `leabharlann_inbox_user_overrides` DuckLake table.
- [ ] **8.4** — **Telegram / WhatsApp / Slack commands** — `/triage <thread_id>` posts the thread summary; reply with `class:<label>` to override the BAML class; reply with `link:<pdf_id>` to override the research link.
- [ ] **8.5** — **Langfuse trace correlation** — every `classify_email_thread` and `link_thread_to_research` call gets a `thread_id` tag; the openclaw chat session is joined to the same trace so the user can see the cost + latency of every triage action.

## Phase 9 — End-to-end demo + Komodo procedure + IaC

- [ ] **9.1** — **End-to-end demo** on 1 sample legal thread (from `leabharlann_inbox_accounts["dkit_ie"]` filtered to `baml_class == "legal_case"`, linked to 3 PDFs from `gemini_deep_research/law/`):
  1. Mailcow IMAP syncs 1 sample mailbox → MBOX file in `/srv/mailcow-exports/`
  2. `leabharlann_inbox_raw` materialises 100 rows
  3. `leabharlann_inbox_baml_classify` classifies → ~5 legal threads
  4. `leabharlann_inbox_research_links` calls `LinkEmailToResearch` → 3 PDFs per thread
  5. `leabharlann_inbox_embeddings` runs CocoIndex → 100 vectors in LanceDB
  6. ADK `email_triage` agent called via WebChat → summarises the thread + returns research links
  7. marimo notebook renders the prioritised inbox
  8. 5 asset checks pass (raw OK, classify OK, thread OK, link OK, embedding OK)
- [ ] **9.2** — **Komodo procedure** `deploy-leabharlann-email-inbox-bunchloch.toml` (6-stage: prereqs → mailcow stack → lakehouse → oideachais ADK agent + Dagster assets → pangolin routes → health checks).
- [ ] **9.3** — **Add to `bonneagar/iac/komodo/deploy-stacks.ts`** so the TypeScript IaC knows about the new inbox pipeline. Add the new openclaw curated skill symlink to the openclaw IaC entry.
- [ ] **9.4** — **Update `infrastructure/AGENTS.md`** +1 row in the Stack Inventory table for `mailcow-dockerized/`. Update `bonneagar/AGENTS.md` cross-reference too.
- [ ] **9.5** — **Update `openspec/project.md`** — add a new capability row under "Cianfhoghlaim core" for `oideachais-email-triage`.
- [ ] **9.6** — **`stack-doctor` 4-gate check** + `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict` must pass.

## Phase 10 — Spec deltas + canonical home for new capability

- [ ] **10.1** — **Write the 10 MODIFIED spec deltas** in `openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/specs/<capability>/spec.md` for: `oideachais-leabharlann`, `oideachais-baml-schemas`, `oideachais-cocoindex-v1-migration`, `oideachais-cognify-knowledge-graph`, `oideachais-marimo-dashboards`, `oideachais-semantic-search`, `infrastructure-stacks`, `meaisinfhoghlaim-agent-frameworks`, `author-archive-pipeline`, `author-archive-cross-corpus-kg`.
- [ ] **10.2** — **Write the 1 NEW spec delta** for `oideachais-email-triage` (in the change dir).
- [ ] **10.3** — **Create the canonical home** `openspec/specs/oideachais-email-triage/spec.md` for the new capability.
- [ ] **10.4** — **Update `openspec/project.md`** capability list with the new `oideachais-email-triage` row.
- [ ] **10.5** — **Create the new SKILL.md** at `.agents/skills/oideachais-email-triage/SKILL.md` with the 4-metadata-rule frontmatter (name, description, when-to-load, location) and 5 sections (Overview, Architecture, Components, Workflow, Cross-references).
- [ ] **10.6** — **Update the 5 affected SKILL.md files** in `.agents/skills/` (`oideachais-leabharlann`, `oideachais-cocoindex-v1`, `google-adk`, `agent-fleet-orchestration`, `infrastructure-stacks`) with the new cross-references.
- [ ] **10.7** — **Run `mise run lint:skills`** — the new + 5 updated SKILL.md files all pass the 4 metadata rules. Total skill count: 124 (was 123).
- [ ] **10.8** — **Run `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict`** — every `### Requirement:` has at least one `#### Scenario:` with WHEN/THEN/AND structure. Iterate until validation passes.
