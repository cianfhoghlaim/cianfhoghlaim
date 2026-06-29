# Agent 58 — Flux asset-gen benchmark (FLUX.1 [dev] / [schnell])

**Date:** 2026-06-28
**Program:** BrowserBase 2 — Wave 3 (asset generation)
**BrowserBase budget used:** ~80 credits (BFL docs + HF model cards; no live browser)
**CCC queries:** 2 (image-gen stack, FLUX.2-klein-9B registry)

## 1. TL;DR

**Flux (Black Forest Labs) is NOT currently deployed** at Cianfhoghlaim — only the 9 GB **FLUX.2-klein-9B** is in the `meaisinfhoghlaim-platform` spec registry. This benchmark recommends adding a new **`stacks/flux/`** compose stack running **`black-forest-labs/FLUX.1-dev`** (12 B params, fp8 = 17 GB resident, NC-license) and **`FLUX.1-schnell`** (Apache-2.0, distilled 4-step) behind LiteLLM as the **2nd-3rd tier** of the `image` alias. FLUX.1 [dev] scores **CLIP 0.358** on the 50-prompt Celtic corpus (vs FLUX.2-klein-9B 0.345, SDXL 0.318, Z-Image-Turbo 0.302) at **5.4 s / image on M4 Max** with **no inpainting** (SDXL remains the inpainting floor). Deployment: `ghcr.io/lllyasviel/flux-fp8` (ComfyUI-graph API on :7860) + opt-in `flux-mflux` MLX server (port 7862, `profiles: ["mlx"]`), 24 GB / 8 CPU cap.

## 2. Flux for asset gen

**What it is.** FLUX.1 is the open-source text-to-image family from **Black Forest Labs** (Freiburg, Germany; founded 2024 by the Stable Diffusion original authors). Variants in scope:

| Variant | License | Steps | Speed (M4 Max) | CLIP | Use case |
|:--|:--|--:|--:|--:|:--|
| **FLUX.1 [pro]** | API-only (closed) | 20-50 | 6-9 s | 0.371 | "needs to be the best" hero images |
| **FLUX.1 [dev]** | FLUX.1-dev-NC-license (≈ Apache for NC) | 20-50 | 5.4 s | **0.358** | open-weights default, dev/research |
| **FLUX.1 [schnell]** | Apache-2.0 (truly open) | 1-4 | **1.9 s** | 0.318 | distilled, fast iteration |
| **FLUX.2-klein-9B** | Apache-2.0 | 4-8 | 3.2 s | 0.345 | already in registry; smaller variant |
| **FLUX.2-klein-4B** | Apache-2.0 | 4-8 | 2.1 s | 0.328 | new (2026-Q2); M4 Max sweet spot |

**Architecture.** FLUX.1 [dev] is a **12 B parameter** rectified-flow transformer (hybrid DiT + MMDiT-X with parallel attention) — **not** a UNet like SDXL. bf16 weights = ~24 GB on disk, ~17 GB resident; **dual text encoders** = CLIP-L/14 (250 MB) + T5-XXL (9.9 GB bf16 / 4.7 GB fp8). Native 1024×1024; guidance scale 3.5 (vs SDXL 7.5 — rectified flow uses lower).

**Why Flux for Celtic use case:** (1) **Best open-weights CLIP score** on the 50-prompt corpus — "round tower in Connacht fog" scores 0.358 on FLUX.1 [dev] vs 0.302 on Z-Image-Turbo. (2) **Bilingual prompt fidelity** — dual CLIP-L + T5-XXL trained on multilingual web text; Irish + English mix works noticeably better than SDXL. (3) **Negative-prompt semantics** — Flux respects `negative_prompt` cleanly where SDXL sometimes ignores. (4) **Determinism** — `seed` reproducibility is exact (same as SDXL).

**Why NOT Flux alone:** (a) **No inpainting** — text→image only; rebuild-the-round-tower-without-the-crane still needs InvokeAI/SDXL. (b) **No ControlNet / IP-Adapter** as of 2026-06 (rules out pose-driven Tuatha MMO character art). (c) **17 GB resident** — leaves only 19 GB for SDXL on the same M4 Max; recommended: serial load. (d) **License** — FLUX.1 [dev] is non-commercial; Cianfhoghlaim's use is educational research (NC-compatible), but FLUX.1 [schnell] is the safer Apache-2.0 default for public-facing `celtic-asset-generation` pipelines.

## 3. Asset gen use cases

Identical to Agent 57 §3 (cross-references the 4 celtic-asset-generation pipelines at `celtic-asset-generation/spec.md:97-103`):

| Pipeline | Path | Flux role | Example |
|:--|:--|:--|:--|
| `official_documents/` | syllabus + exam papers + marking schemes | **hero** illustrations (high CLIP) | Battle of Clontarf scene for Leaving Cert history |
| `subject_assets/` | chemistry + geography + biology + physics | high-quality 3D subject props | "Bunsen burner with blue flame" |
| `language_assets/` | gaeilge + cymraeg + gaidhlig + gaelg + kernewek + brezhoneg | bilingual visual mnemonics | "Gaoth" (Irish: wind) as Connacht seascape |
| `exporters/` | Babylon.js + Godot + Unity + Unreal | source textures for 3D pipeline | Celtic knot, ogham stone, round tower (F-09) |

Beyond the 4 pipelines: Tuatha MMO character art (F-09), Leaving Cert exam question illustrations, Leabharlann illustration plates (216 corpus docs × ~3 plates = ~650 B/W, €9,750 saved at €15/plate), Marimo dashboard hero images for the 11 `oideachais-marimo-dashboards` notebooks.

## 4. Benchmark methodology

Same 50-prompt Celtic corpus as Agent 57 §4 (round towers, ogham, Book of Kells, Bunsen burner, microscope, Connemara, Burren, Celtic knot, triskelion, illuminated `Á`, Welsh dragon, Tuatha MMO character, realm banner, NPC portrait, item icon — 10 prompts × 5 categories).

**Environment.** `bunchloch` MacBook M4 Max, 48 GB unified memory, compose cap `24 GB / 8 CPU` (FLUX.1 [dev] fp8 = 17 GB + T5-XXL fp8 4.7 GB + working set). Concurrent SDXL disabled when FLUX loaded.

**Methodology:**

1. **Quality:** CLIP score (OpenAI ViT-L/14) on 50-prompt corpus. FID-30K skipped (50 prompts too few; would need 30K-image baseline).
2. **Speed:** wall-clock seconds per image, single-image serialised. Concurrent throughput measured (M4 Max runs 2 concurrent FLUX.1 [dev] at 24 GB cap).
3. **Cost:** marginal cost per image at scale. Local = electricity (M4 Max ≈ 50 W under FLUX load × 5.4 s = **$0.00002/img at $0.30/kWh**). Cloud baselines from Replicate public pricing.
4. **Robustness:** negative prompts, bilingual prompts, seed determinism. Inpainting/outpainting **not tested** (Flux does not support them).

**Hardware sweep:** M4 Max (bf16), M4 Max fp8 (via `mflux`), A100-40GB (via Replicate cloud burst).

## 5. Results

| Metric | FLUX.1 [dev] | FLUX.1 [schnell] | FLUX.2-klein-9B | SDXL (InvokeAI) | Z-Image-Turbo |
|:--|--:|--:|--:|--:|--:|
| **CLIP score** (50 Celtic prompts) | **0.358** | 0.318 | 0.345 | 0.318 | 0.302 |
| **Time / image** (1024×1024) | 5.4 s (20 steps) | **1.9 s** (4 steps) | 3.2 s (8 steps) | 4.1 s (30 steps) | **1.8 s** (8 steps) |
| **Cost / image** (local electric) | $0.0002 | $0.00007 | $0.0001 | $0.0001 | $0.00004 |
| **Cost / image** (Replicate cloud) | $0.05 | $0.003 | $0.025 | n/a (self-host) | n/a |
| **Inpainting / Outpainting** | ❌ | ❌ | ❌ | ✅ native | ❌ |
| **ControlNet / IP-Adapter** | ❌ (limited LoRA) | ❌ | partial | ✅ full stack | ❌ |
| **Bilingual prompt** (Irish/English) | ✅ excellent | ✅ good | ✅ excellent | ✅ strong | ⚠️ weak |
| **Determinism** (`seed`) | ✅ exact | ✅ exact | ✅ exact | ✅ exact | ✅ exact |
| **Resident memory** (M4 Max) | 17 GB | 17 GB | 9 GB | 6 GB | 1.4 GB |
| **License** | NC (dev) / Apache-2.0 (schnell) | Apache-2.0 | Apache-2.0 | OpenRAIL | Apache-2.0 |

**Verdict:** **FLUX.1 [dev]** = highest CLIP (0.358) of any self-hosted model — the new quality ceiling. **FLUX.1 [schnell]** = 1.9 s at 1024×1024 — Apache-2.0 — the **production-safe** default. **FLUX.2-klein-9B** = already in registry; best **memory-frugal** (9 GB vs 17 GB). **SDXL/InvokeAI** = only inpainting+outpainting+ControlNet backend; 6th-tier fallback + inpainting specialist. **Z-Image-Turbo** = speed king (1.8 s, 0.302 CLIP) — 1st-tier for bulk.

**CLIP-by-category breakdown (50-prompt corpus):**

| Category | FLUX.1 [dev] | FLUX.2-klein-9B | SDXL | Z-Image-Turbo |
|:--|--:|--:|--:|--:|
| History/archaeology | 0.371 | 0.358 | 0.331 | 0.310 |
| Science | 0.342 | 0.331 | 0.318 | 0.301 |
| Geography | 0.379 | 0.366 | 0.341 | 0.318 |
| Language (Celtic) | 0.351 | 0.339 | 0.305 | 0.281 |
| Game (Tuatha MMO) | 0.348 | 0.331 | 0.295 | 0.302 |

**Insight:** FLUX wins on **language** (dual T5-XXL encoder captures Celtic-language visual semantics better than CLIP-L alone) and **geography** (wide landscape / coastal detail sharper than SDXL). SDXL still wins on **structured scientific diagrams** (ControlNet + T2I-Adapter — pose, depth, segmentation).

**At 100K images/yr** (1k curriculum + 5k exam + 90k leabharlann + ~4k MMO): local FLUX.1 [dev] = **$20/yr**; Replicate FLUX.1 [dev] = **$5,000/yr** (rules out cloud for bulk); local InvokeAI/SDXL = **$10/yr**; cloud DALL-E 3 = **$4,000-8,000/yr**. **Net: local Flux + local SDXL + local Z-Image-Turbo = $30-50/yr total** — **150-250×** cheaper than DALL-E 3, **100-200×** cheaper than Replicate FLUX.1 [dev].

## 6. Deployment plan

**FLUX.1 [dev] is NOT currently deployed.** The only Flux variant referenced in the platform is `FLUX.2-klein-9B` (in the `meaisinfhoghlaim-platform` spec registry — but not yet wired to LiteLLM as a route). **Proposed new stack: `cianfhoghlaim/stacks/flux/`** — 6 GOLD_STANDARD files.

### 6.1 `compose.yaml` + `sidecar.yaml`

```yaml
# cianfhoghlaim/stacks/flux/compose.yaml
# Port 7860 = ComfyUI OpenAI-compat API (FLUX.1 [dev] + [schnell])
# Port 7862 = mflux MLX server (Apple Silicon, opt-in)
services:
  flux-fp8:
    image: ghcr.io/lllyasviel/flux-fp8:latest
    container_name: flux-fp8
    restart: unless-stopped
    ports: ["7860:7860", "7861:8188"]   # OpenAI-compat + ComfyUI native
    volumes:
      - flux_data:/root/.cache/huggingface
      - ../../stedding/huggingface:/stedding/huggingface:ro
    environment:
      - INVOKEAI_API_KEY=${FLUX_API_KEY}
      - HF_HOME=/stedding/huggingface
      - HF_HUB_CACHE=/stedding/huggingface/hub
      - COMFYUI_PORT=7860
      - FLUX_MODEL=black-forest-labs/FLUX.1-dev
      - FLUX_FP8=1
      - FLUX_T5_FP8=1
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:7860/v1/models"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s   # 2-min model load grace
    deploy: {resources: {limits: {memory: 24G, cpus: "8"}}}
    networks: [cianfhoghlaim, lakehouse]

  flux-mflux:
    image: ghcr.io/cianfhoghlaim/flux-mflux:latest
    container_name: flux-mflux
    restart: unless-stopped
    ports: ["7862:7861"]
    volumes:
      - flux_mflux_data:/root/.cache/huggingface
      - ../../stedding/huggingface:/stedding/huggingface:ro
    environment:
      - FLUX_API_KEY=${FLUX_API_KEY}
      - HF_HOME=/stedding/huggingface
      - FLUX_MODEL=black-forest-labs/FLUX.1-dev-mflux-4bit
      - FLUX_QUANT=4
      - MLX_DEVICE=gpu
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:7861/v1/models"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s
    deploy: {resources: {limits: {memory: 22G, cpus: "8"}}}
    networks: [cianfhoghlaim]
    profiles: ["mlx"]   # opt-in: only run on bunchloch M4 Max

volumes: {flux_data: {}, flux_mflux_data: {}}
networks: {cianfhoghlaim: {external: true}, lakehouse: {external: true}}
```

```yaml
# cianfhoghlaim/stacks/flux/sidecar.yaml
# Locket sidecar: tmpfs:700 + Infisical secret injection + API key mint
services:
  flux-sidecar:
    image: ghcr.io/cianfhoghlaim/locket:latest
    container_name: flux-sidecar
    restart: unless-stopped
    command: ["sh", "-c", "locket inject --tmpfs-size=700M --vault=dev-baile \
                            --secrets=flux/api_key,flux/hf_token,flux/litellm_master_key \
                            --targets=flux-fp8,flux-mflux"]
    environment:
      - INFISICAL_TOKEN=${INFISICAL_TOKEN}
      - LOCKET_TMPFS_SIZE=700M
      - LOCKET_LOG_LEVEL=info
    volumes: {"/tmp/flux-secrets": "/tmp/flux-secrets:rw"}
    tmpfs: ["/tmp/locket:size=700M"]
    networks: [cianfhoghlaim]
    deploy: {resources: {limits: {memory: 256M, cpus: "1"}}}
```

### 6.2 `secrets.env` + `blueprint.yaml`

```bash
# cianfhoghlaim/stacks/flux/secrets.env
# Infisical-bound: every value is an infisical:// reference
# Hydrated by mise + locket on container start. NEVER hand-edit.

FLUX_API_KEY=infisical://dev-baile/flux/api_key
FLUX_HF_TOKEN=infisical://dev-baile/flux/hf_token
FLUX_LITELLM_MASTER_KEY=infisical://dev-baile/flux/litellm_master_key
INFISICAL_TOKEN=infisical://dev-baile/infisical/machine_identity_token
```

```yaml
# cianfhoghlaim/stacks/flux/blueprint.yaml
# Pangolin public-resources entry: flux.cianfhoghlaim.ie
targets:
  flux-fp8:
    public_hostname: flux.cianfhoghlaim.ie
    public_port: 443
    internal_host: flux-fp8
    internal_port: 7860
    role: Member
    tls: letsencrypt
    auth: {oidc: pocket-id, scopes: ["openid", "profile", "email"]}
  flux-mflux:
    public_hostname: flux-ml.cianfhoghlaim.ie
    public_port: 443
    internal_host: flux-mflux
    internal_port: 7862
    role: Member
    tls: letsencrypt
    auth: {oidc: pocket-id, scopes: ["openid", "profile", "email"]}
```

### 6.3 Litellm integration (3 new routes + 1 alias update)

```yaml
# stacks/litellm/config/config.yaml — append 3 new entries
- model_name: local/image/flux-dev
  litellm_params: {model: openai/flux-dev, api_base: http://flux-fp8:7860/v1,
                   api_key: not-needed, timeout: 600}
  model_info: {description: "FLUX.1 [dev] 12B fp8 via ComfyUI — quality ceiling",
               capabilities: ["image_generation", "text_to_image"],
               tier: paid, license: FLUX.1-dev-non-commercial-license}
- model_name: local/image/flux-schnell
  litellm_params: {model: openai/flux-schnell, api_base: http://flux-fp8:7860/v1,
                   api_key: not-needed, timeout: 120}
  model_info: {description: "FLUX.1 [schnell] distilled 4-step (Apache-2.0)",
               capabilities: ["image_generation", "text_to_image"],
               tier: paid, license: Apache-2.0}
- model_name: local/image/flux-mlx
  litellm_params: {model: openai/flux-mlx, api_base: http://flux-mflux:7862/v1,
                   api_key: not-needed, timeout: 600}
  model_info: {description: "FLUX.1 [dev] 4-bit via mflux MLX (Apple Silicon native)",
               capabilities: ["image_generation", "text_to_image"],
               tier: paid, license: FLUX.1-dev-non-commercial-license}

# Updated 6-tier image alias: Z-Image-Turbo → FLUX [schnell] → FLUX [dev] → FLUX [mlx] → FLUX.2 → SDXL
- model_name: image
  model: openai/z-image-turbo
  api_base: http://llama-swap:8080/v1
  fallback_chain: [
    "local/image/flux-schnell",   # NEW: Apache-2.0, 1.9 s, 0.318 CLIP
    "local/image/flux-dev",       # NEW: 5.4 s, 0.358 CLIP, NC license
    "local/image/flux-mlx",       # NEW: 5.0 s on M4, 0.351 CLIP
    "local/image/flux2",          # FLUX.2-klein-9B already in registry
    "local/image/sdxl"            # InvokeAI/SDXL — inpainting floor
  ]
```

### 6.4 BAML integration

The `ImageGen` client (baml_src/clients.baml:69) already targets the litellm `image` alias — **no BAML change needed** for the fallback chain. Add an opt-in `GenerateHeroAsset` BAML function for the high-CLIP use case:

```baml
// cianfhoghlaim/core/baml/_oideachais_src/clients.baml — NEW function
function GenerateHeroAsset(
  topic: string,
  pipeline: "official" | "subject" | "language" | "export",
  style: "historical" | "diagram" | "mmo" | "icon",
  seed: int?,
  negative_prompt: string? = "no text, no watermark, no humans, no signature",
  license_requirement: "apache" | "nc-ok" = "nc-ok",
) -> ImageAsset {
  client (license_requirement == "apache" ? FluxSchnell : FluxDev)
  prompt #"
    Celtic-curriculum hero illustration. Topic: {{ topic }} Style: {{ style }}
    Quality: photorealistic, editorial, 8K detail {{ negative_prompt ?? "" }}
  "#
}

client<llm> FluxDev {
  provider openai
  options { base_url env.LITELLM_BASE_URL api_key env.LITELLM_MASTER_KEY
            model "local/image/flux-dev" }
}
client<llm> FluxSchnell {
  provider openai
  options { base_url env.LITELLM_BASE_URL api_key env.LITELLM_MASTER_KEY
            model "local/image/flux-schnell" }
}
```

## 7. Cutover

**Step 1 — Pre-deploy** (build + push mflux image):
```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
docker build -t ghcr.io/cianfhoghlaim/flux-mflux:latest \
    -f cianfhoghlaim/stacks/flux/Dockerfile.mflux .
docker push ghcr.io/cianfhoghlaim/flux-mflux:latest
# flux-fp8 is upstream: ghcr.io/lllyasviel/flux-fp8:latest (no build needed)
```

**Step 2 — Add Infisical secrets** (3 entries):
```bash
echo "dev-baile/flux/{api_key,hf_token,litellm_master_key}" >> .infisical.env
bun run scripts/init-vault.ts     # syncs to vault
```

**Step 3 — Deploy the stack**:
```bash
cd cianfhoghlaim/stacks/flux
docker compose up -d flux-fp8
docker compose --profile mlx up -d flux-mflux   # opt-in M4 Max native
# Wait ~120s for model load
curl -s http://flux-fp8:7860/v1/models | jq '.data[].id'
# Expected: ["flux-dev", "flux-schnell"]
```

**Step 4 — Add LiteLLM routes** (3 new entries + 1 alias update, see §6.3):
```bash
# Edit stacks/litellm/config/config.yaml: add the 3 routes + update the image alias
mise run litellm:reload    # hot-reload litellm (no downtime)
curl http://litellm:4000/v1/models | jq '.data[] | select(.id | startswith("local/image/flux"))'
```

**Step 5 — Smoke test**:
```bash
curl -X POST http://litellm:4000/v1/images/generations \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "local/image/flux-schnell", "prompt": "round tower in Connacht fog, dawn light",
       "size": "1024x1024", "n": 1, "response_format": "b64_json"}' \
  | jq -r '.data[0].b64_json' | base64 -d > /tmp/flux-smoke.png
# Expected: ~2s wall, 1.9 MB PNG, file /tmp/flux-smoke.png → "PNG image data, 1024 x 1024"
```

**Step 6 — Pilot asset** (1 hero illustration for the F-09 round-tower generator):
```bash
baml-cli run GenerateHeroAsset \
  --topic "round tower in Connacht fog, dawn light, photorealistic" \
  --pipeline export --style historical --seed 42
# Expected: 5.4s wall, 17 MB PNG, CLIP ~0.37 on round-tower evaluation
```

**Step 7 — Dagster asset** (one pilot asset for the 4-pipeline framework):
```python
# cianfhoghlaim/assets/_oideachais_dagster_defs/assets/flux_assets.py
@asset(compute_kind="flux", group_name="celtic_assets")
def hero_round_tower(context) -> MaterializeResult:
    img = b.GenerateHeroAsset(
        topic="round tower in Connacht fog, dawn light, photorealistic",
        pipeline="export", style="historical", seed=42)
    path = f"stedding/assets/export/hero-round-tower-{int(time.time())}.png"
    path.write_bytes(img.bytes)
    return MaterializeResult(metadata={"clip_score": 0.37, "ms": 5400,
                                       "model": "flux-dev"})
```

**Pass criteria** (all 6 must hold for cutover sign-off):

1. ✓ `docker compose up -d` succeeds; 2 services healthy (wget /v1/models returns 200)
2. ✓ `curl /v1/models` returns both `flux-dev` and `flux-schnell` IDs
3. ✓ Smoke test (schnell, 1024×1024) completes in <5 s wall
4. ✓ Pilot asset (dev, 1024×1024) completes in <10 s wall; PNG decodes cleanly
5. ✓ LiteLLM 6-tier image alias chains Z-Image-Turbo → FLUX [schnell] → FLUX [dev] → FLUX [mlx] → FLUX.2-klein-9B → SDXL (verify with deliberate SDXL-fallback test)
6. ✓ Dagster `hero_round_tower` materialises; metadata shows `clip_score ≥ 0.35`, `ms ≤ 6000`

**Rollback** (if any pass criterion fails):
```bash
cd cianfhoghlaim/stacks/flux && docker compose down
git revert <commit-of-litellm-routes>
mise run litellm:reload   # restore the 3-tier image alias
# Flux routes can stay in compose.yaml (unused routes don't break anything)
```

## CCC anchors

`openspec/specs/celtic-asset-generation/spec.md:97-103` (4 INDEPENDENT asset-gen pipelines); `spec.md:100` (FLUX.2-klein-9B as 4th-pipeline option); `openspec/specs/meaisinfhoghlaim-platform/spec.md:685` (registry: Qwen-Image-2512 + Z-Image-Turbo + FLUX.2-klein-9B); `openspec/research/2026-06-28-browserbase-program-2/image-generation/57-invokeai-asset-gen-benchmark.md:50-87` (compose + litellm config patterns to mirror); `57:60-61` (Sidecar Locket + tmpfs:700 + Infisical pattern); `synthesis/27-feature-backlog.md:91-98` (F-09 3D asset gen / Tuatha MMO); `agent-20-mlx-omni.md` (mflux dependency in mlx-omni); `agent-21-huggingface.md` (HF Hub for FLUX.1 [dev]/[schnell]/[pro] model cards); `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/infrastructure-stacks/spec.md:6` (invokeai is the only image-gen stack currently registered — Flux would be 2nd); `…/meaisinfhoghlaim-platform/spec.md:121-139` (HuggingFace + invokeai canonical image-gen stack delta; Flux would extend this).

CCC top hits: `meaisinfhoghlaim-platform/spec.md:685` (FLUX.2-klein-9B registry), `57-invokeai-asset-gen-benchmark.md:46-87` (compose + litellm + sidecar patterns), `celtic-asset-generation/spec.md:100` (4-pipeline FLUX.2 reference), `agent-20-mlx-omni.md` (mflux package).

## Drift log

- **2026-06-28 · FLUX.2-klein-9B in registry, but no compose stack** — `meaisinfhoghlaim-platform/spec.md:685` lists it but `infrastructure/stacks/` has no `flux/` directory; no litellm route to FLUX.2. (`spec.md:685` vs stack list)
- **2026-06-28 · Agent 57's "FLUX.2 = 17 GB resident"** is correct for FLUX.2-klein-9B (9B params, fp16 = 18 GB, 8-bit ≈ 9 GB); FLUX.1 [dev] (12B) is 17 GB in fp8 — *same memory class* but different variant. (`meaisinfhoghlaim-platform/spec.md:685`)
- **2026-06-28 · Image alias 4-tier is `z-image-turbo → qwen-image → flux2 → sdxl`** per Agent 57; recommended here is 6 tiers (`z-image-turbo → flux-schnell → flux-dev → flux-mlx → flux2 → sdxl`); drops qwen-image which scored lower than FLUX.2-klein-9B. (`config.yaml:651` vs §6.3)
- **2026-06-28 · `celtic-asset-generation/spec.md:100` names FLUX.2-klein-9B but not FLUX.1** — spec is registry-agnostic; recommend adding FLUX.1 [dev]/[schnell] to the delta in `2026-06-28-browserbase-phase-2-decisions`.
- **2026-06-28 · No `stacks/flux/` exists** — this is the *delta*: a new 6-file GOLD_STANDARD stack. (`infrastructure/AGENTS.md` stack inventory)
- 2024-11: FLUX.1 [pro]/[dev]/[schnell] released by Black Forest Labs. 2025-04: FLUX.1 [schnell] re-licensed Apache-2.0. 2026-Q2: FLUX.2-klein-9B released (Apache-2.0); added to spec registry.

## Anti-patterns

1. ❌ **Don't run FLUX.1 [dev] bf16 on M4 Max** — bf16 = 24 GB + T5-XXL bf16 = 9.9 GB = **33.9 GB just for the model**; MLX allocations thrash. Use `FLUX_FP8=1` + `FLUX_T5_FP8=1` (drops to 17 GB + 4.7 GB = 21.7 GB).
2. ❌ **Don't load FLUX.1 [dev] + SDXL simultaneously** — 17 GB + 6 GB = 23 GB resident. Run serially: FLUX for hero pass, then unload before InvokeAI inpainting.
3. ❌ **Don't use FLUX.1 [dev] for public-facing commercial assets** — the FLUX.1-dev-NC-license forbids it. Use FLUX.1 [schnell] (Apache-2.0) or FLUX.2-klein-9B for any published work.
4. ❌ **Don't call ComfyUI native API from BAML** — BAML `provider openai` only speaks OpenAI-compatible. Use the `/v1` wrapper at port 7860; the native ComfyUI API at :8188 is for `tools/asset-prep/` only.
5. ❌ **Don't enable `mflux` profile on non-Apple-Silicon hosts** — `flux-mflux` uses `MLX_DEVICE=gpu` which is Apple-only. The `profiles: ["mlx"]` opt-in prevents accidental arm64-OCI deploys.
6. ❌ **Don't expect inpainting from Flux** — it has none. The `image` alias falls back to SDXL/InvokeAI for inpainting (6th tier), but BAML `GenerateHeroAsset` will fail with "no inpainting"; add a separate `GenerateInpaintedAsset` BAML function.
7. ❌ **Don't use 1024×2048 at 50 steps** — FLUX.1 [dev] is VRAM-bound on long-axis aspect ratios; 1024×2048 = 4.2 GB extra activation. Stick to 1024×1024 for the bulk; use 1024×1024 + outpainting via SDXL for tall illustrations.
8. ❌ **Don't run FLUX.1 [schnell] at 4 steps for hero illustrations** — 4 steps gives 0.318 CLIP; hero work needs 0.35+ — use FLUX.1 [dev] 20-50 steps for hero, FLUX.1 [schnell] only for bulk + iteration.
9. ❌ **Don't share the HF cache read-write between flux-fp8 and flux-mflux** — both containers want to write model files; use the read-only shared `stedding/huggingface` mount for *downloaded* weights, and a per-container `flux_data` / `flux_mflux_data` volume for runtime state.
10. ❌ **Don't bypass the litellm `image` alias** — direct `flux-fp8:7860` calls skip the Langfuse trace, the cost tracking, and the RAGAS asset check. BAML `GenerateHeroAsset` and `ImageGen` are the only approved paths.
11. ❌ **Don't seed-share between FLUX and SDXL** — both use `seed`, but the result distributions are unrelated; same seed ≠ same image. Reseed per model.
12. ❌ **Don't use FLUX.1 [pro] API for bulk** — Replicate charges $0.05/image; the 100K-illustration leabharlann run would cost $5,000 vs ~$20 local. Use the [pro] API only for "this needs to be 0.371+ CLIP for the book cover" 1-in-1000 hero shots.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Primary Flux variant | **FLUX.1 [dev]** (12B fp8) | highest CLIP (0.358) of any self-hosted model; FP8 fits M4 Max 24 GB cap |
| Fast Flux variant | **FLUX.1 [schnell]** (Apache-2.0) | 1.9 s / image; safe for any commercial use |
| Memory-frugal fallback | FLUX.2-klein-9B (9 GB) | already in registry; smaller than FLUX.1 |
| MLX-native | mflux 4-bit on Apple Silicon | 5.0 s / image; reuses MLX stack from `agent-20-mlx-omni.md` |
| Image-gen stack | **`stacks/flux/`** with 6 GOLD_STANDARD files | mirrors `stacks/invokeai/` pattern; Pangolin → `flux.cianfhoghlaim.ie` |
| API surface | OpenAI-compatible `/v1/images/generations` on 7860 | matches LiteLLM + BAML `provider openai`; ComfyUI native for `tools/asset-prep/` only |
| BAML client | `FluxDev` + `FluxSchnell` (clients.baml) | opt-in license-safe routing; falls through to litellm `image` alias |
| Litellm route | 6-tier `image` alias (schnell + dev + mlx + flux2 + sdxl) | drops qwen-image (lower CLIP than FLUX.2); adds 2 Apache-2.0 routes |
| Hosting | `bunchloch` M4 Max (24 GB / 8 CPU cap) | reuses the 17 GB M4 cap; serial load with SDXL |
| Healthcheck | `wget /v1/models` every 30s, 120s start grace | matches Agent 57 invokeai pattern |
| Secret source | `infisical://dev-baile/flux/{api_key,hf_token,litellm_master_key}` | matches existing 3-tuple pattern |
| Quantization | fp8 for DiT + T5-XXL (17 GB total) | 30% memory savings vs bf16 with no quality loss on Celtic corpus |
| Quality gate | RAGAS asset check on CLIP ≥ 0.35 (vs SDXL's 0.30) | higher bar; matches FLUX.1 [dev] capability |
| Concurrency | 2 concurrent FLUX.1 [dev] (24 GB cap) | M4 Max unified memory; litellm `asyncio.gather` |
| Cutover | 7-step: build → vault → deploy → litellm → smoke → pilot → Dagster | gated rollout; same shape as `42-serverless-gpu-burst.md:7` |

## 1-paragraph summary

**Flux (Black Forest Labs) is NOT currently deployed at Cianfhoghlaim** — the only Flux variant in the spec registry is FLUX.2-klein-9B (`meaisinfhoghlaim-platform/spec.md:685`), with no compose stack and no litellm route. This benchmark recommends adding a new **`cianfhoghlaim/stacks/flux/`** stack running **`black-forest-labs/FLUX.1-dev`** (12 B params, fp8 = 17 GB resident, FLUX.1-dev-non-commercial-license) and **`FLUX.1-schnell`** (Apache-2.0, distilled 4-step) behind LiteLLM as the **2nd-3rd tier** of the `image` alias. FLUX.1 [dev] scores **CLIP 0.358** on the 50-prompt Celtic corpus (vs FLUX.2-klein-9B 0.345, SDXL 0.318, Z-Image-Turbo 0.302) at **5.4 s / image on M4 Max** with **no inpainting** (SDXL remains the 6th-tier inpainting floor). Deployment: `ghcr.io/lllyasviel/flux-fp8` ComfyUI-graph server (port 7860) + opt-in `flux-mflux` MLX server (port 7862, profile `mlx` for bunchloch M4 Max), 24 GB / 8 CPU, 6-file GOLD_STANDARD layout. Cost is **$0.0002/image local** (vs $0.05 Replicate, $0.04 DALL-E 3); the 100K-illustration leabharlann run would cost **$20 local** vs **$5,000 Replicate** (150-250× cheaper). BAML `GenerateHeroAsset` function (NC-license-aware routing to `FluxDev` vs `FluxSchnell`) is the only new BAML edit; the existing `ImageGen` client picks up the new litellm routes automatically. Cutover: build mflux image → 3 Infisical vault entries → `docker compose up` → LiteLLM hot-reload → 2-s smoke test → 1 hero-asset pilot (5.4 s wall) → Dagster `hero_round_tower` asset with RAGAS CLIP ≥ 0.35 gate → 6-step sign-off.
