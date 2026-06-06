# docs/old/ — Merge Plan

**Date:** 2026-06-06  
**Status:** PLAN — awaiting execution approval

## Current State

### Subdirectories

| Directory | Size | Contents | Action |
|---|---|---|---|
| `_archive/` | 61M | 2,433 files — legacy codebases (dspy, crypteolas, misc code) | **DO NOT TOUCH** — archival |
| `papers/` | 92M | 13 PDFs + 1 README.md — academic papers | **DO NOT TOUCH** — research corpus |
| `taighde_new/` | 268K | 15 `.md` files — consolidation reference | **FLATTEN TO ROOT** |

### Paper Inventory (`papers/`)

13 PDFs, all academic research on Irish language, education, ML:

| File | Topic |
|---|---|
| `update-to-the-comprehensive-linguistic-study-on-the-usage-of-irish-in-the-gaeltacht-20.pdf` | Gaeltacht language use (updated) |
| `Linguistic-Study-of-the-Use-of-Irish-in-the-Gaeltacht.pdf` | Gaeltacht language use (original) |
| `Irish-BLiMP_A_Linguistic_Benchmark_for_Evaluating_.pdf` | Irish grammatical benchmark |
| `gramadoirnua.pdf` | Gramadóir Nua — Irish grammar tool |
| `lrec2020.pdf` | LREC 2020 — Irish NLP |
| `7618_Learning_to_Generate_Styl.pdf` | Learning to Generate Stylized Text |
| `2511.06876v1.pdf` | ArXiv paper (Nov 2025) |
| `2510.20957v1.pdf` | ArXiv paper (Oct 2025) |
| `2510.17652v1.pdf` | ArXiv paper (Oct 2025) |
| `2504.02890v2.pdf` | ArXiv paper (Apr 2025) |
| `1765814974-bolmo.pdf` | BolMo model paper |
| `1766008501-molmo2-tech-report.pdf` | MolMo-2 technical report |
| `263826_e7b1c18f-cef2-4235-8d2e-26c6681507e4.pdf` | Academic paper |

### taighde_new/ Inventory (15 `.md` files)

All files were read in full on 2026-06-06.

| File | Lines | Topic | Consolidation Ready? |
|---|---|---|---|
| `INDEX.md` | 27 | Master index of all consolidated research | Yes — keep as root index |
| `RESEARCH_CONSOLIDATION_PLAN.md` | 35 | Original consolidation strategy | Archive after flatten |
| `KCG_SUMMARY.md` | 22 | Summary of consolidation actions | Archive after flatten |
| `bilingual-datasets.md` | 903 | Irish-English datasets (Gaois, TMX, APIs) | Yes — core research |
| `celtic-language-ai-ml.md` | 550 | HuggingFace models for Irish/Welsh/Gaelic/Manx | Yes — core research |
| `data-pipeline-architecture.md` | 685 | BAML + dlt + Dagster pipeline patterns | Yes — core research |
| `document-intelligence-ocr.md` | 473 | VLM vs OCR, ColPali, Gaelic heritage pipeline | Yes — core research |
| `document-intelligence-vlm.md` | 28 | Theme analysis: VLM + OCR comparison | Merge into ocr file |
| `educational-game-development.md` | 687 | Physics/chemistry simulations, game engines, Manim | Yes — core research |
| `geospatial-linguistics.md` | 1413 | DuckDB Spatial, MapLibre, census mapping | Yes — core research |
| `infrastructure-devops.md` | 756 | Dagger, Komodo, Pangolin, 1Password | Yes — core research |
| `infrastructure-knowledge-graph.md` | 31 | Theme analysis: infra + DuckLake + EdTech backend layers | Merge into knowledge-graph file |
| `irish-edtech-platform.md` | 848 | Full EdTech platform architecture (consolidated) | Yes — core research |
| `knowledge-graph-infrastructure.md` | 936 | Graphiti, Cognee, FalkorDB, Memgraph dual-engine | Yes — core research |
| `web-scraping-automation.md` | 655 | Patchright, Skyvern, Crawl4AI, Gaois APIs | Yes — core research |

## Merge Plan

### Step 1: Flatten taighde_new/ to docs/old/ root

Move all 15 `.md` files from `docs/old/taighde_new/` up to `docs/old/`:

```bash
mv docs/old/taighde_new/*.md docs/old/
rmdir docs/old/taighde_new/
```

**Result:** docs/old/ becomes flat with 3 categories visible:
- `docs/old/*.md` — 15 research documents (formerly taighde_new)
- `docs/old/_archive/` — preserved (61M of legacy code)
- `docs/old/papers/` — preserved (92M of academic PDFs)

### Step 2 (Optional): Deduplicate Theme Analysis Files

Two files are thin "theme analysis" wrappers that could be merged into their parent documents:

| Merge Source | Into | Reason |
|---|---|---|
| `document-intelligence-vlm.md` (28 lines) | `document-intelligence-ocr.md` (473 lines) | Same topic; thin analysis wrapper |
| `infrastructure-knowledge-graph.md` (31 lines) | `knowledge-graph-infrastructure.md` (936 lines) | Same topic; thin analysis wrapper |

**Recommendation:** Keep as-is for now. These are lightweight and serve as "bridge documents" documenting the consolidation thought process. Can be archived later.

### Step 3: Archive Process Docs

Two files document the consolidation process itself and can be archived:

| File | Action |
|---|---|
| `RESEARCH_CONSOLIDATION_PLAN.md` | Move to `_archive/` |
| `KCG_SUMMARY.md` | Move to `_archive/` |

Keep `INDEX.md` at root as the canonical index.

## Post-Merge Structure

```
docs/old/
├── INDEX.md                              ← Master research index
├── bilingual-datasets.md                  ← Core research
├── celtic-language-ai-ml.md              ← Core research
├── data-pipeline-architecture.md          ← Core research
├── document-intelligence-ocr.md           ← Core research
├── document-intelligence-vlm.md           ← Thin analysis (keep or merge)
├── educational-game-development.md        ← Core research
├── geospatial-linguistics.md              ← Core research
├── infrastructure-devops.md               ← Core research
├── infrastructure-knowledge-graph.md      ← Thin analysis (keep or merge)
├── irish-edtech-platform.md               ← Core research
├── knowledge-graph-infrastructure.md      ← Core research
├── web-scraping-automation.md             ← Core research
├── _archive/                              ← PRESERVED (61M)
│   └── (2,433 legacy files: dspy, crypteolas, misc)
├── papers/                                ← PRESERVED (92M)
│   ├── README.md
│   └── (13 academic PDFs)
├── RESEARCH_CONSOLIDATION_PLAN.md         ← To archive
└── KCG_SUMMARY.md                         ← To archive
```

## Risks & Notes

1. **No file conflicts** — The 15 taighde_new/ files have no name collisions with existing docs/old/ files (which currently contains only directories).
2. **`_archive/` is 61M** — 2,433 files, mostly Python (dspy) and misc code. Not touched.
3. **`papers/` is 92M** — 13 PDF academic papers. Not touched.
4. **taighde_new/ is 268K** — Trivial to move. No binary files.

## Execution

To execute this plan:

```bash
# Step 1: Flatten
mv docs/old/taighde_new/*.md docs/old/
rmdir docs/old/taighde_new/

# Step 2: Archive process docs
mv docs/old/RESEARCH_CONSOLIDATION_PLAN.md docs/old/_archive/
mv docs/old/KCG_SUMMARY.md docs/old/_archive/

# Step 3: Verify
ls docs/old/*.md | wc -l    # Should be 13 (15 original minus 2 archived)
```

**Result:** `docs/old/` becomes a flat directory with 13 `.md` research files plus 2 preserved subdirectories (`_archive/`, `papers/`).
