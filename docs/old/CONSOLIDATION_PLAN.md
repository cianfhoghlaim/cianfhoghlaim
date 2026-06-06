# Research Directory Consolidation Plan

**Created**: 2025-12-30
**Status**: Ready for execution

## Decisions Made

| Question              | Decision                                             |
| --------------------- | ---------------------------------------------------- |
| Anam project location | `taighde/game/anam/`                                 |
| taighde_new retention | Keep in place (option A)                             |
| PDFs location         | Central `taighde/papers/` (option B)                 |
| bonneagar archive     | Separate in `taighde/_archive/bonneagar/` (option B) |

---

## Summary

| Directory                | Size  | Action                        | Space Saved |
| ------------------------ | ----- | ----------------------------- | ----------- |
| taighde_scoil            | 1.3GB | DELETE clones, ARCHIVE rest   | ~1.29GB     |
| taighde_crypteolas_tuath | 855MB | DELETE clones, MIGRATE unique | ~800MB      |
| taighde_meaisínfhoghlaim | 118MB | MIGRATE all                   | 0 (moved)   |
| taighde_teanga           | 35MB  | MIGRATE all                   | 0 (moved)   |
| taighde_bonneagar        | 2.0MB | ARCHIVE                       | 0 (moved)   |
| taighde_old              | 9.2MB | ARCHIVE                       | 0 (moved)   |
| taighde_new              | 272KB | KEEP                          | 0           |

**Total space recovery**: ~2.1GB

---

## Execution Script

Run from `/Users/cliste/dev/cianfhoghlaim`:

```bash
#!/bin/bash
set -e

echo "=== Phase 1: Backup ==="
tar -czvf /tmp/taighde_old_backup_$(date +%Y%m%d).tar.gz taighde/old/
echo "Backup created at /tmp/taighde_old_backup_$(date +%Y%m%d).tar.gz"

echo "=== Phase 2: Create target directories ==="
mkdir -p taighde/_archive/{scoil/{indexing,rill,docs},crypteolas/{raw,tuath_old},old,bonneagar}
mkdir -p taighde/teanga/{irish,welsh,scottish,datasets,handwriting,ocr}
mkdir -p taighde/papers
mkdir -p taighde/game/anam/{chef,design,tokenomics,gdext}
mkdir -p taighde/web/{agentic,frameworks}
mkdir -p taighde/infrastructure/{crypto,cloudflare}
mkdir -p meaisínfhoghlaim/training/{utils,open-instruct,phone/docs}
mkdir -p meaisínfhoghlaim/notebooks/{archive,unsloth/docs,vlm/docs}

echo "=== Phase 3: Delete cloned repositories (2.1GB) ==="
rm -rf taighde/old/taighde_scoil/three.js
rm -rf taighde/old/taighde_scoil/Babylon.js
rm -rf taighde/old/taighde_crypteolas_tuath/convex
rm -rf taighde/old/taighde_crypteolas_tuath/x402
rm -rf taighde/old/taighde_crypteolas_tuath/AP2
rm -rf taighde/old/taighde_crypteolas_tuath/vibesdk
rm -rf taighde/old/taighde_crypteolas_tuath/inspector
find taighde/old -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
echo "Cloned repos deleted"

echo "=== Phase 4: Migrate ML research ==="
# GGUF converter
cp taighde/old/taighde_meaisínfhoghlaim/convert_hf_to_gguf.py meaisínfhoghlaim/training/utils/
# Open-instruct fork
cp -r taighde/old/taighde_meaisínfhoghlaim/open-instruct/* meaisínfhoghlaim/training/open-instruct/ 2>/dev/null || true
# Notebooks
cp taighde/old/taighde_meaisínfhoghlaim/*.ipynb meaisínfhoghlaim/notebooks/archive/ 2>/dev/null || true
# Unsloth docs
cp taighde/old/taighde_meaisínfhoghlaim/*Unsloth*.md meaisínfhoghlaim/notebooks/unsloth/docs/ 2>/dev/null || true
# VLM/OCR docs
cp taighde/old/taighde_meaisínfhoghlaim/*VLM*.md meaisínfhoghlaim/notebooks/vlm/docs/ 2>/dev/null || true
cp taighde/old/taighde_meaisínfhoghlaim/*OCR*.md meaisínfhoghlaim/notebooks/vlm/docs/ 2>/dev/null || true
# Phone deployment
cp taighde/old/taighde_meaisínfhoghlaim/*Phone*.md meaisínfhoghlaim/training/phone/docs/ 2>/dev/null || true
cp taighde/old/taighde_meaisínfhoghlaim/*iPhone*.md meaisínfhoghlaim/training/phone/docs/ 2>/dev/null || true
cp taighde/old/taighde_meaisínfhoghlaim/*iOS*.md meaisínfhoghlaim/training/phone/docs/ 2>/dev/null || true
# Analysis docs
cp taighde/old/taighde_meaisínfhoghlaim/ANALYSIS_SUMMARY.md meaisínfhoghlaim/ 2>/dev/null || true
cp taighde/old/taighde_meaisínfhoghlaim/README_ANALYSIS.md meaisínfhoghlaim/ 2>/dev/null || true
cp taighde/old/taighde_meaisínfhoghlaim/QUICK_REFERENCE.md meaisínfhoghlaim/ 2>/dev/null || true
echo "ML research migrated"

echo "=== Phase 5: Migrate Celtic language resources ==="
# Master resource file
cp taighde/old/taighde_teanga/CELTIC_LANGUAGES_AI_RESOURCES.md taighde/teanga/RESOURCES.md
# Irish resources
cp taighde/old/taighde_teanga/irish_gaeilge_huggingface_resources.md taighde/teanga/irish/
cp taighde/old/taighde_teanga/gaeilge.md taighde/teanga/irish/ 2>/dev/null || true
# Welsh resources
cp taighde/old/taighde_teanga/welsh-huggingface-resources.md taighde/teanga/welsh/
# Scottish Gaelic resources
cp taighde/old/taighde_teanga/scottish_gaelic_huggingface_resources.md taighde/teanga/scottish/
# Datasets
cp taighde/old/taighde_teanga/irish_bilingual_dataset_research.md taighde/teanga/datasets/
cp taighde/old/taighde_teanga/british_isles_parallel_data_sources.md taighde/teanga/datasets/
cp taighde/old/taighde_teanga/BritLLM.md taighde/teanga/datasets/ 2>/dev/null || true
# Handwriting
cp taighde/old/taighde_teanga/*[Hh]andwriting*.md taighde/teanga/handwriting/ 2>/dev/null || true
# OCR
cp taighde/old/taighde_teanga/*OCR*.md taighde/teanga/ocr/ 2>/dev/null || true
cp taighde/old/taighde_teanga/*Qwen*VL*.md taighde/teanga/ocr/ 2>/dev/null || true
# Geospatial (to geoai)
cp taighde/old/taighde_teanga/*[Gg]eospatial*.md taighde/geoai/ 2>/dev/null || true
cp taighde/old/taighde_teanga/*British*Isles*.md taighde/geoai/ 2>/dev/null || true
echo "Celtic resources migrated"

echo "=== Phase 6: Migrate PDFs to central location ==="
cp taighde/old/taighde_meaisínfhoghlaim/*.pdf taighde/papers/ 2>/dev/null || true
cp taighde/old/taighde_teanga/*.pdf taighde/papers/ 2>/dev/null || true
cp taighde/old/taighde_crypteolas_tuath/*.pdf taighde/papers/ 2>/dev/null || true
echo "PDFs migrated to taighde/papers/"

echo "=== Phase 7: Migrate Anam project ==="
cp -r taighde/old/taighde_crypteolas_tuath/chef taighde/game/anam/
cp -r taighde/old/taighde_crypteolas_tuath/game-design taighde/game/anam/design 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/tokenomics taighde/game/anam/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/gdext taighde/game/anam/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/smart-contracts taighde/game/anam/ 2>/dev/null || true
echo "Anam project migrated"

echo "=== Phase 8: Migrate web/infra research ==="
# Frontend/agentic
cp -r taighde/old/taighde_crypteolas_tuath/frontend/* taighde/web/agentic/ 2>/dev/null || true
# Backend frameworks
cp -r taighde/old/taighde_crypteolas_tuath/hono taighde/web/frameworks/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/orpc taighde/web/frameworks/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/restate taighde/web/frameworks/ 2>/dev/null || true
# Infrastructure
cp -r taighde/old/taighde_crypteolas_tuath/infrastructure/* taighde/infrastructure/crypto/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/cloudflare/* taighde/infrastructure/cloudflare/ 2>/dev/null || true
# DuckDB research
cp -r taighde/old/taighde_crypteolas_tuath/duckdb/* taighde/ducklake/ 2>/dev/null || true
# BAML schemas
cp -r taighde/old/taighde_crypteolas_tuath/baml/* taighde/baml/ 2>/dev/null || true
# Data pipeline
cp -r taighde/old/taighde_crypteolas_tuath/data-pipeline/* taighde/data-pipeline/ 2>/dev/null || true
echo "Web/infra research migrated"

echo "=== Phase 9: Archive remaining content ==="
# Archive scoil
cp -r taighde/old/taighde_scoil/indexing/* taighde/_archive/scoil/indexing/ 2>/dev/null || true
cp -r taighde/old/taighde_scoil/rill-github-analytics/* taighde/_archive/scoil/rill/ 2>/dev/null || true
cp -r taighde/old/taighde_scoil/00-overview/* taighde/_archive/scoil/docs/ 2>/dev/null || true

# Archive crypteolas remnants
cp -r taighde/old/taighde_crypteolas_tuath/crypteolas_old/* taighde/_archive/crypteolas/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/tuath_old/* taighde/_archive/crypteolas/tuath_old/ 2>/dev/null || true
cp -r taighde/old/taighde_crypteolas_tuath/raw/* taighde/_archive/crypteolas/raw/ 2>/dev/null || true
cp taighde/old/taighde_crypteolas_tuath/*.md taighde/_archive/crypteolas/ 2>/dev/null || true
cp taighde/old/taighde_crypteolas_tuath/*.jpeg taighde/_archive/crypteolas/ 2>/dev/null || true
cp taighde/old/taighde_crypteolas_tuath/*.webp taighde/_archive/crypteolas/ 2>/dev/null || true

# Archive taighde_old
cp -r taighde/old/taighde_old/* taighde/_archive/old/ 2>/dev/null || true

# Archive bonneagar (separate per user request)
cp -r taighde/old/taighde_bonneagar/* taighde/_archive/bonneagar/ 2>/dev/null || true

echo "Archives created"

echo "=== Phase 10: Create archive README ==="
cat > taighde/_archive/README.md << 'ARCHIVEREADME'
# Research Archive

**Archived**: 2025-12-30
**Source**: `taighde/old/taighde_*` directories

## Contents

| Directory | Original Source | Description |
|-----------|-----------------|-------------|
| `scoil/` | taighde_scoil | Educational scraping research (ChunkHound, Rill) |
| `crypteolas/` | taighde_crypteolas_tuath | Crypto/game research (pre-Anam consolidation) |
| `old/` | taighde_old | Original 6-category research structure |
| `bonneagar/` | taighde_bonneagar | Infrastructure research (Ansible, Komodo) |

## Migration Summary

### Migrated (Active Use)
- Celtic AI resources → `taighde/teanga/`
- ML training utilities → `meaisínfhoghlaim/training/`
- Anam game project → `taighde/game/anam/`
- Research papers → `taighde/papers/`
- Web frameworks → `taighde/web/`

### Deleted (Cloned Repos)
- three.js (610MB)
- Babylon.js (710MB)
- Convex (565MB)
- x402 protocol (218MB)
- Various SDK clones (~15MB)

**Total space recovered**: ~2.1GB

## Access Policy

These files are preserved for **historical reference only**.
Active development should use the main project directories.

## Reference

The consolidation index remains at:
`taighde/old/taighde_new/INDEX.md`
ARCHIVEREADME

echo "=== Phase 11: Create papers README ==="
cat > taighde/papers/README.md << 'PAPERSREADME'
# Research Papers

Academic papers referenced during project development.

## Categories

| File Pattern | Topic |
|--------------|-------|
| `*_Learning_*` | Machine learning papers |
| `*ocr*`, `*vlm*` | Document intelligence |
| `*celtic*`, `*irish*` | Celtic language AI |
| `*molmo*`, `*bolmo*` | Vision-language models |

## Source

Migrated from:
- `taighde/old/taighde_meaisínfhoghlaim/`
- `taighde/old/taighde_teanga/`
- `taighde/old/taighde_crypteolas_tuath/`

## Note

These PDFs are typically available on arXiv if re-download is needed.
PAPERSREADME

echo "=== Phase 12: Cleanup ==="
# Remove empty directories
find taighde/old -type d -empty -delete 2>/dev/null || true

# Remove .DS_Store files
find taighde/old -name ".DS_Store" -delete 2>/dev/null || true

echo "=== Verification ==="
echo ""
echo "Space after cleanup:"
du -sh taighde/old/
echo ""
echo "Key migrations verified:"
test -f taighde/teanga/RESOURCES.md && echo "✓ Celtic resources"
test -f meaisínfhoghlaim/training/utils/convert_hf_to_gguf.py && echo "✓ GGUF converter"
test -d taighde/game/anam/chef && echo "✓ Anam project"
test -d taighde/papers && echo "✓ Papers directory"
test -f taighde/_archive/README.md && echo "✓ Archive index"
echo ""
echo "=== CONSOLIDATION COMPLETE ==="
```

---

## Post-Execution

### Final Directory Structure

```
taighde/
├── _archive/                    # Historical reference
│   ├── README.md
│   ├── scoil/
│   ├── crypteolas/
│   ├── old/
│   └── bonneagar/
├── papers/                      # Central research papers
├── teanga/                      # Celtic language AI
│   ├── RESOURCES.md            # Master catalog
│   ├── irish/
│   ├── welsh/
│   ├── scottish/
│   ├── datasets/
│   ├── handwriting/
│   └── ocr/
├── game/
│   └── anam/                   # Anam project
│       ├── chef/
│       ├── design/
│       ├── tokenomics/
│       └── gdext/
├── web/
│   ├── agentic/
│   └── frameworks/
├── old/
│   └── taighde_new/            # Consolidation reference (kept)
└── [existing active dirs...]

meaisínfhoghlaim/
├── training/
│   ├── utils/
│   │   └── convert_hf_to_gguf.py
│   ├── open-instruct/
│   └── phone/docs/
├── notebooks/
│   ├── archive/
│   ├── unsloth/docs/
│   └── vlm/docs/
├── ANALYSIS_SUMMARY.md
└── [existing...]
```

### Optional: Remove Original Directories

After verifying the migration, you can delete the now-empty source directories:

```bash
# Only run after verification!
rm -rf taighde/old/taighde_scoil
rm -rf taighde/old/taighde_crypteolas_tuath
rm -rf taighde/old/taighde_meaisínfhoghlaim
rm -rf taighde/old/taighde_teanga
rm -rf taighde/old/taighde_bonneagar
rm -rf taighde/old/taighde_old
# Keep taighde_new as consolidation reference
```
