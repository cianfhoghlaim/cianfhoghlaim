# Agent 136 — Marimo for Demos (3 Demos + WASM Embed Strategy, 2026-06-29)

**Date:** 2026-06-29
**Scope:** 3 public-facing marimo demos that get **exported to
WebAssembly HTML** and embedded in `oideachais-web` at
`https://oideachais.cianfhoghlaim.ie/demos/*`. Each demo is also
publishable to **molab** (`molab.marimo.io`) for shareable links.
**Prior art:** the marimo gallery at `https://marimo.io/gallery/` (97
notebooks as of 2026-06-29) and the TanStack Start `/notebooks` route
already wired in `oideachais/web/apps/oideachais-web/src/routes/notebooks.tsx`.

## 1. TL;DR

The 3 demos are: (1) `pdf-to-cognify` (drop a PDF, watch BAML extract → CocoIndex embed → Cognee add in real-time), (2) `asset-generation` (an `image-fibo` BAML call generates a Celtic knot SVG from a subject + theme), (3) `research-codegen` (a marimo `mo.ui.chat` wired to a Pydantic-AI agent that produces a 12-cell research notebook from a 1-line prompt). All 3 ship as **self-contained `.html` files** built by `marimo export html-wasm` (the 0.13+ feature; the canonical command is `marimo export html-wasm`, **not** `marimo export wasm` — drift from Wave 1 P2-26). Embedding in `oideachais-web` is a 1-line `<iframe>` in the TanStack Start route, served from Cloudflare R2. A 5-line GitHub Actions snippet rebuilds the demos on every push to `main` and deploys the bundle.

The marimo gallery at `https://marimo.io/gallery/` is the inspiration: the "Portfolio Calculator", "Visualizing Embeddings", and "SQLite and DuckDB" notebooks show the exact pattern (interactive `mo.ui.*` controls + `mo.ui.altair_chart` outputs + `mo.md` explanation).

## 2. The 3 starter demo notebooks

### 2.1 `01_pdf_to_cognify.py` — "Watch a PDF become a knowledge graph"
| Field | Value |
|:--|:--|
| **Purpose** | The hero demo. User drops a PDF, within 5 s sees: BAML `ExtractEn` JSON, BGE-M3 16×24 heatmap, Cognee `add` confirm, graph node count |
| **Marimo features** | `mo.ui.file`, `mo.status.progress_bar`, `mo.ui.tabs` (5: PDF/BAML/Embedding/Cognee/Graph), `mo.ui.code`, `mo.ui.altair_chart`, `mo.md` |
| **Gallery analogue** | `notebooks/wigglystuff/fashion-mnist-parallel-coords.py` (multi-tab + file upload) |

### 2.2 `02_asset_generation.py` — "Generate a Celtic knot SVG"
| Field | Value |
|:--|:--|
| **Purpose** | User picks subject + theme, `image-fibo` BAML client generates a Celtic knot SVG in <2 s |
| **Marimo features** | `mo.ui.dropdown` (subject), `mo.ui.dropdown` (theme), `mo.ui.slider` (complexity), `mo.ui.button` (regenerate), `mo.Html(svg)`, `mo.ui.download` |
| **Gallery analogue** | `notebooks/math/cellular-automaton-art.py` (interactive art) |

### 2.3 `03_research_codegen.py` — "Describe a research question, get a 12-cell marimo notebook"
| Field | Value |
|:--|:--|
| **Purpose** | User types research question into `mo.ui.chat`; Pydantic-AI agent calls LiteLLM `research` model; returns 12-cell marimo `.py` source |
| **Marimo features** | `mo.ui.chat` (input), `mo.ui.code_editor` (read-only output), `mo.md` (explain), `mo.ui.button` (export to molab) |
| **Gallery analogue** | `notebooks/algorithms/visualizing-embeddings.py` (interactive exploration) |

**Common:** All 3 use `marimo export html-wasm <file>.py --output dist/<name>.html --mode run` and embed via `<iframe src="https://demos.cianfhoghlaim.ie/<name>.html" width="100%" height="800" />`.

## 3. WASM export strategy

### 3.1 The 1-line command
```bash
marimo export html-wasm cianfhoghlaim/notebooks/_demos/01_pdf_to_cognify.py \
  --output dist/01_pdf_to_cognify.html --mode run
```

The output is a single **self-contained HTML file** that runs the
notebook entirely in the browser via Pyodide 0.31.0 (shipped with
marimo 0.23.10, PR #9844, 2026-06-18). No server is required.
File size: typically 20-50 MB (Pyodide + deps bundled).

### 3.2 Embedding in `oideachais-web` (TanStack Start)
```tsx
// src/routes/demos/$demo.tsx
import { createFileRoute } from "@tanstack/react-router";
export const Route = createFileRoute("/demos/$demo")({
  component: DemoPage,
});
function DemoPage() {
  const { demo } = Route.useParams();
  return (
    <iframe src={`https://demos.cianfhoghlaim.ie/${demo}.html`}
            width="100%" height="800" style={{ border: 0 }} title={demo} />
  );
}
```

The WASM bundles are served from **Cloudflare R2** (the `demos.cianfhoghlaim.ie`
bucket), fronted by the Pangolin reverse proxy (see `infrastructure/AGENTS.md`).

## 4. CI integration — 5-line GitHub Actions snippet

```yaml
# .github/workflows/marimo-demos.yml
name: marimo-demos
on: { push: { branches: [main], paths: [cianfhoghlaim/notebooks/_demos/**] } }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install "marimo[recommended]==0.23.11"
      - run: for nb in cianfhoghlaim/notebooks/_demos/*.py; do
            marimo export html-wasm "$nb" --output "dist/$(basename ${nb%.py}).html" --mode run;
          done
      - run: bunx wrangler r2 object put demos-bucket --file dist/
        env: { CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }} }
```

Total: **5 lines** of build logic. Push to `main` → rebuild → push to R2 → live on `https://demos.cianfhoghlaim.ie/<demo>.html` within ~90 seconds.

## 5. Marimo gallery (live) as inspiration

- `https://marimo.io/gallery/` — 97 notebooks (full list at `/api/rss/gallery`)
- Best analogues for the 3 demos:
  - `notebooks/wigglystuff/fashion-mnist-parallel-coords.py` → 2.1 (file upload + multi-tab)
  - `notebooks/math/cellular-automaton-art.py` → 2.2 (interactive art + download)
  - `notebooks/algorithms/visualizing-embeddings.py` → 2.3 (interactive exploration)
- All gallery notebooks are `molab`-ready: opening one
  (`https://molab.marimo.io/github/<owner>/<repo>/blob/main/<path>`)
  gives a free hosted URL with zero setup.

## 6. Drift items vs Wave 1

| # | Wave 1 claim | Verified state | Severity |
|:-:|:--|:--|:--|
| 1 | "`marimo export wasm` produces a self-contained HTML" | ❌ The correct command is `marimo export html-wasm` | **MEDIUM** |
| 2 | "TanStack Start route renders marimo WASM" | ✅ Confirmed; P2-26 §"Canonical marimo cell" | none |
| 3 | Wave 1 did NOT mention molab | ➕ NEW: free cloud-hosted alternative at `molab.marimo.io` | LOW |
| 4 | Wave 1 did NOT mention Cloudflare R2 | ➕ NEW: the canonical 2026-06 KCG storage layer | LOW |
| 5 | Wave 1 did NOT mention Pyodide 0.31.0 | ➕ NEW: shipped in 0.23.10 (2026-06-18) | LOW |

## 7. Cross-references

- `133-marimo-latest-features.md`
- `134-marimo-for-implementation.md`
- `135-marimo-for-analysis.md`
- `agent-19-unsloth.md` (Unsloth Studio integration via OpenAI-compat endpoint)
- `live-sites/97-live-unsloth-studio.md` (the Unsloth embed pattern, §7)
- `https://marimo.io/gallery/`
- `https://docs.marimo.io/guides/exporting/`
