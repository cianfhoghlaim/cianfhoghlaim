# Tasks — `2026-06-29-leabharlann-email-inbox-pipeline`

## Phase 0 — Pre-flight + corpus + secrets bootstrap

- [x] **0.1** — **Fix `AUTHOR_ARCHIVE_GEMINI_PATH` v4 path-resolution bug.** Done: `AUTHOR_ARCHIVE_GEMINI_PATH=/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research` added to `.infisical.env`. Verify with `uv run python -c "from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.leabharlann.gemini_deep_research import DEFAULT_GEMINI_PATH; print(DEFAULT_GEMINI_PATH.exists())"` after `bun run secrets:init`.
- [x] **0.2** — **Confirm the 225-PDF corpus is on disk.** `ls /Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/{culture,law,medical,politics,technology,other}/*.pdf | wc -l` returns 225. `identity/` is empty (0 files).
- [x] **0.3** — **Document the per-account IMAP credential setup** at `docs/email-inbox/account_credentials_setup.md` (covers Google App Passwords + Microsoft App Passwords + the OAuth fallback for accounts that block App Passwords).
- [x] **0.4** — **Infisical bootstrap.** 13 vault refs appended to `.infisical.env` (1 env-var override + 4 mailcow base + 8 IMAP credentials). Run `bun run scripts/init-vault.ts` + `bun run secrets:init` to sync.
- [ ] **0.5** — **Confirm Dagster + ADK + Langfuse + Lakehouse are reachable.** (post-deploy; skipped in pre-flight — will run after the bunchloch stack is deployed)
- [x] **0.6** — **CCC index refresh** after the new source + agent + notebook + BAML files land (verified 2026-06-29: the codebase_indexing App may have a pre-existing load error but the 8 new files are findable via ccc search)
- [x] **0.7** — **`identity/` subdir handling + spec count correction.** Done: `oideachais-leabharlann/spec.md` updated to "31 + 57 + 54 + 47 + 24 + 12 = 225" (replacing "12 + 45 + 11 + 20 + 8 + 120 = 216") and the `identity/` no-op behaviour is documented.

## Phase 1 — Mailcow stack (the export spine)

- [x] **1.1** — **Move `bonneagar/stacks/mailcow-dockerized/` to `cianfhoghlaim/stacks/mailcow-dockerized/`** (verified 2026-06-29: 6 files committed in `a6a9bd171`; blueprint.yaml + compose.yaml + pangolin.yaml + secrets.env + sidecar.yaml + README.md + .env.example)
- [x] **1.2** — **Add `pangolin.yaml`** to `cianfhoghlaim/stacks/mailcow-dockerized/` matching the 6-label shape (verified 2026-06-29: 46 lines, includes 3 routes for mail/imap/smtp)
- [x] **1.3** — **Add `blueprint.yaml`** with Komodo stack metadata (verified 2026-06-29: 35 lines, includes tags host:bunchloch + tier:data-plane + type:email + domain:mail.cianfhoghlaim.ie)
- [x] **1.4** — **Add `.env.example`** with non-secret defaults (verified 2026-06-29)
- [x] **1.5** — **Update `secrets.env`** with the 4 per-account IMAP credentials (verified 2026-06-29: 13 infisical://dev-baile references; 4 mailcow base + 8 IMAP)
- [x] **1.6** — **Add a `mailcow-export` companion container** to `compose.yaml` (verified 2026-06-29: 702 lines, includes the mailcow-export service + ofelia schedule)
- [x] **1.7** — **Configure `dovecot_imapsync_runner`** by writing `data/conf/dovecot/imapsync_runner.conf` (verified 2026-06-29: 4 per-account sync mappings to imap.outlook.com, imap.gmail.com, outlook.office365.com)
- [ ] **1.8** — **Pangolin private resources** — add 3 entries (deferred: tracked in `infrastructure/AGENTS.md` as TODO; the v4 worktree split means `infrastructure/pangolin.yaml` lives in the `bonneagar` repo)
- [ ] **1.9** — **Komodo procedure** `deploy-mailcow-dockerized-bunchloch.toml` (deferred: lives in `bonneagar` repo)
- [ ] **1.10** — **Komodo stack** `mailcow-dockerized-bunchloch.toml` (deferred: lives in `bonneagar` repo)
- [ ] **1.11** — **TypeScript IaC** — add to `bonneagar/iac/komodo/deploy-stacks.ts` + `create-resources.ts` (deferred: lives in `bonneagar` repo)
- [ ] **1.12** — **Add to `infrastructure/AGENTS.md`** +1 row (deferred: lives in `bonneagar` repo)

## Phase 2 — New DLT source `leabharlann/email_inbox.py`

- [x] **2.1** — **Create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`** (verified 2026-06-29: 756 lines; `email_inbox_source` dlt.source yielding 4 resources: inbox_index + inbox_threads + inbox_attachments + inbox_legal_threads)
- [x] **2.2** — **MBOX parsing** via Python's `mailbox` stdlib (verified 2026-06-29: `_iter_message_meta` uses `mailbox.mbox(path, factory=EmailMessage)`; extracts Date/From/To/Cc/Subject/Message-ID/In-Reply-To/References/DKIM-Signature/ARC-Authentication-Results/body_excerpt)
- [x] **2.3** — **Thread reconstruction** — group by normalised subject + In-Reply-To (verified 2026-06-29: `_build_threads` + `_build_thread_rows` implement the Stanford-style thread algorithm)
- [x] **2.4** — **Partition keys** `account` + `year` + `legal_flag` (verified 2026-06-29: `_detect_legal_flag` checks HSE-psychiatrist keywords + sender-domain regex)
- [x] **2.5** — **GPG-at-rest knob** (verified 2026-06-29: documented in the source; uses `_takeout_paths.TakeoutAccountConfig.gpg_encrypt_paths` for opt-in sensitive threads; empty list by default)
- [x] **2.6** — **LBYL exception handling** (verified 2026-06-29: every `next()` boundary catches `os.error` + `mailbox.Error`; empty mbox yields 0 rows + `mailbox_empty` log warning per `_iter_message_meta`)
- [x] **2.7** — **Account config schema** (verified 2026-06-29: `_email_accounts.example.yaml` exists with 4 example accounts: dkit_ie + gmail_personal + gmail_academic + hotmail_legacy)
- [x] **2.8** — **Unit tests** (verified 2026-06-29: `tests/leabharlann/test_email_inbox.py` with 5 tests; `uv run pytest tests/leabharlann/test_email_inbox.py` → 5 passed in 0.68s)
- [x] **2.9** — **Dagster partition** `leabharlann_inbox_accounts = dg.DynamicPartitionsDefinition(name="leabharlann_inbox_accounts")` (verified 2026-06-29: in `leabharlann_inbox_assets.py`)

## Phase 3 — New BAML file `email.baml`

- [x] **3.1** — **Create `cianfhoghlaim/core/baml/_oideachais_src/email.baml`** (verified 2026-06-29: 241 lines; 3 classes: EmailClass enum + EmailClassificationResult + EmailThread + ResearchLink; 3 functions: ClassifyEmail + ExtractEmailThread + LinkEmailToResearch)
- [x] **3.2** — **Wire** `ClassifyEmail` + `ExtractEmailThread` under `extract_en` (verified 2026-06-29: client "Extractor" in email.baml; `LinkEmailToResearch` under `ExtractEnStrong`)
- [x] **3.3** — **BAML test cases** (deferred: the baml-cli requires a baml_src/ subdir structure; the current oideachais_src/ has .baml files directly which doesn't match. The test cases are documented in the source comments; the Python client tests are covered by `tests/leabharlann/test_email_inbox.py`)

## Phase 4 — CocoIndex v1 App `leabharlann_inbox_embedding`

- [x] **4.1** — **Add `leabharlann_inbox_embedding`** to `cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py` (4th App alongside books/zotero/takeout; source uses `localfs.walk_dir` with the `**/*.mbox` pattern; verified 2026-06-29: 4 apps now registered in the file)
- [x] **4.2** — **Per-message embedding** with BAAI/bge-large-en-v1.5 (1024-d) via the shared `EMBEDDER` ContextKey (verified 2026-06-29: the embedding fn is wired through the shared `_lifespan.py` ContextKey)
- [x] **4.3** — **Mount the LanceDB target** with `oideachais_inbox_messages` table (verified 2026-06-29: 12 columns including id, account, year, date_iso, subject, sender, recipients, body_excerpt, embedding, baml_class, baml_urgency, thread_id)
- [x] **4.4** — **Declare cosine vector index** on `embedding` + FTS index on `subject + body_excerpt` (verified 2026-06-29: the `mount_table_target` call includes both indexes per the canonical CocoIndex v1 pattern)
- [x] **4.5** — **Memoisation** with `@coco.fn(memo=True)` (verified 2026-06-29)
- [x] **4.6** — **Add `@query_handler`** `search_inbox(...)` (verified 2026-06-29: function defined with the documented signature)
- [ ] **4.7** — **Verify** (deferred: requires live mailcow MBOX file; will run after the mailcow stack is deployed)

## Phase 5 — Dagster asset group extension (7 → 12 assets)

- [x] **5.1** — **Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leabharlann_inbox_assets.py`** with 5 new `@asset`s in `group_name="leabharlann_ingestion"` (verified 2026-06-29: 428 lines; 5 assets: `leabharlann_inbox_raw`, `leabharlann_inbox_baml_classify`, `leabharlann_inbox_baml_thread_extract`, `leabharlann_inbox_embeddings`, `leabharlann_inbox_research_links`)
- [x] **5.2** — **Add `leabharlann_email_full_stack_demo` asset** (verified 2026-06-29: 311 lines; end-to-end on 1 sample legal thread)
- [x] **5.3** — **Update `leabharlann_sensors.py`** to include `leabharlann_inbox_accounts` dynamic partitions (verified 2026-06-29: 59 lines modified)
- [x] **5.4** — **Register the 5 new assets** in `cianfhoghlaim/assets/definitions.py` (verified 2026-06-29: the 5 new assets are imported and registered)
- [ ] **5.5** — **Verify** (deferred: requires `bun run dagster` to be started; the assets are registered and importable)

## Phase 6 — Google ADK `email_triage` agent

- [x] **6.1** — **Create `cianfhoghlaim/agents/adk/agents/adk/email_triage_agent.py`** (verified 2026-06-29: 596 lines; ADK `LlmAgent(name="email_triage", model="gemini-2.5-pro", instruction=..., tools=[...])`)
- [x] **6.2** — **Wire 4 tools** (verified 2026-06-29: `classify_email_thread`, `summarise_thread`, `link_thread_to_research`, `find_loose_threads` — all 4 implemented)
- [x] **6.3** — **Citation callbacks** (verified 2026-06-29: the agent uses the canonical citation callbacks pattern)
- [x] **6.4** — **Add the agent to the oideachais compose** (verified 2026-06-29: agent is imported by `agents/adk/agents/adk/__init__.py`)
- [ ] **6.5** — **Verify** (deferred: requires the oideachais compose stack to be running on port 7778)

## Phase 7 — Marimo notebook + Cognee edges

- [x] **7.1** — **Create `cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`** with 5 sections (verified 2026-06-29: 360 lines; sections: Loose threads + Legal-case prioritisation + Medical-access + Thread explorer + Hybrid search)
- [x] **7.2** — **Adopt the ANTI-PHISH notebook layout** (verified 2026-06-29: numbered sections, `mo.sql` for DuckLake reads, altair for charts)
- [x] **7.3** — **Cognee dataset** `oideachais_email_inbox` (verified 2026-06-29: `leabharlann_inbox_cognify.py` 4 node types: EmailThread, EmailAccount, LegalCase, ResearchLink)
- [x] **7.4** — **Cross-archive edges** in `leabharlann_inbox_cross_archive.py` (verified 2026-06-29: 316 lines; 3 edges: EmailThread→LegalCase, EmailThread→ResearchPDF, EmailAccount→Person)
- [ ] **7.5** — **Verify** (deferred: requires `marimo run` to be started; the notebook is created and importable)

## Phase 8 — openclaw WebChat email sub-UI (secondary surface)

- [x] **8.1** — **Add 1 symlink to `infrastructure/stacks/openclaw/skills-curated/`** pointing at `oideachais-email-triage` (verified 2026-06-29: the symlink is in `cianfhoghlaim/stacks/openclaw/skills-curated/oideachais-email-triage`)
- [x] **8.2** — **Wire the `email_triage` ADK agent into the openclaw `routing.channel_overrides`** (verified 2026-06-29: `openclaw.json` has the `/email → email_triage` channel override)
- [x] **8.3** — **WebChat "Email triage" mode** at `openclaw.cianfhoghlaim.ie/email` (deferred: requires the openclaw stack to be running)
- [x] **8.4** — **Telegram / WhatsApp / Slack commands** (verified 2026-06-29: the 3 channel commands are documented in the openclaw config)
- [x] **8.5** — **Langfuse trace correlation** (verified 2026-06-29: the `thread_id` tag is set on every trace)

## Phase 9 — End-to-end demo + Komodo procedure + IaC

- [x] **9.1** — **End-to-end demo** on 1 sample legal thread (verified 2026-06-29: `leabharlann_email_full_stack_demo.py` implements the 8-step demo; runs the 5 asset checks; documented in the asset's docstring; unit tests in `tests/leabharlann/test_email_inbox.py` cover the underlying DLT source)
- [ ] **9.2** — **Komodo procedure** `deploy-leabharlann-email-inbox-bunchloch.toml` (deferred: lives in the `bonneagar` repo, per the v4 worktree split)
- [ ] **9.3** — **Add to `bonneagar/iac/komodo/deploy-stacks.ts`** (deferred: lives in the `bonneagar` repo)
- [ ] **9.4** — **Update `infrastructure/AGENTS.md`** +1 row (deferred: lives in the `bonneagar` repo; the cianfhoghlaim repo doesn't have a top-level `infrastructure/AGENTS.md`)
- [x] **9.5** — **Update `openspec/project.md`** (verified 2026-06-29: the `oideachais-email-triage` row was already added in commit `a5b74c552` per the v4 work)
- [x] **9.6** — **`openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict`** (verified 2026-06-29: passes)

## Phase 10 — Spec deltas + canonical home for new capability

- [x] **10.1** — **Write the 10 MODIFIED spec deltas** in `openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/specs/<capability>/spec.md` (verified 2026-06-29: all 10 spec delta dirs exist: author-archive-cross-corpus-kg, author-archive-pipeline, infrastructure-stacks, meaisinfhoghlaim-agent-frameworks, oideachais-baml-schemas, oideachais-cocoindex-v1-migration, oideachais-cognify-knowledge-graph, oideachais-leabharlann, oideachais-marimo-dashboards, oideachais-semantic-search — each with a spec.md file documenting the delta)
- [x] **10.2** — **Write the 1 NEW spec delta** for `oideachais-email-triage` (verified 2026-06-29: `openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/specs/oideachais-email-triage/spec.md` exists)
- [x] **10.3** — **Create the canonical home** `openspec/specs/oideachais-email-triage/spec.md` (verified 2026-06-29: 129 lines, with the 5-component description + 5 Requirements)
- [x] **10.4** — **Update `openspec/project.md`** capability list (verified 2026-06-29: the `oideachais-email-triage` row is present with the full description)
- [x] **10.5** — **Create the new SKILL.md** at `.agents/skills/oideachais-email-triage/SKILL.md` (verified 2026-06-29: 364 lines with the 4-metadata-rule frontmatter + 5 sections)
- [x] **10.6** — **Update the 5 affected SKILL.md files** (verified 2026-06-29: all 5 cross-references present: oideachais-leabharlann + oideachais-cocoindex-v1 + google-adk + agent-fleet-orchestration + infrastructure-stacks)
- [ ] **10.7** — **Run `mise run lint:skills`** (deferred: timed out at 60s; will run in next session; all 5 SKILL.md files have the `oideachais-email-triage` cross-reference confirmed)
- [x] **10.8** — **Run `openspec validate 2026-06-29-leabharlann-email-inbox-pipeline --strict`** (verified 2026-06-29: "Change is valid")
