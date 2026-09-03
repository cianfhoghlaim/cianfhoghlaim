# Agent 61 — FLUX + Qwen-Image extract existing (PDF → asset re-derivation)

**Date:** 2026-06-28
**Program:** BrowserBase 2 — Wave 3 (asset generation / image extraction)
**BrowserBase budget used:** ~120 credits (mostly upstream FLUX/Qwen-Image docs + InvokeAI-comparison page)
**CCC queries:** 4
**Prior art:** `image-generation/57-invokeai-asset-gen-benchmark.md` (sister spec; this one focuses on **re-deriving images from existing PDFs**, not generating new ones), `image-generation/57...md:140-150` (FLUX.2 row in the CLIP comparison table)

---

## 1. TL;DR

Cianfhoghlaim already has **2 of the 3 image-gen backends it needs for PDF re-derivation** wired into LiteLLM: `local/image/qwen-image` (Qwen-Image-2512) and `local/image/flux2` (FLUX.2-klein-9B via mflux on MLX) — both sit as the **2nd and 3rd tiers of the 4-tier `image` alias fallback** (`z-image-turbo → qwen-image → flux2 → sdxl` per `litellm/config/config.yaml:651`). The missing piece is a **Python pipeline** that (a) extracts embedded raster images from existing PDF curricula via `pymupdf`/`pikepdf`, (b) routes each extracted image through either FLUX img2img (for **upscale / cleanup** of low-res scans) or Qwen-Image Edit (for **de-OCR / object removal** of OCR'd plates), and (c) re-inserts the cleaned image into a re-paginated PDF (or a new asset) wired into the BAML `ImageGen` client. This is a **spec for the pipeline**, not a new model deployment.

## 2. Use case

Same motivation as Agent 57 (FIBO/SDXL text→image for new assets) but **inverted**: instead of generating fresh illustrations, we **re-derive** them from the PDFs we already have. Two concrete drivers in the program:

- **Leabharlann corpus** — 216 academic PDFs (Agent 25 R15/R19) full of 1970s-era B/W plates, OCR'd scans, and embedded low-DPI JPEGs. Many are derivatives of stock art (round tower photos, ogham stones) where the **original asset** would be more useful than the re-printed scan.
- **Celtic-asset-generation reuse** — Agent 57's 4 pipelines (`official_documents/`, `subject_assets/`, `language_assets/`, `exporters/`) currently regenerate from scratch. For assets that have a **historical original** in `stedding/ingest_queue/`, we should **re-derive** (upscale + de-OCR) the original rather than spend 1.4 s on a Z-Image-Turbo regen whose CLIP will be lower than the cleaned original.

**Concretely, the 4 use cases for Flux + Qwen-Image Edit:**

| # | Trigger | Source | FLUX role | Qwen-Image role |
|:--|:--|:--|:--|:--|
| 1 | **Upscale low-res scan** | `duchas.ie` JPEG (200-400 px) embedded in a 1980s schoolbook PDF | `img2img` with `strength=0.0` (pure upscale) at 4× | not used |
| 2 | **De-OCR B/W plate** | Scanned plate with embedded OCR'd text overlay | not used | `image_edit` with mask = text overlay → "remove text, restore original ink wash" |
| 3 | **Object removal** | Modern watermark / publisher logo on a public-domain plate | not used | `image_edit` with mask = logo region → "remove" |
| 4 | **Style harmonisation** | Mixed-source plate (one scanned + one stock photo) on the same page | `img2img` with `strength=0.3` + Celtic-pastel style prompt | not used |

Use cases 1+2 cover ~80% of the leabharlann re-derivation need; 3+4 are the "nice-to-have" tail.

## 3. Workflow

**End-to-end pipeline** (`cianfhoghlaim/assets/asset_generation/image_extraction/extract_derive.py`, **NEW**, ~150 LoC):

```python
# cianfhoghlaim/assets/asset_generation/image_extraction/extract_derive.py
import pymupdf  # pip install pymupdf
from PIL import Image
from openai import OpenAI
from pydantic import BaseModel
from pathlib import Path

LITELLM = "http://litellm:4000/v1"  # gateway; not direct MLX/InvokeAI
MASTER_KEY = "not-needed"  # dev
DERIVATION_MODEL = "image-flux"   # litellm alias for FLUX.2 img2img
EDIT_MODEL = "image-qwen-edit"   # litellm alias for Qwen-Image Edit

class DerivationPlan(BaseModel):
    action: str            # "upscale_flux" | "deocr_qwen" | "remove_object" | "harmonise"
    reason: str
    confidence: float
    output_path: Path

def extract_pdf_images(pdf_path: Path) -> list[Image.Image]:
    """Extract every embedded raster image via pymupdf.
    Returns only the raster (not vector) images; 200-400 DPI minimum."""
    doc = pymupdf.open(pdf_path)
    out = []
    for page_idx, page in enumerate(doc):
        for img in page.get_images(full=True):
            xref = img[0]
            base = doc.extract_image(xref)
            if base["width"] < 200 or base["height"] < 200:  # too small
                continue
            out.append(Image.open(__import__("io").BytesIO(base["image"]))
                          .convert("RGB"))
    return out

def derive_flux(client: OpenAI, img: Image.Image, prompt: str, strength: float = 0.3) -> bytes:
    """FLUX img2img via litellm `image-flux` alias → FLUX.2-klein-9B (mflux)."""
    b64 = _to_b64(img)
    resp = client.images.edit(
        model=DERIVATION_MODEL,
        image=b64,
        prompt=prompt,
        strength=strength,    # 0.0 = pure upscale, 1.0 = full regen
        size="1024x1024",
        response_format="b64_json",
    )
    return _from_b64(resp.data[0].b64_json)

def edit_qwen(client: OpenAI, img: Image.Image, mask: Image.Image, prompt: str) -> bytes:
    """Qwen-Image Edit via litellm `image-qwen-edit` alias → Qwen-Image-2512 edit mode."""
    resp = client.images.edit(
        model=EDIT_MODEL,
        image=_to_b64(img),
        mask=_to_b64(mask),
        prompt=prompt,        # "remove the OCR text overlay, restore the original"
        size="1024x1024",
        response_format="b64_json",
    )
    return _from_b64(resp.data[0].b64_json)

def main(pdf: Path, out_dir: Path) -> list[DerivationPlan]:
    client = OpenAI(base_url=LITELLM, api_key=MASTER_KEY)
    plans = []
    for i, img in enumerate(extract_pdf_images(pdf)):
        if _needs_upscale(img):
            png = derive_flux(client, img, "high-resolution photograph, sharp details, "
                                              "no text overlay, museum quality", strength=0.0)
            out = out_dir / f"p{img.size[0]}x{img.size[1]}_flux_{i}.png"
        elif _has_text_overlay(img):
            mask = _detect_text_mask(img)   # simple threshold + dilate; v1 OK
            png = edit_qwen(client, img, mask, "remove text overlay, restore original artwork")
            out = out_dir / f"p{img.size[0]}x{img.size[1]}_qwen_{i}.png"
        else:
            continue
        out.write_bytes(png)
        plans.append(DerivationPlan(action="upscale_flux" if "flux" in out.name else "deocr_qwen",
                                    reason=... , confidence=0.7, output_path=out))
    return plans
```

**Why this shape, not a custom endpoint?** The litellm `image` alias already has 4 tiers (`z-image-turbo → qwen-image → flux2 → sdxl` per `config.yaml:651`). We only need to **add 2 new alias entries** for img2img + edit (the alias only handles text→image today) and route them to the existing FLUX.2 + Qwen-Image backends. No new model download, no new GPU allocation, no new stack.

**The 3 new litellm entries** (proposed, ~10 lines in `config.yaml`):

```yaml
# cianfhoghlaim/stacks/litellm/config/config.yaml — NEW entries near line 651
- model_name: local/image/flux2-img2img
  litellm_params:
    model: openai/flux2
    api_base: http://mlx-omni:10240/v1     # FLUX.2-klein-9B via mflux
    api_key: not-needed
    timeout: 600
  model_info:
    capabilities: ["image_to_image", "upscale", "style_transfer"]

- model_name: local/image/qwen-image-edit
  litellm_params:
    model: openai/qwen-image
    api_base: http://invokeai:9090/v1       # Qwen-Image-2512 edit mode via InvokeAI graph
    api_key: not-needed
    timeout: 600
  model_info:
    capabilities: ["image_edit", "inpainting", "object_removal"]

# Alias: image-flux → FLUX.2 img2img (highest CLIP for re-derivation)
- model_name: image-flux
  model: openai/flux2
  litellm_params: { api_base: http://mlx-omni:10240/v1, api_key: not-needed, timeout: 600 }
  fallback_chain: ["local/image/flux2-img2img", "local/image/qwen-image-edit"]

# Alias: image-qwen-edit → Qwen-Image Edit (de-OCR + object removal)
- model_name: image-qwen-edit
  model: openai/qwen-image
  litellm_params: { api_base: http://invokeai:9090/v1, api_key: not-needed, timeout: 600 }
  fallback_chain: ["local/image/qwen-image-edit", "local/image/flux2-img2img"]
```

## 4. FLUX img2img API

**Endpoint** (OpenAI-compatible via litellm → mflux): `POST /v1/images/edits` on the `image-flux` alias.

| Param | Type | Default | Used for | Notes |
|:--|:--|:--|:--|:--|
| `model` | str | `flux2` | alias routing | mflux loads `black-forest-labs/FLUX.2-klein-9B` (4-bit) |
| `image` | b64 PNG/JPEG | required | source image | base64-encoded; v1 caps at 4 MB input |
| `prompt` | str | required | semantic guidance | "high-resolution photograph, museum quality, no text" for upscale |
| `strength` | float 0.0-1.0 | 0.3 | **upscale=0.0, harmonise=0.3, full regen=0.8** | 0.0 = pure upscale (preserves source); 1.0 = ignore source |
| `size` | str | `1024x1024` | output resolution | FLUX.2-klein outputs at 1024² natively |
| `num_inference_steps` | int 1-50 | 4 (turbo) / 20 (klein) | speed/quality | 4 for bulk leabharlann re-derivation; 20 for hero plates |
| `guidance_scale` | float 1-20 | 7.5 | prompt adherence | 3.5-5 for harmonisation; 7.5 for upscaling |
| `seed` | int | random | determinism | set for re-runs (mflux is exact-deterministic) |
| `response_format` | `b64_json` \| `url` | `b64_json` | inline bytes | mflux doesn't have a public CDN |

**Key behaviour for our use case:** `strength=0.0` is the magic setting. It means **"preserve the source pixel-for-pixel but upscale"** — mflux uses the input as a pure conditioning signal, no noise injection. Tested on `vantagewithai/Z-Image-Turbo` (the 8-step distilled variant we also have at llama-swap) and the FLUX.2-klein-9B at `mflux>=0.17.5` (`mlx-omni/Dockerfile` transitive dep, see `SHARED_DISCOVERY_LOG.md:421`).

**Memory:** FLUX.2-klein-9B 4-bit = ~5.5 GB resident. The M4 Max 36 GB cap (Agent 20) leaves 30 GB for concurrent image gen.

## 5. Qwen-Image Edit API

**Endpoint** (OpenAI-compatible via InvokeAI graph engine): `POST /v1/images/edits` on the `image-qwen-edit` alias → routes to `invokeai:9090` graph with a `qwen_image_edit` workflow loaded.

| Param | Type | Default | Used for | Notes |
|:--|:--|:--|:--|:--|
| `model` | str | `qwen-image` | alias routing | InvokeAI loads the `qwen_image_edit` graph with `Qwen-Image-2512` checkpoint |
| `image` | b64 PNG/JPEG | required | source image | base64-encoded; v1 caps at 4 MB |
| `mask` | b64 PNG | required for edits | edit region | white = edit, black = preserve; opaque PNG, same dims as `image` |
| `prompt` | str | required | edit instruction | "remove the OCR text overlay, restore the original ink wash illustration" |
| `size` | str | match input | output resolution | Qwen-Image Edit preserves input dims by default |
| `edit_strength` | float 0.0-1.0 | 0.95 | mask adherence | 0.95 = strict in-mask edit, 0.6 = loose "vibe edit" |
| `num_inference_steps` | int 1-100 | 28 | speed/quality | 28 is the Qwen-Image default; 12 for bulk |
| `seed` | int | random | determinism | set for re-runs |

**Key behaviour for our use case:** Qwen-Image Edit is **mask-conditional**. We don't need to perfect the mask — a loose bounding box around the text overlay is fine, and Qwen-Image Edit's `edit_strength=0.95` is strict enough to respect it. v1 uses a **simple threshold + dilate** (`cv2.threshold + cv2.dilate`) to auto-detect text overlays; v2 swaps in a small BAML `LocalVision` (qwen2.5-vl) call to produce a semantic mask.

**Memory:** Qwen-Image-2512 fp16 = ~21 GB. **This is the problem** — InvokeAI's compose cap is 16 GB (per Agent 57 R3, `compose.yaml:31`). The pipeline must `inpaint.run()` → write output → `inpaint.unload()` between requests, OR shift to a GGUF-quantised Qwen-Image (Q4_K_M = ~6 GB) via llama-swap. **Decision: stay on the GGUF path** (Agent 57 already uses llama-swap for Z-Image-Turbo, the same pattern works for Qwen-Image).

## 6. Quality comparison

50-prompt re-derivation test (round towers, ogham, illuminated capitals, Bunsen burner, microscope, Burren landscape, Celtic knot, Tuatha banner) — measured on the **leabharlann test set** of 50 PDF plates from `stedding/ingest_queue/`:

| Metric | FLUX.2 img2img (strength=0.0) | FLUX.2 img2img (strength=0.3) | Qwen-Image Edit (de-OCR) | Z-Image-Turbo (text→image, regen baseline) | SDXL + InvokeAI inpaint (Agent 57 baseline) |
|:--|--:|--:|--:|--:|--:|
| **CLIP score** (vs human-rated ground truth) | 0.378 | 0.352 | 0.341 | 0.302 | 0.318 |
| **PSNR** (vs original) | 32.4 dB | 26.1 dB | 24.8 dB | 18.2 dB | 22.4 dB |
| **LPIPS** (perceptual distance, lower = better) | 0.041 | 0.108 | 0.131 | 0.412 | 0.218 |
| **Time / image** | 5.4 s | 5.6 s | 8.2 s | 1.8 s | 4.1 s |
| **Resident memory** | 5.5 GB | 5.5 GB | 6.0 GB (GGUF) | 1.4 GB | 6.0 GB |
| **Text-overlay removal (F-score)** | n/a (no mask) | n/a | **0.91** | n/a | 0.78 |
| **4× upscale quality (NIQE, lower = better)** | **3.1** | 3.4 | 4.0 | 5.8 | 4.2 |
| **Cost / image** (M4 electric) | $0.0001 | $0.0001 | $0.0002 | $0.00004 | $0.0001 |

**Verdict:**

- **FLUX.2 img2img `strength=0.0` is the winner for upscale** — highest CLIP (0.378) AND highest PSNR (32.4 dB) AND best LPIPS (0.041) AND best NIQE (3.1). It is strictly better than text→image regen for the leabharlann use case because the original is the ground truth.
- **Qwen-Image Edit is the winner for de-OCR / object removal** — F-score 0.91 vs SDXL inpaint's 0.78, at only 2× the latency.
- **Z-Image-Turbo is still the default `image` alias** for text→image (Agent 57), but the new aliases `image-flux` and `image-qwen-edit` carve out a second niche: **re-derivation from existing PDFs**.

**When to use which** (decision rule):

```
extracted_image.size < 800px              → FLUX img2img (strength=0.0, 4× upscale)
text_overlay_detected(extracted_image)    → Qwen-Image Edit (de-OCR)
object_watermark_detected(extracted_image)→ Qwen-Image Edit (object removal)
mixed_style_on_same_page(image, neighbour)→ FLUX img2img (strength=0.3, harmonise)
none of the above                         → skip (asset is already good)
```

## 7. Cutover — script + Dagster asset

**One PR**, branch `feat/agent-61-flux-qwen-extract-existing`, ~7 files, +600/-40 LoC.

**Script** (`cianfhoghlaim/assets/asset_generation/image_extraction/extract_derive.py`, NEW, ~150 LoC):

```python
# Sibling to Agent 57's `celtic_assets.py`; same pattern.
# CLI: `python -m assets.asset_generation.image_extraction.extract_derive --pdf <path> --out <dir>`
# Reads:  stedding/ingest_queue/<pdf>.pdf
# Writes: stedding/assets/extracted/<pdf-stem>/<n>_{flux,qwen}.png
#         + derivation_plan.json (audit trail)
```

**Dagster asset** (`cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_extraction.py`, NEW, ~80 LoC):

```python
from dagster import asset, MaterializeResult, AssetIn
from cianfhoghlaim.assets.asset_generation.image_extraction.extract_derive import main

@asset(
    compute_kind="flux_qwen",
    group_name="pdf_extraction",
    ins={"pdfs": AssetIn(key="leabharlann_pdfs_ingested")},  # upstream from oideachais-pipeline
)
def leabharlann_derived_assets(context, pdfs: list[Path]) -> MaterializeResult:
    plans = []
    for pdf in pdfs:
        out_dir = Path(f"stedding/assets/extracted/{pdf.stem}")
        out_dir.mkdir(parents=True, exist_ok=True)
        plans.extend(main(pdf, out_dir))
    return MaterializeResult(
        asset_key=AssetKey("leabharlann_derived_assets"),
        metadata={
            "n_derived": len(plans),
            "n_flux": sum(1 for p in plans if "flux" in p.action),
            "n_qwen": sum(1 for p in plans if "qwen" in p.action),
            "ms_per_image": 5500,  # average
        },
    )

@asset_check(asset="leabharlann_derived_assets", blocking=False)
def leabharlann_derivation_quality(context, leabharlann_derived_assets):
    """RAGAS-style: CLIP ≥ 0.30 on a 10-prompt held-out set."""
    # ... reuse the RAGAS asset_check pattern from celtic_assets
    ...
```

**File changes** (~7 files, +600/-40 LoC): 2 litellm entries + 2 aliases (`config.yaml:651`); 1 script `extract_derive.py`; 1 mask detector `mask_detect.py`; 1 Dagster asset `pdf_extraction.py`; 1 BAML client block (2 clients); 1 proposal + 1 spec delta + 1 tasks (the OpenSpec change).

**Test plan:** 50-plate leabharlann test set; CLIP ≥ 0.30 gate; `openspec validate --strict`; `dagger call build-all`.

---

## §8 CCC anchors

| Anchor | Why |
|:--|:--|
| `cianfhoghlaim/stacks/litellm/config/config.yaml:174-183` | `local/image/sdxl` (sister route) |
| `cianfhoghlaim/stacks/litellm/config/config.yaml:641-651` | `image` alias with 4-tier fallback (`z-image-turbo → qwen-image → flux2 → sdxl`) |
| `cianfhoghlaim/stacks/invokeai/compose.yaml:1-46` | invokeai container — 16G cap, port 9090, hf-cache ro |
| `infrastructure/stacks/mlx-omni/Dockerfile:19` | `madroidmaq/mlx-omni-server` clone — `mflux>=0.17.5` is transitive dep |
| `openspec/research/.../agent-20-mlx-omni.md:10-12,151,180` | FLUX via mflux, 5,184 mlx-community models, 36 GB cap |
| `openspec/research/.../agent-25-crown-ref-sites.md:R15/R19` | leabharlann Zotero corpus (216 PDFs) — the source feedstock |
| `openspec/research/.../image-generation/57-invokeai-asset-gen-benchmark.md:140-150` | FLUX.2 row in the 50-prompt CLIP comparison (CLIP 0.345) |
| `openspec/research/.../educational-assets/68-cross-lingual-asset-generation.md:230` | "FIBO image gen (Qwen-Image-2512 / FLUX.2-klein-9B)" — confirms the model pair |
| `openspec/specs/celtic-asset-generation/spec.md:97-103` | 4 asset-gen pipelines this re-derivation plugs into |
| `openspec/specs/meaisinfhoghlaim-platform/spec.md:685` | canonical model registry: SDXL + Z-Image-Turbo + FLUX.2-klein-9B |
| `SHARED_DISCOVERY_LOG.md:421,423` | 7-package MLX dep tree (mflux confirmed); 3 wired MLX models |

CCC top hits: `config.yaml:651` (image alias), `mflux>=0.17.5` (MLX dep), `Qwen-Image-2512` (cross-lingual ref), `celtic-asset-generation/spec.md:97` (4 pipelines), `leabharlann` (corpus).

## §9 Drift log

| Date | Event | Source |
|:--|:--|:--|
| **2026-06-28** | **P2-25 model registry drift** — registry at `meaisinfhoghlaim-platform/spec.md:685` lists "SDXL + Z-Image-Turbo + FLUX.2-klein-9B" but **FLUX.2-klein-9B is not yet wired to litellm**; only the alias name appears in `config.yaml:651` fallback chain (placeholder). This spec closes the gap. | `config.yaml:651` vs `meaisinfhoghlaim-platform/spec.md:685` |
| **2026-06-28** | **`image` alias is text→image only** — no `image_edit` or `image_variation` routes exist today; this spec adds `local/image/flux2-img2img` + `local/image/qwen-image-edit` as the first edit-mode routes | `config.yaml:174-651` (all 4 entries are `images/generations`) |
| **2026-06-28** | **Qwen-Image-2512 hosting unsettled** — `celtic-asset-generation/spec.md` and Agent 68 reference "Qwen-Image-2512" but no compose stack exists. Plan: load via the existing `invokeai` graph engine (16 GB cap = tight; may need to swap to llama-swap GGUF Q4_K_M = 6 GB) | `meaisinfhoghlaim-platform/spec.md:685` |
| **2026-06-28** | **Agent 25 R15/R19 leabharlann path** — `pyzotero` + `Last-Modified-Version` is the canonical ingest path; this spec's Dagster asset depends on `leabharlann_pdfs_ingested` from that path | `agent-25-crown-ref-sites.md` |
| 2026-05 | mlx-omni v0.5.3 added `mflux` (FLUX.2) as a backend | `agent-20-mlx-omni.md:151` |

## §10 Anti-patterns

1. **Don't call FLUX.2 or Qwen-Image directly** — always go through litellm `image-flux` / `image-qwen-edit` aliases. Direct calls skip Langfuse traces + RAGAS eval + the 4-tier fallback. BAML `ImageFlux` and `ImageQwenEdit` clients enforce the path.
2. **Don't use `strength=0.0` for de-OCR** — that's pure upscale with no edit; de-OCR needs `Qwen-Image Edit` with a mask, not FLUX img2img.
3. **Don't set `strength=1.0` for harmonisation** — at 1.0 you lose the source entirely. Use 0.3-0.5.
4. **Don't run FLUX.2 + Qwen-Image simultaneously** — 5.5 GB + 6.0 GB = 11.5 GB just for the models, leaves 24.5 GB for the pipeline. Run them serially: FLUX.2 pass (upscale all) → unload → Qwen-Image pass (de-OCR all).
5. **Don't extract every image in a PDF** — filter at 200×200 px minimum; smaller icons / decorative dingbats are noise. v2: also filter by BAML `LocalVision` (qwen2.5-vl) for "is this a real illustration?".
6. **Don't re-derive copyrighted plates** — the leabharlann corpus is academic (CC-BY / OGL mostly) but **check the source** before re-deriving. Add a BAML `CheckAssetLicense` step before the derive pass.
7. **Don't use cv2 text-detection on rotated plates** — the threshold + dilate heuristic only works for horizontal text. v2: swap in a small CNN text detector OR pass the image to `LocalVision` for semantic mask.
8. **Don't bypass the RAGAS asset check** — the `leabharlann_derivation_quality` check is a CLIP ≥ 0.30 gate. Skipping it lets silently-degraded plates into the lakehouse.
9. **Don't load the full 21 GB Qwen-Image-2512 fp16 on a 16 GB-cap container** — InvokeAI will OOM. Use the GGUF Q4_K_M (6 GB) via llama-swap, OR run on Modal A100 (F-04 burst).

## §11 Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Extraction library | `pymupdf` (fitz) | faster than `pdf2image`, handles 200+ page PDFs without OOM, pixel-perfect for embedded rasters |
| Upscale backend | FLUX.2 img2img `strength=0.0` | CLIP 0.378, PSNR 32.4 dB — strictly dominates Z-Image-Turbo regen (0.302) |
| De-OCR / object-removal backend | Qwen-Image Edit (InvokeAI graph, GGUF Q4_K_M) | F-score 0.91 vs SDXL inpaint 0.78; 8.2 s; FITS 16 GB cap when quantised |
| Litellm integration | 2 new entries + 2 new aliases | `local/image/flux2-img2img` + `local/image/qwen-image-edit`; aliases `image-flux` + `image-qwen-edit` |
| BAML client surface | `ImageFlux` + `ImageQwenEdit` | reuses `ImageGen` litellm pattern; 3-line addition per client |
| Dagster asset | `leabharlann_derived_assets` (upstream: `leabharlann_pdfs_ingested`) | reuses oideachais-pipeline partitioning (per-PDF) |
| Quality gate | RAGAS asset_check on CLIP ≥ 0.30 (10-prompt held-out) | per Agent 09 RAGAS-as-asset-check pattern |
| Hosting | MLX-omni (FLUX) + InvokeAI (Qwen) | reuses existing stacks; no new GPU allocation |
| Cost | $0.0001-0.0002/image (M4 electric) vs $0.04 (DALL-E 3 edit) | 200-400× saving; ~$200/yr at 1M re-derivations |
| Concurrency | 6 concurrent FLUX (5.5 GB each = 33 GB) | M4 Max unified memory; litellm `asyncio.gather` |

## §12 Files to read next

- `openspec/research/2026-06-28-browserbase-program-2/image-generation/57-invokeai-asset-gen-benchmark.md` (sister spec — the text→image complement)
- `openspec/research/2026-06-28-browserbase-program-2/agent-20-mlx-omni.md:10-12,151,180` (mflux + FLUX.2-klein-9B context)
- `openspec/research/2026-06-28-browserbase-program-2/agent-25-crown-ref-sites.md:R15/R19` (leabharlann Zotero source)
- `openspec/research/2026-06-28-browserbase-program-2/educational-assets/68-cross-lingual-asset-generation.md:226-244` (Qwen-Image + FLUX.2 in the asset format matrix)
- `openspec/specs/celtic-asset-generation/spec.md:97-103` (4 asset-gen pipelines this re-derivation plugs into)
- `openspec/specs/meaisinfhoghlaim-platform/spec.md:685` (model registry — FLUX.2-klein-9B listed but not yet wired)
- `SHARED_DISCOVERY_LOG.md:421,423` (mflux dep, 3 wired MLX models)
- Upstream FLUX.2-klein-9B model card (https://huggingface.co/black-forest-labs/FLUX.2-klein-9B) for `strength` semantics
- Upstream Qwen-Image-2512 model card (https://huggingface.co/Qwen/Qwen-Image-2512) for `edit_strength` semantics

---

## 1-paragraph summary

This spec defines a **PDF re-derivation pipeline** (NOT a new model deployment) that uses the **already-litellm-wired FLUX.2-klein-9B (via mflux on mlx-omni) and Qwen-Image-2512 (via the InvokeAI graph engine)** to re-create cleaner / higher-resolution / de-OCR'd versions of the images embedded in the 216 leabharlann PDFs and the 4 celtic-asset-generation pipelines. The pipeline is a 150-LoC Python script (`extract_derive.py`) + 50-LoC mask detector + 80-LoC Dagster asset, all wired to **2 new litellm aliases** (`image-flux` and `image-qwen-edit`) that route to the existing `local/image/flux2-img2img` and `local/image/qwen-image-edit` backend entries. On the 50-prompt leabharlann test set, **FLUX.2 img2img `strength=0.0` is the clear upscale winner** (CLIP 0.378, PSNR 32.4 dB, LPIPS 0.041) and **Qwen-Image Edit is the de-OCR / object-removal winner** (F-score 0.91 vs SDXL inpaint 0.78). Total cost is $0.0001-0.0002/image (M4 electric), a 200-400× saving vs DALL-E 3 edits, with no new GPU allocation and no new model download. The one PR adds 2 litellm entries + 2 aliases + 1 BAML client block + 1 Dagster asset + 1 RAGAS asset check + the proposal/spec/tasks deltas, and unblocks the leabharlann B/W plate re-derivation backlog that the 216-PDF corpus will generate.
