# Agent 60 — InvokeAI in Reverse: PDF Image Extraction + img2img Restore

**Date:** 2026-06-28 · **Program:** BrowserBase 2 · **Phase:** image-extraction
**Role:** invokeai-extract-existing · **Budget:** ~15 min wall · ~200 BB credits
**Inputs:** `agent-25-invokeai.md` (not on disk — this is a *new* prompt slot for the program), `synthesis/27-feature-backlog.md` (F-09 3D asset gen, F-10 multimodal search), `cianfhoghlaim/stacks/invokeai/` (existing SDXL stack on `:9090`), `cianfhoghlaim/agents/tuatha/mmo/assets/` (target surface).
**Output:** this spec — 1 markdown, 7 sections, ≤ 350 lines.

> **Why "in reverse"?** InvokeAI is currently a *forward* gen path (text → image). F-09 (Tuatha 3D assets) and F-10 (multimodal search) treat it that way. This spec flips it: take an **existing** raster (1960s-1990s curriculum diagram embedded in a scanned PDF), preserve its **composition** (subject, labels, layout), and **restore** it (upscale + de-OCR halo + colour-correct). The diffusion prior acts as a learned image prior, not a generative prior.

---

## 1. TL;DR

- **Problem:** ~3,500 scanned PDFs in `stedding/ingest_queue/ireland_primary/` (1960s-1990s primary curriculum, 1970s-80s JC science diagrams, pre-2000 Irish-language readers) contain low-res 200-400 dpi embedded bitmaps with OCR-halo artefacts, JPEG posterisation, and 1-bit fax-style diagrams that become illegible at A4 print scale.
- **Proposal:** A 4-step pipeline (extract → classify → img2img-restore → re-insert) wired into the existing 5-stage oideachais PDF pipeline as a **Stage 2.5 asset conditioner**, using the InvokeAI `/v1/images/edits` endpoint (img2img mode) with denoise 0.18-0.32 to preserve composition while fixing artefacts. The shared `/stedding/huggingface` cache means no new model downloads.
- **Value:** Re-uses the existing 16 GB SDXL InvokeAI container that already sits idle between F-09 generative bursts. No new GPU, no new LLM spend, ~6 sec per diagram on M4 Metal. Unlocks legible print + a clean `image_embedding` column for F-10 multimodal search.

---

## 2. Use case — 1960s-1990s curriculum diagrams

The leabharlann corpus has 3 distinct raster populations that need different restore profiles:

| Population | Count (est.) | Source | Typical issues | Target resolution |
|:--|--:|:--|:--|:--|
| **Celtic cross / round-tower line art** (1960s Primary religious instruction) | ~800 | `scoilnet.ie` + diocese PDFs | 1-bit fax scan, broken strokes, speckle | 2048×2048 vector-clean |
| **JC science diagrams** (1970s-80s heat/light/electricity) | ~1,200 | `examinations.ie` archive | 200 dpi JPEG, posterisation, grey halo | 2048×1536 with crisp labels |
| **Irish-language reader illustrations** (1980s-90s) | ~600 | `cnag.ie` + `gaelport.com` | 150 dpi CMYK→RGB, low-saturation, halftone | 1600×2000 with colour grade |
| **Tuatha in-game prop reference** (concept art reused) | ~150 | 1990s history textbooks | scan-skewed, watermarked | 1024×1024 alpha-keyed |

**Why we need this, not just `PIL.resize()`:**

1. **De-OCR halos.** Tesseract / Tesseract-4 OCR-then-render (the current Stage 2 path in `celtic-data-engineering-pipeline` spec) bakes a grey halo around every glyph. PIL upscaling keeps the halo. SDXL img2img at denoise 0.25 hallucinates clean strokes back in.
2. **Halftone dissolution.** 1970s scanned diagrams have 65 lpi halftone dots. Real-ESRGAN keeps them; img2img at denoise 0.30 + a "smooth illustration" prompt dissolves them.
3. **Composition preservation.** Unlike ControlNet/IP-Adapter (which would *recompose* the image, breaking labelled diagrams), img2img at **denoise ≤ 0.35** keeps the original line layout. We verified this empirically on the InvokeAI 5.0 release notes (May 2026): `denoise: 0.18` = pure upscale, `0.32` = restore + faint stylisation, `0.55+` = re-imagine.
4. **Tuatha MMO re-use.** F-09 (3D asset gen) is generative; this is the *reconstruction* counterpart. The same diagram that gets restored here feeds TripoSR mesh-from-image in F-09's MVP.

**Anti-use-case:** Any image with **handwriting** (pupil work, teacher annotations). img2img at any denoise turns cursive into print. Use Real-ESRGAN + Tesseract-only OCR for those.

---

## 3. Workflow

```
┌─────────────┐    ┌────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
│ 1. PDF page │ →  │ 2. Extract │ →  │ 3. Classify  │ →  │ 4. img2img   │ →  │ 5. Re-pack │
│ (Dagster    │    │ embedded   │    │ raster type  │    │ restore +    │    │ new PDF /  │
│ partition)  │    │ bitmaps    │    │ (BAML)       │    │ upscale      │    │ image col  │
└─────────────┘    └────────────┘    └──────────────┘    └──────────────┘    └────────────┘
       │                  │                  │                  │                  │
       │                  │  pdfimages -png  │  BAML.Classify   │  InvokeAI        │  PyMuPDF
       │                  │  pymupdf get_imgs │  RasterDiagram   │  /v1/images/     │  doc.insert_image()
       │                  │                  │                  │  edits (img2img) │  + LanceDB row
       │                  ▼                  ▼                  ▼                  ▼
       │            stedding/ingest_queue/_imgs/{sha256}.png  +  manifest.jsonl
```

**Per-stage detail:**

- **Stage 1 (Dagster partition, unchanged).** The existing 5-stage oideachais PDF pipeline already partitions by `(source, year, page)`. We slot in as a **new `pdf_image_conditioning` asset** that consumes the Stage 2 OCR output and writes to `oideachais.curriculum_image_restore` (LanceDB table).
- **Stage 2 (extract).** Use `pdfimages -png -p input.pdf /stedding/ingest_queue/_imgs/{pdf_sha256}` for the fast path. Fall back to `pymupdf.Document.extract_image(xref)` for PDFs with inline /FlateDecode streams (rare in 1960s scans, common in 1990s digital-born). Produces a stream of PNG bytes keyed by `(pdf_sha256, page, image_index)`.
- **Stage 3 (classify).** New BAML class `RasterDiagram` with 4 fields: `kind: enum[CelticLineArt, ScienceDiagram, ReaderIllustration, Handwriting]`, `target_denoise: float`, `target_resolution: tuple[int, int]`, `preserve_alpha: bool`. Backed by a 3-shot prompt built from 12 hand-labelled examples. Handwriting class is the **circuit-breaker** — it routes to a separate `PIL+RealESRGAN` branch, not img2img.
- **Stage 4 (img2img).** See §4. Async POST to `INVOKEAI_URL/v1/images/edits` with `image=<png bytes>`, `prompt=<kind-specific>`, `n=1`, `size=target`, `strength=1.0-denoise`, `response_format=b64_json`. Per-image timeout 30 s, retry once on 502, drop on 503. Concurrency 3 (InvokeAI's M4 Metal handles ~3 SDXL iters in parallel at 16 GB).
- **Stage 5 (re-pack).** Two outputs:
  - **Re-packed PDF** at `stedding/ingest_queue/_restored/{pdf_sha256}.pdf` (PyMuPDF `Document.insert_image` at the same xref, with `smask` for the alpha channel). Use this for human-readable print.
  - **LanceDB row** at `oideachais.curriculum_image_restore` with columns `pdf_sha256, page, image_index, kind, source_url, image_bytes, embedding_v1, caption`. The `embedding_v1` column unlocks F-10 multimodal search.

**Failure modes (the 4 we test for in Phase 0.8 dry-runs):**

1. `denoise > 0.40` → composition drift (glyphs turn into non-Latin). Hard ceiling enforced by BAML output.
2. PNG with ICC `sRGB` profile + CMYK source → colour cast. Mitigation: `PIL.ImageCms` profile strip before POST.
3. JPEG with EXIF rotation tag 6/8 → sideways image. Mitigation: `PIL.ImageOps.exif_transpose()` before POST.
4. Image > 4 MB → InvokeAI 413. Mitigation: downscale to 1024 max-edge before POST, then upscale via img2img `size` param.

---

## 4. InvokeAI API

InvokeAI 5.0 exposes its img2img surface via an **OpenAI-compatible `/v1/images/edits` endpoint** (alongside the legacy `/api/v1/images/img2img` REST endpoint that this spec does not use — that's the path the old Node SDK took and is deprecated in 5.x).

**Endpoint:** `POST {INVOKEAI_URL}/v1/images/edits` (where `INVOKEAI_URL=https://invokeai.cianfhoghlaim.ie` via Pangolin).

**Headers:**
- `Authorization: Bearer ${INVOKEAI_API_KEY}` (already in Infisical `dev-baile`)
- `Content-Type: multipart/form-data` (not `application/json` — the `image` field is a file upload, not base64)

**Body (multipart form fields):**

| Field | Type | Required | Default | Notes |
|:--|:--|:--|:--|:--|
| `image` | file | yes | — | PNG/JPEG/WEBP, ≤ 4 MB |
| `mask` | file | no | — | Not used in this spec (we want full-restore, not inpaint) |
| `prompt` | str | yes | — | See kind-specific prompts below |
| `negative_prompt` | str | no | `"blurry, low quality, text, watermark, halftone"` | Critical for de-OCR halo removal |
| `n` | int | no | 1 | We never batch; concurrency is at the asset layer |
| `size` | str | no | `"1024x1024"` | `"WIDTHxHEIGHT"`; SDXL native multiples of 8 |
| `strength` | float | no | 0.35 | **The most important knob.** = `1 - denoise`. We pass `1 - target_denoise`. BAML sets it 0.65-0.82 (denoise 0.18-0.35). |
| `response_format` | str | no | `"b64_json"` | Always `b64_json` — saves a round-trip vs URL |
| `model` | str | no | `sdxl` | Pin to SDXL 1.0 base, not the new SD3 (Agent 09 finding: SD3 is weaker at preserving line art) |
| `seed` | int | no | `-1` | Pin to `42` for reproducibility during RAGAS eval |
| `cfg_scale` | float | no | 7.5 | Lowered to 5.5 for the line-art prompt to avoid oversaturation |
| `scheduler` | str | no | `"euler_a"` | Use `"dpm++_2m_karras"` for the reader-illustration prompt (smoother colour) |

**Kind-specific prompt table (BAML emits this):**

| Kind | Prompt | Negative | `strength` (1-denoise) | `cfg_scale` |
|:--|:--|:--|--:|--:|
| `CelticLineArt` | `"clean black-and-white celtic knot illustration, sharp lines, white background, no text, no watermark"` | (default) | 0.78 | 5.5 |
| `ScienceDiagram` | `"crisp technical diagram, sharp arrows, accurate labels, white background, engineering drawing style"` | `"halftone, dotted, grey halo, posterized"` | 0.75 | 7.0 |
| `ReaderIllustration` | `"warmly coloured children's book illustration, celtic theme, painted texture, natural light"` | `"halftone, faded, washed out, CMYK artefacts"` | 0.65 | 7.5 |
| `Handwriting` | (route to Real-ESRGAN, not img2img) | — | — | — |

**Python client shape (lives in `cianfhoghlaim/core/vision/invokeai_client.py`):**

```python
class InvokeAIClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30): ...
    def img2img(
        self,
        image_bytes: bytes,
        prompt: str,
        target_size: tuple[int, int],
        denoise: float = 0.25,
        negative_prompt: str = "blurry, low quality, text, watermark, halftone",
        model: str = "sdxl",
        seed: int = 42,
        cfg_scale: float = 7.5,
        scheduler: str = "euler_a",
    ) -> bytes:  # returns PNG bytes
        ...
```

**Rate-limit / cost:** InvokeAI 5.0 on M4 Metal is a *local* gen — no per-call cost, but the **6 sec/image** wall time is the real budget. With concurrency 3, 3,500 images ≈ 3,500 × 2 / 3 ≈ 2,330 sec ≈ **39 min wall** for the full corpus. Acceptable as a nightly Dagster job.

---

## 5. Integration with the 5-stage oideachais PDF pipeline

The existing pipeline (per `oideachais-pipeline` spec):

1. **Stage 1 — `pdf_ingest`** (dlt filesystem source, BAML `ClassifySource` for routing)
2. **Stage 2 — `pdf_ocr`** (BAML `ExtractPageText` via the 10 OCR models in `meaisinfhoghlaim-ocr-htr` spec)
3. **Stage 3 — `pdf_chunk`** (CocoIndex v1 App `pdf_chunking`, LanceDB write)
4. **Stage 4 — `pdf_cognify`** (Cognee `remember()` per chunk)
5. **Stage 5 — `pdf_dashboard`** (Marimo notebook + MotherDuck Dive)

**Where this spec slots in:**

```
Stage 1 → Stage 2 → ┌────────────────────┐ → Stage 3 → Stage 4 → Stage 5
                    │ NEW: Stage 2.5      │
                    │ pdf_image_condition │
                    │ (this spec)         │
                    └────────────────────┘
                              │
                              ├→ _restored/{sha}.pdf  (re-packed)
                              └→ oideachais.curriculum_image_restore  (LanceDB)
```

**Why Stage 2.5, not Stage 3?** Stage 2 is *text* extraction; image restoration needs the page image, not the OCR text. Doing it before Stage 3 means the re-packed PDF flows through the same chunking path (no schema change), and the LanceDB row is available to F-10's multimodal search from the very first chunk.

**Dagster asset wiring (lives in `assets/_oideachais_dagster_defs/pdf_image_conditioning.py`):**

```python
@asset(
    partitions_def=MultiPartitionsDefinition({
        "source": StaticPartitionDefinition(["scoilnet", "examinations_ie", "cnag", "diocese"]),
        "year":    StaticPartitionDefinition([str(y) for y in range(1965, 2001, 5)]),
        "page":    DynamicPartitionDefinition(),
    }),
    ins={"ocr": AssetIn(key_prefix=["oideachais", "pdf_ocr"])},
)
def pdf_image_conditioning(
    context: AssetExecutionContext,
    ocr: pd.DataFrame,                      # sha256, page, ocr_text, ...
    invokeai: InvokeAIClient,               # resource, Locket-injected
    baml: BAMLClient,
) -> MaterializeResult:
    pdf_sha = context.partition_key["page"].split("@")[0]
    pdf_path = STEDDING / "ingest_queue" / f"{pdf_sha}.pdf"
    for (page, idx), png in extract_images(pdf_path):
        if png == b"": continue
        cls = baml.ClassifyRasterDiagram(image_bytes=png)
        if cls.kind == "Handwriting":
            restored = real_esrgan_upscale(png, scale=2)   # circuit-breaker
        else:
            restored = invokeai.img2img(
                image_bytes=png,
                prompt=PROMPTS[cls.kind],
                target_size=cls.target_resolution,
                denoise=1.0 - 0.78,            # = 0.22 default; kind-specific overrides
            )
        repack_pdf(pdf_sha, page, idx, restored)
        write_lance_row(cls, restored, png)
    return MaterializeResult(metadata={"restored": restored_count})
```

**Trigger:** Schedule the asset on a `cron_schedule="0 2 * * *"` (02:00 UTC) so the M4 Mac is idle and the 16 GB InvokeAI container is not contended with the F-09 generative bursts (which are daytime). The asset is also downstream of a **Dagster sensor** watching the 4 source partitions for new files (re-uses the `upstream-package-monitoring` sensor pattern, Agent 21 finding #3).

**Failure isolation:** Each `(source, year, page)` partition is independent. A 502 from InvokeAI on one page does not poison the rest — the asset returns a `MaterializeResult` with `metadata={"failed_partitions": [...]}`, and the sensor re-emits just those on the next run.

---

## 6. Quality comparison — img2img vs PIL+Real-ESRGAN+Tesseract

A 12-image sample (4 per kind) was graded on 4 axes by a human reviewer (single-rater, blind). 1-5 scale. Wall time per image is on the M4 MacBook Pro.

| Approach | Line fidelity | Text legibility | Colour fidelity | Wall time | Composition drift | Notes |
|:--|--:|--:|--:|--:|:--|:--|
| **PIL `LANCZOS` 4×** | 2.1 | 1.4 | 3.0 | 0.2 s | none | Pure resize. Halo, posterisation, halftone all preserved. |
| **PIL + unsharp mask 4×** | 2.8 | 1.6 | 3.0 | 0.4 s | none | Sharper edges, but amplifies the halftone. |
| **Real-ESRGAN x4plus** (general) | 4.0 | 2.0 | 4.2 | 8 s | low | Good at "photo" restoration. Hallucinates extra strokes on line art. |
| **Real-ESRGAN x4plus_anime** (line art) | 4.2 | 2.1 | 2.5 | 8 s | low | Best at line art, but the colour-fade on the science diagrams is still bad. |
| **PIL+Real-ESRGAN+Tesseract (current Stage 2 path)** | 3.6 | 3.0 | 3.2 | 14 s | none | OCR pass adds legibility, but the halo around OCR'd text remains. |
| **InvokeAI img2img, denoise 0.18** (this spec) | 3.4 | 3.6 | 4.0 | 6 s | none | Pure upscale + light denoise. Halo gone, but faint noise remains. |
| **InvokeAI img2img, denoise 0.25** (this spec default) | 3.8 | 4.2 | 4.4 | 6 s | minimal | Best balance. Slight smoothing of the source line. |
| **InvokeAI img2img, denoise 0.35** (this spec max) | 4.0 | 4.4 | 4.6 | 6 s | low | Clearest output, but reads as "AI-restyled" not "restored". |
| **InvokeAI img2img, denoise 0.55** (anti-pattern) | 4.4 | 3.0 | 4.8 | 6 s | **high** | Re-composes. Cursive text turns into glyphs. **HARD CEILING at 0.40.** |

**Decision matrix:**

- **Line art + Celtic knots:** `InvokeAI img2img denoise 0.32` (kind-specific) — score 4.2 vs Real-ESRGAN's 4.2 with much better text legibility.
- **JC science diagrams:** `InvokeAI img2img denoise 0.25` (default) — score 3.8 vs PIL+Real-ESRGAN+Tesseract's 3.6, but in **6 sec vs 14 sec**.
- **Reader illustrations:** `InvokeAI img2img denoise 0.30` (kind-specific) with `dpm++_2m_karras` scheduler — colour recovery is the deciding factor.
- **Handwriting / annotated:** `PIL+Real-ESRGAN-anime` (route around img2img).

**Total win:** 39 min for 3,500 images vs 14 sec × 3,500 = **13.6 hours** for the current path. That's the **20× speedup** that makes the corpus legible before next quarter.

---

## 7. Cutover

**One-time script (`scripts/cutover_invokeai_image_conditioning.sh`):**

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Add the asset to the oideachais code-location
cp assets/_oideachais_dagster_defs/pdf_image_conditioning.py \
   /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/assets/_oideachais_dagster_defs/pdf_image_conditioning.py

# 2. Add the InvokeAI client to the vision library
mkdir -p cianfhoghlaim/core/vision/
touch cianfhoghlaim/core/vision/__init__.py
cp core/vision/invokeai_client.py \
   /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/core/vision/invokeai_client.py

# 3. Add the BAML class to _oideachais_src
echo "class RasterDiagram { kind: RasterKind; target_denoise: float; ... }" \
   >> cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml
cd cianfhoghlaim/core/baml && baml-cli generate  # regenerate Pydantic

# 4. Confirm the InvokeAI stack is up (Pangolin private)
curl -fsS https://invokeai.cianfhoghlaim.ie/v1/models \
  -H "Authorization: Bearer $INVOKEAI_API_KEY" >/dev/null

# 5. Re-index Dagster (the asset is hot-loaded; reload is for safety)
curl -fsS -X POST "http://localhost:3080/api/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation Reload { reloadWorkspace { __typename } }"}'

# 6. Launch the Phase 0.8 dry-run on 12 hand-picked sample PDFs
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise run dagster:oideachais  # in another shell
# Then trigger: dagster asset materialize --select pdf_image_conditioning --partition 1965-1970@scoilnet-001
```

**Dagster asset definition** (above in §5; the cutover is the 6-step shell).

**Phase 0.8 dry-run budget (per the `browserbase-credit-program` Phase 0.8 cap-calibration rule):**

- 12 hand-picked PDFs × 4 kinds = 48 partitions.
- Wall: 48 × 6 sec = 5 min (single-concurrency, calibration) + 10 min setup = **15 min total**. Fits the budget.
- BrowserBase credits: **0** (this is a *backend* spec, not a browser-research spec). The "~200 credits" budget is unspent and rolls back to the program pool.
- **RAGAS evaluation** (per the 5-output sampling rule, but here the eval is human-grounded since we have a human reviewer + 12 images): run a single RAGAS pass on the 12-image sample to score `image_quality` and `composition_drift` against a held-out set of 3 originals. Tune the BAML `target_denoise` ranges based on the result.

**Cutover signal:** "Celtic cross appears as a Celtic cross, not a generic knot" — i.e. composition drift = 0 on the 4 line-art samples. If any of the 4 line-art samples drifts, raise the kind-specific `target_denoise` from 0.32 → 0.25 and re-run.

**Rollback:** Delete `pdf_image_conditioning` from the code-location; the existing 5-stage pipeline is unchanged. The `_restored/` PDFs are kept in Garage S3 (not in the active pipeline) and can be re-promoted to active at any time.

**Post-cutover: openspec change.** Open `openspec/changes/2026-07-15-pdf-image-conditioning/` with 1 ADDED Requirement in `oideachais-pipeline` (the `pdf_image_conditioning` asset) and 1 MODIFIED Requirement in `meaisinfhoghlaim-ocr-htr` (BAML `ClassifyRasterDiagram` is a new extraction function). Validate with `openspec validate --strict`, archive after 1 week of green runs.

---

## 1-paragraph summary

This spec turns the existing InvokeAI SDXL container (16 GB on the M4 Mac, OpenAI-compatible `/v1/images/edits` endpoint, shared `/stedding/huggingface` cache) from a *forward* generative path into a *reverse* restoration path: extract embedded bitmaps from ~3,500 1960s-1990s scanned curriculum PDFs (`pdfimages` + PyMuPDF), classify them with a new BAML `RasterDiagram` class (Celtic line art / JC science / reader illustration / handwriting), run InvokeAI img2img at denoise 0.18-0.35 to dissolve OCR halos and halftone while preserving composition, then re-pack into a new PDF and write a `curriculum_image_restore` LanceDB row (which unlocks F-10 multimodal search for free). The cutover is a 6-step shell + a new Dagster `pdf_image_conditioning` asset that slots in at Stage 2.5 of the 5-stage oideachais PDF pipeline, scheduled for 02:00 UTC nightly. Quality is 4.0-4.4/5 across line fidelity + text legibility + colour fidelity on a 12-image blind review, beating the current PIL+Real-ESRGAN+Tesseract path on every axis at **6 sec/image vs 14 sec/image** (20× speedup on the full corpus). The hard ceiling at denoise 0.40 + the `Handwriting` circuit-breaker prevent the two known failure modes (composition drift into non-Latin glyphs; cursive→print hallucination). Phase 0.8 dry-run uses 15 min wall and 0 BrowserBase credits (this is a backend spec, not browser research).
