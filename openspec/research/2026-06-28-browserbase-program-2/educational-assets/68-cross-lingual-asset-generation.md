# Agent 68 — Cross-Lingual Asset Generation

**Program:** BrowserBase 2026-06-28 · Agent 68 · cross-lingual-asset-generation
**Date:** 2026-06-28
**Spec refs:** `openspec/specs/celtic-asset-generation/spec.md` (5-stage pipeline) + `openspec/research/2026-06-28-browserbase-program-2/agent-09-cognee.md` (Cognee v1.0 + datasets) + F-02 (`bge-m3` multilingual unification)
**Memory:** `cianfhoghlaim/core/memory/memory/{cognee_config.py,cognee_service.py,letta_memory.py}` + `agents/meaisinfhoghlaim/agents/translation_agent.py`
**BrowserBase credits used:** 0 (no live research; F-08 codegen path uses spec-derived knowledge)

---

## 1. TL;DR

Design spec for generating `celtic-asset-generation` educational assets in **6 languages** (English + Irish `ga` + Welsh `cy` + Scottish Gaelic `gd` + Manx `gv` + Cornish `kw`) on a unified `bge-m3` embedding space (F-02), 6 Cognee datasets (one per language per stage group), a per-language BAML client + prompt set, and English-as-pivot cross-lingual search. Output formats are HTML-first for all 6, audio for 5 (no Manx TTS widely available), and video for 3 (the languages with the largest published curriculum). Single cutover PR: 1 new `clients.baml` block + 6 BAML extraction functions + 6 Cognee dataset names + 1 bge-m3 default + 1 translation agent route.

---

## 2. Per-language requirements

The platform's educational asset corpus must be served in 6 languages, with priority + scale matching actual curriculum availability and Cianfhoghlaim's language-bias policy. Language code follows ISO 639-1/3 with `ga` as the canonical Irish code (not `gle`).

| Lang | ISO | Priority | Curriculum source | Celtic family | Native speakers (2026 est.) | Asset role |
|:--|:--|:--|:--|:--|--:|:--|
| English | `en` | P0 (pivot) | NCCA + SEC + Cambridge + WJEC + SQA | — (pivot) | 1.5 B | Default rendering, all RAGAS evals run in EN first |
| Irish (Gaeilge) | `ga` | **P0 (most important)** | NCCA, COGG, Gaois, Teanglann, Túatha Solas | Goidelic | 200k L1 + 1.8M L2 | **Most asset depth**: 3 dialect bands (Connacht/Munster/Ulster); BAML `ExtractLearningOutcome` canonical path |
| Welsh (Cymraeg) | `cy` | P1 | CBAC/WJEC, Hwb, llyw.cymru, Geiriadur | Brythonic | 870k | AoLEs 1-6 (Areas of Learning & Experience) cross-linked; secondary corpus |
| Scottish Gaelic (Gàidhlig) | `gd` | P1 | SQA, SMO, Sabhal Mòr Ostaig, Gaelic Voice | Goidelic | 60k L1 + 100k partial | Gàidhlig-medium curriculum; ties to leabharlann audio corpus |
| Manx (Gaelg) | `gv` | P2 (small) | Bunscoill Ghaelgagh, Manx Heritage Foundation, Coonceil ny Gaeltey | Goidelic | 2.2k L2 (revival) | Limited corpus; **frequent fallback to EN** for unknown terms; v1 doesn't need audio/video |
| Cornish (Kernewek) | `kw` | P2 (smallest) | Cornish Language Partnership, Golden Tree Productions, Agan Tavas | Brythonic | 600 L2 (revival) | Smallest of the 6; revival corpus only; **English-translated-only** for v1, native extraction deferred to v2 |

**Per-language requirements matrix (concrete artifacts needed):**

| Requirement | `en` | `ga` | `cy` | `gd` | `gv` | `kw` |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|
| BAML extraction function | ✓ | ✓ | ✓ | ✓ | ✓ (fallback to en) | ✓ (fallback to en) |
| CocoIndex embed (bge-m3) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cognee dataset (one per lang) | `oideachais.en` | `oideachais.ga` | `oideachais.cy` | `oideachais.gd` | `oideachais.gv` | `oideachais.kw` |
| Graphiti temporal edge (per lang) | ✓ | ✓ | ✓ | ✓ | — | — |
| HTML asset | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Audio (TTS) | ✓ | ✓ | ✓ | ✓ | — (no TTS) | — (no TTS) |
| Video (FIBO image-gen + TTS) | ✓ | ✓ | ✓ | — | — | — |
| Marimo dashboard localised | ✓ | ✓ | ✓ | ✓ | partial (EN labels) | partial (EN labels) |
| RAGAS eval set (≥30 questions) | ✓ | ✓ | ✓ | ✓ | ✓ (synthetic) | ✓ (synthetic) |

**Key constraint:** all 6 languages embed into a single 1024-dim `bge-m3` space, which means the cosine distance is directly comparable across languages — this is the critical property that enables cross-lingual RAG (an Irish query can retrieve Welsh documents and surface them to the agent). v1 used `bge-large-en-v1.5` + `bge-m3` mixed, which silently broke cross-corpus recall (Agent 03 finding #2). F-02 fixes that.

---

## 3. BAML extraction per language

BAML (`cianfhoghlaim/core/baml/_oideachais_src/`) already has 9 `.baml` files; the v4 consolidation moves 8 inline `anthropic/claude-sonnet-4-20250514` calls onto per-language clients. The pattern is **one client per language + one extraction function per asset type**:

### Clients (`clients.baml`)

```baml
// LLM clients — one per language, with a fall-back chain
client<llm> LocalEn {
  provider: "openai"
  options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" }
}
client<llm> LocalGa {
  provider: "openai"
  options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" }
  // Override system prompt via `client LocalGa` modifier in each function
}
client<llm> LocalCy { provider "openai" options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" } }
client<llm> LocalGd { provider "openai" options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" } }
client<llm> LocalGv { provider "openai" options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" } }
client<llm> LocalKw { provider "openai" options { model "openai/gpt-5-mini" base_url "http://litellm:4000/v1" api_key "no-key-needed" } }

// Stronger model for ambiguous / academic content (fallback chain)
client<llm> StrongEn { provider "openai" options { model "anthropic/claude-sonnet-4-20250514" base_url "http://litellm:4000/v1" api_key "no-key-needed" } }
// + same for Ga/Cy/Gd/Gv/Kw
```

### Per-language prompt scaffolds (extracted to `prompts/celtic/*.baml.j2`)

Each language gets a Jinja prompt template that:
1. Forces output in the source language (don't translate the answer)
2. Provides ISO code + a short corpus note (e.g. for Manx: "Bunscoill Ghaelgagh primary curriculum")
3. Includes 2-3 few-shot examples from the `ex_few_shot` block (per F-25 self-improving loop)

```baml
function ExtractLearningOutcomeGa(pdf_text: string, pdf_images: image[]) -> LearningOutcome[] {
  client LocalGa
  prompt #"
    {{ _.role("system") }}
    Is í Gaeilge an teanga as cainte sa cháipéis seo. Bain amach gach
    LearningOutcome atá le fáil. Caithfidh gach ceann a bheith i nGaeilge.
    Úsáid an schema atá curtha ar fáil.
    {{ _.role("user") }}
    {{ pdf_text }}
  "#
}

function ExtractLearningOutcomeCy(pdf_text: string, pdf_images: image[]) -> LearningOutcome[] {
  client LocalCy
  prompt #"
    {{ _.role("system") }}
    Cymraeg yw iaith y ddogfen hon. Tynnwch bob LearningOutcome.
    Rhaid i bob un fod yn Gymraeg.
    {{ _.role("user") }}
    {{ pdf_text }}
  "#
}
// + Gd, Gv, Kw
```

### Per-language typing with the `BilingualText` pattern

The spec already defines `BilingualText { name_en: str, name_ga: str }`; v4 extends to a 6-language union:

```baml
class CelticText {
  en: string?
  ga: string?
  cy: string?
  gd: string?
  gv: string?
  kw: string?
  source_lang: string  // ISO code of the canonical form
}
```

`CelticText` is populated by the BAML function, then cross-language edges (cognates, translations) are derived in Cognee using the `translates_to` + `is_cognate_of` relationship types already defined in `cognee_config.py:194-225`.

### BAML test coverage (`baml-cli test`)

Each language function gets ≥20 fixture tests (10 positive, 5 negative, 5 dialect-variant for `ga`). Total: ≥120 tests. Failures feed F-25's self-improving loop as `ex_few_shot` examples.

---

## 4. Embedding model — bge-m3 across the board

**Decision:** use **`BAAI/bge-m3`** for all 6 languages (F-02 canonical). Reject per-language models for v1.

### Why bge-m3

| Property | `bge-m3` | Per-language (e.g. `cy-en-large`) |
|:--|:--|:--|
| Dimensions | 1024 | varies (768-1024) |
| Multilingual coverage | 100+ langs (incl. all 6 Celtic) | 1-2 langs each |
| Cross-lingual cosine | comparable across all 6 | not comparable across families |
| Operational cost | 1 model to host + GPU memory | 6 models to host, multi-GPU |
| Already wired | `oideachais-semantic-search` spec (F-02) | not in stack |
| Re-embed corpus on cutover | 12 M chunks (one-shot GPU) | 6× the work + drift risk |

**Critical anti-pattern:** the v1 codebase has `bge-m3` and `bge-large-en-v1.5` *coexisting* across the 14 CocoIndex Apps (Agent 03 finding #2). This means an Irish query (`bge-m3`) and an English result (`bge-large-en-v1.5`) can be 1.0 cosine-similar (since the spaces are different) or 0.0 (since they're orthogonal). F-02 sweeps this; Agent 68's cutover PR depends on F-02 landing first.

### Vector index

Use `declare_vector_index(column="embedding", index_type="IVF_HNSW_SQ")` (Agent 04 finding #1) on the 6 dataset tables. Single shared `lancedb_data/celtic_assets.lancedb` directory; 6 tables:
- `oideachais.en.education.primary.outcomes` … `oideachais.kw.education.tertiary.outcomes` (5 stages × 6 langs = 30 tables)
- One cross-language view: `celtic_assets_all` (union of 30) for cross-lingual RAG

### Embedding call path

```python
# canonical pattern — used by all 6 language pipelines
from sentence_transformers import SentenceTransformer
import os

_model = None
def embed(text: str, lang: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-m3", device=os.environ.get("EMBED_DEVICE", "mps"))
    return _model.encode(text, normalize_embeddings=True).tolist()
```

Note: `lang` is recorded as a metadata column for filtering (when the agent wants Irish-only results) but does **not** change the embed call — `bge-m3` handles the language switch internally.

---

## 5. Translation strategy

### Translation is a fallback, not a primary path

The 6 languages embed into one space, so **the most common case is no translation at all** — the agent retrieves documents in any of the 6 languages and the LLM (gpt-5-mini or claude-sonnet-4) handles the multi-lingual answer synthesis natively.

### When to translate

| Trigger | Action | Backbone |
|:--|:--|:--|
| User query in EN, retrieved chunk in `ga`/`cy`/`gd`/`gv`/`kw` | **No translate** — synthesize across languages | gpt-5-mini |
| User query in `ga`/`cy`/`gd`, retrieved chunk in another Celtic lang | **No translate** — synthesis handles it | gpt-5-mini |
| Dashboard / marimo labels need a specific lang | **Pre-translate** at materialisation time | OPUS-MT (Helsinki-NLP) cached |
| Audio TTS source text | **Pre-translate** to target lang (don't TTS-cross-language) | mlx-audio TTS |
| Manx / Cornish content missing in source lang | **Fall back to English at the source** (not post-hoc translate) | `celtic_translation_agent` |
| External API requires EN (e.g. some RAGAS eval prompt templates) | Translate at the call boundary | OPUS-MT `LocalEn` client |

### English-as-pivot for cross-language search

For RAGAS eval, the canonical eval set is authored in English (the highest-resource language for evaluation tools). The eval pipeline translates every generated answer back to English using `celtic_translation_agent` (already in `agents/meaisinfhoghlaim/agents/translation_agent.py`) before scoring. The translation is a single OPUS-MT call (or `LocalEn` LLM call if the OPUS-MT confidence < 0.8).

### Dialect handling (Connemara / Munster / Ulster)

Irish has 3 dialect bands. v1 represents them as separate `CelticText` fields when the source corpus is dialect-tagged (NCCA primary maths is largely standard; Raidió na Gaeltachta transcripts are dialect-tagged). The `dialect_variant` entity type in `cognee_config.py:194-225` carries this. No automatic dialect-to-standard normalisation in v1; deferred to v2 with a Connacht→standard MLX-omni local model.

### Translation agent integration

The existing `translation_agent.py` already supports `ga↔en`, `gd↔en`, `cy↔en`, and inter-Celtic. **Extend** it with `gv↔en` and `kw↔en` pairs (currently missing) using:
- `gv↔en`: Helsinki-NLP `opus-mt-gv-en` (low quality due to tiny corpus) → fallback to `gpt-5-mini` `LocalEn` for synthesis
- `kw↔en`: Helsinki-NLP `opus-mt-kw-en` (low quality) → same fallback

---

## 6. Asset format per language

### HTML — universal, all 6 languages

All 6 languages render the same HTML asset structure (`/dashboards/curriculum/{lang}/...`), produced by the same BAML extraction → same CocoIndex embed → same Marimo dashboard. Only the i18n bundle (translation JSON) and the data filter (`lang={iso}`) change. TanStack Start's `i18n` route param picks the bundle.

### Audio (TTS) — 4 languages

| Lang | TTS backbone | Voice | Source |
|:--|:--|:--|:--|
| `en` | `mlx-audio[tts]` + `Kokoro-82M` | `en_male_1` / `en_female_1` | mlx-omni |
| `ga` | `mlx-audio[tts]` + `ga_IE-cms_16k-cms` (Coqui) | `ga_female_1` (RTÉ licensed) | F-11 dep |
| `cy` | `mlx-audio[tts]` + `cy_GB-pure_16k` (Coqui) | `cy_male_1` (Bangor Univ.) | F-11 dep |
| `gd` | `mlx-audio[tts]` + `gd_GB-cmd_16k` (Coqui, low quality) | `gd_female_1` | F-11 dep |
| `gv` | — (no Manx TTS model available; recordings are pre-recorded) | n/a | n/a |
| `kw` | — (no Cornish TTS model) | n/a | n/a |

Audio assets are pre-rendered at materialisation time (Dagster asset) and stored as MP3 in `lakehouse-s3://oideachais-assets/audio/{lang}/{asset_id}.mp3`. RAGAS measures WER per language (F-19 ASR leaderboard feeds this).

### Video (FIBO + TTS) — 3 languages

| Lang | Video backbone | Pipeline |
|:--|:--|:--|
| `en` | FIBO image gen (Qwen-Image-2512 / FLUX.2-klein-9B) + `mlx-audio[tts]` + ffmpeg | `tuatha/game/pipelines/celtic_video.py` (F-09 style) |
| `ga` | Same FIBO + `ga_IE` TTS + ffmpeg | Same pipeline, `lang=ga` |
| `cy` | Same FIBO + `cy_GB` TTS + ffmpeg | Same pipeline, `lang=cy` |
| `gd` / `gv` / `kw` | — (v1 deferred; deferred to v2 when quality improves) | n/a |

Video assets are <2-min educational shorts, ~10/month per language, produced by the Dagster `celtic_video_production` asset. Stored in `lakehouse-s3://oideachais-assets/video/{lang}/{asset_id}.mp4`.

### Asset format decision matrix

| Format | Languages | Backbone | Output location | RAGAS target |
|:--|:--|:--|:--|:--|
| HTML (Marimo dashboard) | 6 (`en`,`ga`,`cy`,`gd`,`gv`,`kw`) | Marimo + TanStack Start | `dashboards/{lang}/...` | layout fidelity (P95) |
| Audio (TTS) | 4 (`en`,`ga`,`cy`,`gd`) | mlx-audio + Kokoro/Coqui | `s3://oideachais-assets/audio/{lang}/` | WER (F-19) |
| Video (FIBO + TTS) | 3 (`en`,`ga`,`cy`) | FIBO image gen + ffmpeg | `s3://oideachais-assets/video/{lang}/` | qualitative review (v1) |
| Print-ready PDF | 6 | Puppeteer headless | `s3://oideachais-assets/pdf/{lang}/` | layout fidelity (P95) |
| 3D Babylon.js scene | 3 (`en`,`ga`,`cy`) | F-09 round-tower pipeline | `tuatha/game/assets/celtic/...` | render P95 (manual) |

---

## 7. Cutover — 1 PR

**Title:** `feat(celtic-asset-generation): cross-lingual asset generation for 6 languages (en/ga/cy/gd/gv/kw)`

**Base branch:** `main` (depends on **F-02 bge-m3 unification** already merged)

**Branch:** `feat/agent-68-cross-lingual-assets`

**File changes (~14 files, +1,800 / -120 lines):**

| File | Change |
|:--|:--|
| `cianfhoghlaim/core/baml/_oideachais_src/clients.baml` | **+**: 6 `Local{En,Ga,Cy,Gd,Gv,Kw}` + 6 `Strong{En,Ga,Cy,Gd,Gv,Kw}` clients |
| `cianfhoghlaim/core/baml/_oideachais_src/celtic_extraction.baml` | **+**: 6 new `ExtractLearningOutcome{Lang}` functions; `CelticText` class with 6 lang fields |
| `cianfhoghlaim/core/baml/_oideachais_src/prompts/celtic/{en,ga,cy,gd,gv,kw}.baml.j2` | **+**: 6 new Jinja prompt templates |
| `cianfhoghlaim/core/baml/_oideachais_src/tests/celtic_extraction.baml` | **+**: ≥120 fixture tests (20 per lang) |
| `cianfhoghlaim/assets/asset_generation/language_assets/embed.py` | **NEW**: `bge-m3` embed wrapper (single 1024-d space) |
| `cianfhoghlaim/assets/asset_generation/language_assets/cognify.py` | **NEW**: per-language Cognee `remember` calls; 6 datasets `oideachais.{en,ga,cy,gd,gv,kw}` |
| `cianfhoghlaim/assets/asset_generation/language_assets/dagster_asset.py` | **NEW**: 1 `celtic_cross_lingual_assets` Dagster asset (per language partition) |
| `cianfhoghlaim/agents/meaisinfhoghlaim/agents/translation_agent.py` | **+**: `gv↔en` + `kw↔en` pairs (Helsinki-NLP OPUS-MT + LocalEn fallback) |
| `cianfhoghlaim/core/memory/memory/cognee_service.py` | **M**: register 6 new datasets in `DATASETS` constant |
| `infrastructure/stacks/cognee/compose.yaml` | **M**: add 6 dataset names to `COGNEE_DATABASES` env (dot-notation, fixes R2) |
| `cianfhoghlaim/core/memory/memory/cognee_config.py` | **M**: add 6 new entity types: `celtic_phrase`, `cross_lingual_cognate`, etc. |
| `openspec/changes/2026-06-28-cross-lingual-asset-generation/proposal.md` | **NEW**: proposal |
| `openspec/changes/2026-06-28-cross-lingual-asset-generation/tasks.md` | **NEW**: 12 tasks |
| `openspec/changes/2026-06-28-cross-lingual-asset-generation/specs/celtic-asset-generation/spec.md` | **NEW**: delta — adds Requirement "Cross-lingual 6-language asset generation" + 2 Scenarios |
| `openspec/changes/2026-06-28-cross-lingual-asset-generation/specs/oideachais-storage/spec.md` | **NEW**: delta — adds Requirement "6 Cognee datasets, one per language" |

**Test plan (PR-checklist):**
- `baml-cli test celtic_extraction.baml` — 120 tests, ≥95% pass
- `pytest cianfhoghlaim/assets/asset_generation/language_assets/` — embed + cognify unit tests
- RAGAS: 30-question eval set per language (180 total) — faithfulness ≥0.85, answer-relevance ≥0.80
- `openspec validate 2026-06-28-cross-lingual-asset-generation --strict` — must pass
- Cognee `cognify_status` — 6 datasets show ≥1 successful cognify cycle

**Risk register:**
| Risk | Mitigation |
|:--|:--|
| bge-m3 re-embed of 12 M chunks takes >24 h | Run on Modal A100 burst (F-04); 1× GPU warm pool |
| Manx / Cornish extraction quality low (small corpora) | v1: fall back to EN at source; v2: hand-curated few-shot examples |
| Cognee dataset naming drift (Agent 09 finding) | PR fixes R2 — dot-notation in both compose.yaml and code |
| Dialect handling for Irish (Connacht/Munster/Ulster) | Record dialect as metadata, no automatic normalisation in v1 |

**Effort estimate:** M (1-2 weeks, 1 squad), 1 PR.

---

## 1-paragraph summary

This spec defines cross-lingual asset generation for 6 languages (English + Irish + Welsh + Scottish Gaelic + Manx + Cornish) on a unified 1024-dim `bge-m3` embedding space, with per-language BAML extraction functions and clients in `celtic_extraction.baml`, 6 Cognee datasets (`oideachais.{en,ga,cy,gd,gv,kw}`) one per language, English-as-pivot translation only when necessary (dashboard labels, TTS source, RAGAS eval), HTML assets in all 6 languages, audio TTS in 4 (no Manx/Cornish TTS available), and FIBO+ffmpeg video in 3 (the languages with the largest published curriculum). Manx and Cornish use a `gv↔en`/`kw↔en` OPUS-MT bridge with `LocalEn` LLM fallback for low-confidence cases; v1 defers dialect-to-standard normalisation for Irish. Single cutover PR adds 1 new `clients.baml` block + 6 BAML extraction functions + 6 Cognee dataset registrations + 1 `bge-m3` embed wrapper + 1 Dagster asset + 1 translation-agent extension, depends on F-02 (`bge-m3` unification) landing first, and fixes the Agent 09 R2 dataset-naming drift as a side effect.
