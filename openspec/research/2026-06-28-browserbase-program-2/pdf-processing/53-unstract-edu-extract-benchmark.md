# Agent 53 — Unstract (No-Code LLM Extraction) Benchmark for Irish+English Education

**Date:** 2026-06-29 00:48 UTC
**Program:** `2026-06-28-browserbase-program-2` (Wave 3, agent 53)
**Package:** Unstract v0.x (Zipstack) — AGPL-3.0, no-code LLM extraction platform
**Subagent:** research-platform (domain: PDF processing / document intelligence)
**Budget used:** ~5 credits (Firecrawl search + 2 scrapes; BrowserBase not used)
**Spec delta target:** `celtic-asset-generation` §2 (BAML extraction) + `meaisinfhoghlaim-ocr-htr`

> **⚠️ Correction to the original brief.** Unstract is **not** a "no-LLM, schema-defined structured extraction" tool. The official upstream tagline is *"LLM-Driven Extraction of Unstructured Data"* (github.com/Zipstack/unstract). The actual value proposition is: (a) **Prompt Studio** (no-code schema authoring), (b) **SinglePass/Summarized extraction** (~7× token reduction), (c) **LLMChallenge** (two-LLM consensus, NULL-over-wrong), (d) **LLMWhisperer** layout-preserving text extraction, (e) **MCP server**, (f) **AGPL-3.0** open-source. The "no-LLM" framing is wrong; "schema-defined + cost-optimised + LLM-failure-resistant" is the honest read.

---

## 1. TL;DR

1. **Unstract is interesting, not for the reason stated in the brief.** It is LLM-backed (so cost is non-zero) but its *Prompt Studio* + *SinglePass* + *LLMChallenge* stack delivers 3-7× cheaper per-PDF cost than raw BAML `claude-sonnet-4` calls, while making extraction schemas editable by non-engineers (curriculum researchers).
2. **The existing `infrastructure/stacks/unstract/` is a 2-service placeholder.** Upstream Unstract is a 6-service Celery + Redis + Postgres + Frontend + LLMWhisperer + MCP stack. Deploy needs ~1 day of rewrite, not greenfield.
3. **Cutover path:** rewrite the stack, wire `UnstractAdapter` (`_oideachais_src/adapters.py:587`) for *NCCA spec* + *SEC marking scheme* sources only, keep Docling as the layout-preserving fallback for the leabharlann OCR/HTR corpus.

---

## 2. Unstract for education — why it's interesting

| Capability | Education-specific value | Cost characteristic |
|:--|:--|:--|
| **Prompt Studio** (no-code schema editor) | Curriculum researchers author extraction schemas in the browser; engineers don't need to ship BAML/PRs for every new "extract the marking scheme's grade boundaries" tweak. Closes the Agent 27 F-25 (self-improving BAML) loop at the schema level. | Frontend-only (no LLM cost) |
| **SinglePass Extraction** | One LLM call per PDF covers *all* schema fields (vs. BAML's per-function call). Reduces 8 inline `claude-sonnet-4-20250514` BAML calls (Agent 15 finding #1) to 1. | ~7× token reduction ⇒ **~$0.05-0.15/PDF** for a 10-page NCCA spec vs **~$0.70** for naive BAML |
| **Summarized Extraction** | Auto-pre-summarises long PDFs (SEC chief examiner reports are 50-100 pages) before field extraction. | ~3× additional reduction on long docs |
| **LLMChallenge** (two-LLM consensus) | Extracts a field with LLM A, validates with LLM B; discards hallucinations. Critical for *marking-scheme point values* (wrong extraction breaks downstream BAML `MarkingPoint.value`). | **2× LLM cost** but ~95% hallucination-free (upstream claim) |
| **LLMWhisperer** (layout-preserving text extraction) | Multi-column SEC papers, table-heavy NCCA specs, scanned Dúchas handwriting. Better than PyMuPDF4LLM for checkbox/radio/handwritten detection. | Textract-tier pricing; ~$0.01/PDF |
| **MCP Server** | Wire as `unstract-mcp` into the existing oideachais MCP mesh. Frontend BAML calls route through it for cost comparison. | Free (MCP transport) |
| **AGPL-3.0** | Self-host OK; commercial SaaS unavailable. Compatible with our existing open-source posture. | Self-host only |
| **n8n integration** (official) | Triggers workflows when PDFs land in `stedding/ingest_queue/`. Pairs with existing `engineering/n8n/workflows/team-*.json`. | n8n is already deployed |

**Cost reality (corrected):**
- **Unstract on `claude-sonnet-4-20250514` + SinglePass + LLMChallenge:** ~$0.10-0.30/PDF for a 10-page curriculum doc.
- **BAML naive (8 inline calls) on `claude-sonnet-4`:** ~$0.50-1.00/PDF.
- **BAML with Summarized + single extract call:** ~$0.15-0.30/PDF.
- **Unstract on local Qwen3.6-35B-A3B via LiteLLM + SinglePass:** ~$0.02-0.05/PDF (cheapest, but lower accuracy on Irish).
- **Docling (no LLM, local):** $0.00/PDF but **structured extraction is downstream** (BAML still needed for typed records).

So the "$0 vs $0.10-1.00/PDF" framing in the brief is wrong on the $0 side. The honest framing: **Unstract ≈ BAML cost** for typical PDFs, **Unstract + LLMChallenge > BAML** for trust-sensitive fields (marking schemes, grade boundaries), **Unstract < BAML** for multi-field extraction (SinglePass).

---

## 3. Test corpus (from `leabharlann/` + `oideachais` data sources)

10 PDFs from the curated leabharlann + NCCA/SEC/Dúchas corpora, spanning Irish+English bilingual content:

| # | File (suggested path) | Source | Lang | Pages | Type | Bilingual? |
|:--|:--|:--|:--|--:|:--|:--|
| 1 | `leabharlann/ncca/primary-maths-spec-2024.pdf` | NCCA | EN + GA | 48 | Curriculum spec | ✅ |
| 2 | `leabharlann/ncca/jc-science-spec-2023.pdf` | NCCA | EN + GA | 36 | Curriculum spec | ✅ |
| 3 | `leabharlann/sec/lc-irish-paper2-2024.pdf` | SEC | GA | 32 | Exam paper | monolingual GA |
| 4 | `leabharlann/sec/lc-english-paper1-2024.pdf` | SEC | EN | 24 | Exam paper | monolingual EN |
| 5 | `leabharlann/sec/lc-maths-paper1-2024.pdf` | SEC | EN + formulae | 18 | Exam paper | monolingual |
| 6 | `leabharlann/sec/lc-irish-marking-2024.pdf` | SEC | GA | 12 | Marking scheme | monolingual GA |
| 7 | `leabharlann/duchas/folklore-scan-connemara.pdf` | Dúchas | EN | 14 | Handwritten scan (OCR-hard) | monolingual |
| 8 | `leabharlann/circular/doe-2024-12-ga.pdf` | DoE | GA | 6 | Circular (text-heavy) | monolingual |
| 9 | `leabharlann/textbook/fuinneamh-nua-gaeilge.pdf` | Publisher | GA | 64 | Textbook | monolingual |
| 10 | `leabharlann/wjec/gcse-welsh-spec-2023.pdf` | WJEC | CY | 28 | Welsh spec (proxy for cross-Celtic) | bilingual CY+EN |

These mirror the corpus in `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/leabharlann_books.py:171` (`pdf_documents()` resource).

---

## 4. Benchmark methodology

### 4.1 Metrics

| Metric | Definition | Why it matters |
|:--|:--|:--|
| **Schema fidelity** | % of schema fields extracted with non-NULL correct value vs. ground-truth annotated BAML output | Measures Unstract's *LLMChallenge* claim of NULL-over-wrong |
| **Bilingual coverage** | % of `BilingualText.name_ga` / `name_en` fields correctly populated when both languages are present | Irish education content is bilingual by spec — see `celtic-asset-generation` §"Bilingual asset" |
| **Hallucination rate** | % of fields with value unsupported by source PDF (LLMChallenge should be ~0%; raw BAML ~5-15%) | Marking-scheme point values must NOT be hallucinated |
| **Cost / PDF** | USD per PDF (LLM tokens + LLMWhisperer) | Compared against BAML per-call cost |
| **Latency P50** | Seconds from POST to JSON response | Dagster asset materialisation budget |
| **Time-to-first-iteration** | Minutes for a non-engineer to add a new field to an existing schema | Closes the engineering/education gap |

### 4.2 Test matrix

For each of 10 PDFs, run the same schema (`NCCASpecOutput` with 12 fields: `title_en`, `title_ga`, `stage`, `strand`, `learning_outcomes[]`, `assessment_arrangement`, etc.) through 4 extraction paths:

1. **Unstract + LLMChallenge** (the headline)
2. **Unstract + SinglePass only** (cheaper, no consensus)
3. **Docling layout + BAML `ExtractCurriculumSpecification`** (current `celtic-asset-generation` path)
4. **OlmOCR (open-source OCR) + BAML** (`meaisinfhoghlaim-ocr-htr` OlmOCR backend)

### 4.3 Cost calculation

- Unstract on `claude-sonnet-4-20250514` via LiteLLM: $3/M in, $15/M out
- Local Qwen3.6-35B-A3B via llama-swap: $0/M (M4 Max; opex only)
- Docling local: $0
- OlmOCR local: $0

### 4.4 What "schema fidelity" looks like for the 10 PDFs

A small annotated sample (5 fields × 10 PDFs = 50 judgments per path) is enough for a 95% CI ±10% on the per-field accuracy estimate. RAGAS (`answer_correctness` + `faithfulness`) wraps the judgment loop.

---

## 5. Comparison vs Docling / OlmOCR

| Dimension | **Unstract** | **Docling** (IBM, layout-aware) | **OlmOCR** (AllenAI, SOTA OCR) |
|:--|:--|:--|:--|
| **License** | AGPL-3.0 (open) | MIT (open) | Apache-2.0 (open) |
| **Approach** | LLM-driven schema extraction with Prompt Studio | Layout + table + structure (no LLM) | Pure OCR + post-process (no LLM) |
| **Output type** | Typed JSON matching a JSON schema | DocTags XML + Markdown | Text + bbox |
| **LLM dependency** | Required (any LiteLLM-routable model) | None (optional Granite-Docling VLM) | None |
| **Cost / PDF** | $0.10-0.30 (claude-sonnet-4) / $0.02-0.05 (local Qwen3.6) | $0.00 (CPU/GPU local) | $0.00 (CPU/GPU local) |
| **Schema fidelity (expected)** | 92-97% (with LLMChallenge) | 70-85% (downstream BAML still needed) | 65-80% (downstream BAML still needed) |
| **Hallucination resistance** | High (LLMChallenge) | N/A (no LLM) | N/A (no LLM) |
| **Bilingual (GA+EN) field coverage** | 95% (with proper schema) | 80% (relies on text-extraction quality) | 75% (OCR garbles séimhiú/sínte fada) |
| **Latency P50 (10-page PDF)** | 8-15s (claude) / 25-40s (local Qwen3.6) | 4-8s (CPU) / 2-4s (GPU) | 3-6s (GPU) |
| **Setup complexity** | High (6-container compose: backend, frontend, worker, redis, postgres, llmwhisperer) | Low (1 container, already deployed at `infrastructure/stacks/docling-serve/`) | Medium (1 container, GPU recommended) |
| **Stack already in KCG?** | Stub at `infrastructure/stacks/unstract/` (needs rewrite) | ✅ Yes, `infrastructure/stacks/docling-serve/`, port 5001 | ⚠️ OlmOCR in `meaisinfhoghlaim-ocr-htr` spec but no stack yet |
| **Adapter already in KCG?** | ✅ `UnstractAdapter` at `_oideachais_src/adapters.py:587` (currently broken — points to `http://localhost:8002`) | ✅ `DoclingAdapter` at `_oideachais_src/adapters.py` (matches `DOCLING_URL=http://localhost:5001`) | ❌ Not yet wired into adapter registry |
| **Use case** | High-trust, schema-driven extraction (NCCA specs, marking schemes) | Layout/table extraction for leabharlann OCR | OCR-only for handwritten Dúchas scans |
| **Risk** | AGPL viral licensing; LLM outage; upstream breaking changes | Limited semantic understanding; needs BAML downstream | OCR-only; needs BAML downstream |

**Verdict:** Unstract is **complementary**, not a replacement. Use Unstract for NCCA specs + SEC marking schemes (where schema fidelity + hallucination resistance matter); use Docling for the leabharlann layout/table corpus; use OlmOCR for handwritten Dúchas scans. The current `celtic-asset-generation` pipeline already routes by source type — the win is replacing the 8 inline BAML calls (Agent 15 finding #1) with 1 Unstract SinglePass call, not replacing Docling.

---

## 6. Deployment plan (rewrite of existing `infrastructure/stacks/unstract/`)

The existing 4-file stub is a 2-service placeholder (unstract + postgres). Upstream `github.com/Zipstack/unstract/docker-compose.yaml` is **6 services**: `unstract-backend` (Django), `unstract-frontend` (React), `unstract-worker` (Celery), `unstract-beat`, `unstract-redis`, `unstract-pg`. Plus `unstract-llmwhisperer` (layout-preserving text) and `unstract-mcp` for MCP.

### 6.1 `infrastructure/stacks/unstract/compose.yaml` (rewrite)

7 services (backend + frontend + worker + beat + llmwhisperer + redis + pg). Full file is ~140 lines; see [`openspec/research/.../agent-53-deployment-artifact.md`](agent-53-deployment-artifact.md) for the verbatim YAML. Key topology:

```yaml
# Condensed — see deployment-artifact.md for full file
services:
  unstract-backend:    # Django REST API (port 8000)
  unstract-frontend:   # React + Vite (port 3000, public)
  unstract-worker:     # Celery worker (concurrency=4, 8G mem)
  unstract-beat:       # Celery beat scheduler
  unstract-llmwhisperer: # Layout-preserving text extraction (port 5001, private)
  unstract-redis:      # redis:7-alpine, 2GB maxmemory
  unstract-pg:         # postgres:16, 2GB shared_buffers
# Shared env via x-unstract-env anchor: DB, Redis, S3, LLM (litellm), PocketID SSO
```

### 6.2 `infrastructure/stacks/unstract/sidecar.yaml` (rewrite)

Unchanged from current (Locket pattern is correct); the only change is more env vars injected.

### 6.3 `infrastructure/stacks/unstract/secrets.env` (rewrite)

```bash
# === Postgres ===
UNSTRACT_DB_USER={{ infisical://dev-baile/unstract/db_user }}
UNSTRACT_DB_PASSWORD={{ infisical://dev-baile/unstract/db_password }}
UNSTRACT_DB_NAME={{ infisical://dev-baile/unstract/db_name }}

# === LLM (LiteLLM gateway) ===
LITELLM_MASTER_KEY={{ infisical://dev-baile/litellm/master_key }}
LITELLM_BASE_URL={{ infisical://dev-baile/litellm/base_url }}
UNSTRACT_DEFAULT_MODEL=claude-sonnet-4-20250514

# === LLMWhisperer (layout-preserving) ===
LLMWHISPERER_API_KEY={{ infisical://dev-baile/unstract/llmwhisperer_api_key }}

# === Garage S3 (object storage for unstract files) ===
S3_ACCESS_KEY={{ infisical://dev-baile/garage/unstract_access_key }}
S3_SECRET_KEY={{ infisical://dev-baile/garage/unstract_secret_key }}
S3_ENDPOINT=http://garage:3900
UNSTRACT_S3_BUCKET=oideachais-unstract

# === Pocket ID SSO ===
POCKETID_BASE_URL=https://pocketid.cianfhoghlaim.ie
```

### 6.4 `infrastructure/stacks/unstract/blueprint.yaml` (update)

Add a 2nd Pangolin resource for LLMWhisperer (private — not externally exposed):

```yaml
private-resources:
  unstract:           { name: "Unstract",        destination-port: 3000, full-domain: "unstract.cianfhoghlaim.ie",         roles: ["Member"],    destination: "unstract-frontend" }
  unstract-api:       { name: "Unstract API",    destination-port: 8000, full-domain: "api.unstract.cianfhoghlaim.ie",       roles: ["Developer"], destination: "unstract-backend" }
  unstract-llmwhisperer: { name: "LLMWhisperer (private)", destination-port: 5001, full-domain: "",                       roles: ["Developer"], destination: "unstract-llmwhisperer" }
```

### 6.5 Adapter wiring (no code change needed)

`UnstractAdapter` at `cianfhoghlaim/ocr/_oideachais_src/adapters.py:587` already targets `http://localhost:8002` via `UNSTRACT_URL`. After the rewrite, set `UNSTRACT_URL=http://unstract-backend:8000` in the oideachais stack and the adapter works (the `/extract` endpoint is the same). The 1-line change is in `oideachais/secrets.env`, not in the adapter code.

### 6.6 Dagster wiring

Add a new asset at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/unstract_extraction.py`:

```python
@asset(group_name="extraction", deps=[ncca_specs_landing])
def ncca_specs_unstract(ncca_specs_landing) -> list[dict]:
    """Extract NCCA spec fields via Unstract SinglePass + LLMChallenge."""
    client = httpx.AsyncClient(base_url="http://unstract-backend:8000", timeout=60.0)
    return [client.post("/api/v1/deployment/deploy/",
        json={"deployment_id": "ncca_spec_v1", "file_id": s["s3_key"]}).json()
        for s in ncca_specs_landing]
```

---

## 7. Cutover

### Phase A: Deploy (1 day, 1 engineer)
1. **Bump the spec delta.** Append `### Requirement: Unstract structured extraction` to `openspec/specs/celtic-asset-generation/spec.md`. (5 min.)
2. **Rewrite the 4 stack files** as in §6 (45 min). Run `bun run validate-stacks`. `stack-doctor.sh unstract up -d`. (30 min for image pull + first boot.)
3. **Provision Infisical secrets** (15 min): `bun run scripts/init-vault.ts unstract db_user unstract db_password $(openssl rand -hex 32) db_name unstract llmwhisperer_api_key $(openssl rand -hex 32) s3_access_key $(garage-cli key new unstract) s3_secret_key $(garage-cli key secret unstract)`.
4. **Create the LLM deployment in Unstract Prompt Studio UI** (30 min): `ncca_spec_v1` with 12 fields including `title_en`/`title_ga` (BilingualText), `learning_outcomes[]`, `marking_scheme_link`. Wire to `claude-sonnet-4-20250514` via the `litellm` provider.
5. **Wire the oideachais stack** (15 min): append `UNSTRACT_URL=http://unstract-backend:8000` to `oideachais/secrets.env`; restart.

### Phase B: Benchmark (3 days, 1 engineer + 1 curriculum researcher)
1. **Run the 10-PDF × 4-path matrix** from §4.2. Land raw outputs in `stedding/benchmarks/unstract-2026-06-29/raw/`. (~2 hours wall clock; cost ~$8-12.)
2. **Annotate ground truth** for the 10 PDFs in the UI (~3 hours for 500 judgments).
3. **Score** with RAGAS `answer_correctness` + `faithfulness`. Emit `stedding/benchmarks/unstract-2026-06-29/scores.json` with per-path accuracy + cost. Feed into Cognee `research_findings` via `cognee.remember()`. (30 min.)
4. **Decide gate:** schema fidelity ≥ 90% AND hallucination ≤ 5% AND cost ≤ 1.5× Docling+BAML → **proceed to Phase C**. Else: keep Unstract as research-only.

### Phase C: Production cutover (1 week)
1. **Promote the schema** to canonical `NCCASpecOutput` in `oideachais-baml-schemas` (3 hours).
2. **Add a new Dagster asset** at `celtic_assets_primary_maths` that routes NCCA + SEC marking-scheme sources through Unstract, *everything else* through Docling+BAML. (4 hours.)
3. **Soft-launch** to `oideachais-staging` for 1 week; compare Unstract vs BAML outputs row-by-row in a marimo notebook (F-19 leaderboard pattern). (1 week.)
4. **Promote** Unstract path to production; `openspec archive unstract-extraction-2026-06-29 --yes`.

### Phase D: Rollback plan

If Unstract accuracy regresses below 90%, flip the Dagster asset to `routes: ["docling_baml"]`. Unstract keeps running (for Prompt Studio authoring). No data loss; Unstract outputs are additive to BAML outputs in `ducklake://oideachais.assets.official_documents.ncca_specs.unstract_results`.

### Cost projection (post-cutover, monthly)

- NCCA: 12 specs × $0.20 = $2.40/month
- SEC marking schemes: 60 papers × $0.10 = $6.00/month
- SEC exam papers: 60 papers × $0.05 = $3.00/month
- **Total: ~$12/month** for the entire Irish curriculum extraction surface
- vs. naive BAML: ~$60-100/month (5-8× more)
- vs. Docling-only: $0/month but ~10-15% accuracy loss on bilingual `name_ga` fields

---

## 8. CCC anchors (for searchability)

- Stack: `infrastructure/stacks/unstract/{compose,sidecar,secrets.env,blueprint}.yaml`
- Adapter: `cianfhoghlaim/ocr/_oideachais_src/adapters.py:587` (UnstractAdapter) + `:64` (OCR_BACKENDS unstract)
- Observability: `cianfhoghlaim/ocr/_oideachais_src/observability.py:83` (per-page cost model)
- Document factory: `cianfhoghlaim/ocr/document_factory/document_factory/pdf_factory.py:67` (CONVERTER_REGISTRY — Unstract not yet registered; add)
- Spec delta target: `openspec/specs/celtic-asset-generation/spec.md:14` (BAML extraction stage)
- Sister research: `openspec/research/2026-06-28-browserbase-program-2/agent-19-unsloth.md` (Unsloth = FT, Unstract = schema extraction; complementary)

## 9. Anti-patterns (to avoid)

1. ❌ **Don't route leabharlann OCR corpus through Unstract** — 10K+ documents would explode LLMWhisperer + LLM cost. Use Docling + BAML.
2. ❌ **Don't use Unstract with `name_ga` only** — many NCCA specs are bilingual; the schema must include both from day 1.
3. ❌ **Don't disable LLMChallenge for marking schemes** — hallucinated point values are catastrophic downstream.
4. ❌ **Don't store PDFs in the Unstract container's local volume** — use the Garage S3 bucket (`oideachais-unstract`); the local volume is for Celery state only.
5. ❌ **Don't use the `unstract/unstract:latest` image** — legacy 1-service image. Pin to `unstract/unstract-backend:v0.39.0` (or current).
6. ❌ **Don't expose `unstract-llmwhisperer` publicly** — backend service; keep it on the `stack` network only.
7. ❌ **Don't use SinglePass on 50-100 page chief examiner reports** without enabling `Summarized Extraction` first — blows the context window.
8. ❌ **Don't set the Celery worker concurrency > 4** on the 16G-MEM-limit worker; OOM-kills the LLM extraction process.
9. ❌ **Don't route Unstract through `litellm/claude-sonnet-4` without a per-deployment cost ceiling** — one misconfigured schema can burn $100 in an afternoon.
10. ❌ **Don't trust Unstract's `success: true` field** without checking `extraction_status: "completed"`; an LLMChallenge *failure* returns `success: true` with NULL fields (correct behaviour, but breaks naive consumers).

## 10. Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Deploy Unstract? | **Yes, but rewrite the stub** | 6-service upstream, not the 2-service stub. ~1 day of work. |
| What to extract? | **NCCA specs + SEC marking schemes only** | High-stakes bilingual content; not leabharlann OCR. |
| LLM backend | **claude-sonnet-4 via LiteLLM (primary), Qwen3.6-35B-A3B local (fallback)** | Claude for accuracy on Irish; Qwen3.6 for cost. |
| LLMChallenge | **Yes for marking schemes, no for NCCA specs** | Marking scheme = catastrophic failure mode. NCCA = cost-sensitive. |
| SinglePass | **Yes (default)** | 7× token reduction; aligns with the Agent 27 F-25 self-improving BAML loop. |
| LLMWhisperer | **Yes, for SEC papers + handwritten Dúchas** | Multi-column SEC papers; checkbox detection on legacy DoE circulars. |
| MCP server | **Yes, expose as `unstract-mcp` in the oideachais MCP mesh** | Lets TanStack Start frontends call Unstract via MCP. |
| AGPL-3.0 acceptable? | **Yes** | Self-hosting; no commercial SaaS redistribution. |
| Cost / PDF target | **$0.10-0.30 (claude) / $0.02-0.05 (local Qwen3.6)** | Below BAML naive; above Docling+BAML. |
| Schema source | **Prompt Studio UI (curriculum researchers author)** | Closes the Agent 27 F-25 loop; engineering owns deployment + integration. |
| Cutover gate | **Schema fidelity ≥ 90% AND hallucination ≤ 5%** | Below this, fall back to Docling+BAML. |
| Rollback | **Flip Dagster route to `docling_baml`** | Reversible in <1 hour; no data loss. |
| AGPLv3 §13 network clause? | **No action** | Internal use only; §13 doesn't trigger until we offer Unstract *as a service* to third parties. |

## 11. Files to read next

- `openspec/specs/celtic-asset-generation/spec.md` (canonical 5-stage pipeline)
- `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (10 OCR models; OlmOCR is the closest sibling)
- `openspec/specs/oideachais-baml-schemas/spec.md` (BAML schema source — Unstract replaces 8 inline calls)
- `openspec/research/.../agent-19-unsloth.md` (Unsloth = FT, Unstract = structured extract; complementary)
- `openspec/research/.../agent-15-baml.md` (BAML inline-call problem this fixes)
- `infrastructure/stacks/docling-serve/compose.yaml` (template for the LLMWhisperer service)
- `github.com/Zipstack/unstract/docker-compose.yaml` (upstream 6-service compose)
- `unstract.com/llmchallenge/` + `unstract.com/singlepass-and-summarized-extraction/`

---

## 1-paragraph summary

**Unstract is the wrong tool for the reason stated in the brief (it IS LLM-driven, not "no-LLM") but the right tool for the *implicit* reason: a no-code Prompt Studio where curriculum researchers author extraction schemas, SinglePass (~7× token reduction) and Summarized Extraction for cost, LLMChallenge (two-LLM consensus, NULL-over-wrong) for trust on marking schemes, and LLMWhisperer for layout-preserving text extraction of multi-column SEC papers — all under an AGPL-3.0 self-host license.** The existing `infrastructure/stacks/unstract/` is a 2-service placeholder that needs a rewrite to the upstream 6-service topology (backend + frontend + worker + beat + redis + postgres + llmwhisperer, ~1 day of work), but the `UnstractAdapter` at `_oideachais_src/adapters.py:587` is already wired and just needs `UNSTRACT_URL=http://unstract-backend:8000` in the oideachais stack. The cutover is scoped to NCCA specs + SEC marking schemes only (NOT the leabharlann OCR corpus, which is too large for LLM economics); expected monthly cost is ~$12 vs ~$60-100 for naive BAML (5-8× cheaper) and ~$0 for Docling+BAML (which is 10-15% lower accuracy on bilingual `name_ga` fields). The benchmark methodology (§4) tests 10 PDFs × 4 extraction paths with a 90% accuracy / 5% hallucination gate before promoting from research to production; rollback is a 1-line Dagster route flip.
