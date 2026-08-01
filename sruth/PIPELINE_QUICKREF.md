# Pipeline Quick Reference Cards

## 1. OIDEACHAS (Irish Education Curriculum)

### Entry Point
```bash
cd sruth/oideachais
uv run dagster dev -m dagster_defs.definitions
```

### Key Files
| File | Purpose | Debug Command |
|------|---------|---------------|
| `dagster_defs/definitions.py` | Main definitions | `uv run python -c "from dagster_defs import defs; print(defs.assets)"` |
| `dagster_defs/assets/ireland/curriculum_dlt_assets.py` | Ireland curriculum | `uv run python -c "from dagster_defs.assets.ireland import curriculum_dlt_assets; print(curriculum_dlt_assets)"` |
| `dagster_defs/assets/pdf_assets.py` | PDF processing | `uv run python -c "from dagster_defs.assets.pdf_assets import pdf_processing_assets; print(pdf_processing_assets)"` |
| `cocoindex_flows/pdf_embedding.py` | Embedding flow | Check flow definition structure |

### Asset Hierarchy
```
ireland/curriculum/
├── early_childhood/        (Aistear, Siolta)
├── primary/                (8 subjects)
├── junior_cycle/           (18 subjects × 2 languages)
├── senior_cycle/           (33 subjects × 2 languages)
└── short_courses/          (8 courses × 2 languages)

ireland/curriculum/pdf_downloads/
ireland/curriculum/pdf_extracted_text/
```

### Test Single Asset
```python
from dagster import materialize
from dagster_defs.assets.ireland import curriculum_dlt_assets

# Materialize Junior Cycle Mathematics
result = materialize(
    assets=[curriculum_dlt_assets[2]],  # junior_cycle asset
    partition_value="junior_cycle|mathematics|en",
)
```

---

## 2. CRYPTEOLAS (GitHub + DeFi Data)

### Entry Point
```bash
cd sruth/crypteolas
uv run dagster dev -m dagster_assets.definitions
```

### Key Files
| File | Purpose | Debug Command |
|------|---------|---------------|
| `dagster_assets/definitions.py` | Main definitions | `uv run python -c "from dagster_assets import defs; print(defs.assets)"` |
| `dagster_assets/github_assets.py` | GitHub data | Check repos, issues, PRs assets |
| `dagster_assets/defi_assets.py` | DeFi protocols | Check TVL, yields assets |
| `dlt_sources/github/github_source.py` | GitHub DLT source | Test REST endpoint |
| `cocoindex_flows/code_embedding.py` | Code embeddings | Check CodeBERT integration |

### Asset Hierarchy
```
crypteolas/github/
├── repos/                 (by owner/repo)
├── issues/                (by repository)
├── pulls/                 (by repository)
└── commits/               (by repository)

crypteolas/defi/
├── protocols/             (by protocol, chain)
├── tvl/                   (time series)
└── yields/                (by protocol)

crypteolas/embeddings/
├── code/                  (CodeBERT 768-dim)
└── documents/             (BGE-M3 1024-dim)
```

### Test GitHub Source
```python
import dlt
from dlt_sources.github.github_source import github_source

pipeline = dlt.pipeline(
    pipeline_name="github_test",
    destination="duckdb",
    dataset_name="github",
)

info = pipeline.run(
    github_source(
        repos=["dagster-io/dagster"],
        include_issues=True,
    )
)
```

---

## 3. ALEYUM (Music Web Scraping)

### Entry Point
```bash
cd sruth/aleyum
uv run dagster dev -m dagster_assets.definitions
```

### Key Files
| File | Purpose | Debug Command |
|------|---------|---------------|
| `dagster_assets/definitions.py` | Main definitions | `uv run python -c "from dagster_assets import defs; print(defs.assets)"` |
| `dagster_assets/dlt_assets.py` | DLT wrappers | Check Spotify/SoundCloud assets |
| `pipelines/spotify/source.py` | Spotify API | Test REST endpoint |
| `pipelines/soundcloud/scraper.py` | SoundCloud scraper | Test browser scraping |
| `cocoindex_flows/artwork_embedding.py` | CLIP embeddings | Check image pipeline |

### Asset Hierarchy
```
aleyum/spotify/
├── tracks/                (by playlist/album)
├── albums/                (by artist)
└── artists/               (by genre)

aleyum/soundcloud/
├── tracks/                (by artist)
└── metadata/              (artist info)

aleyum/artwork/
├── downloaded/            (S3: music-artwork bucket)
├── processed/             (thumbnails, color extraction)
└── embeddings/            (CLIP 768-dim)
```

### Test Browser Scraping
```python
from sruth.browser.sruth_browser.backends import get_backend
import asyncio

async def test_scraping():
    backend = await get_backend("stagehand")
    result = await backend.scrape(
        url="https://soundcloud.com/test-artist",
        instruction="Extract track titles and artwork URLs"
    )
    print(result)

asyncio.run(test_scraping())
```

---

## Component-Based Assets (New - Incomplete)

### Current State
```python
# Component YAML files exist but aren't parsed yet
# sruth/oideachais/dagster_defs/components/pdf_pipeline_component.yaml
# sruth/crypteolas/dagster_assets/components/rest_pipeline_component.yaml
# sruth/aleyum/dagster_assets/components/scraping_pipeline_component.yaml

# Component loaders return placeholder AssetSpecs
from sruth.oideachais.dagster_defs.components import load_oideachais_components
defs = load_oideachais_components()
# Returns: Definitions(asset_specs=[...])  # NO EXECUTABLE ASSETS
```

### To Make Components Work
1. Implement YAML parsing in component loaders
2. Generate `@asset` functions from component specs
3. Add component assets to main definitions

---

## Quick Debug Commands

```bash
# Check all assets in a pipeline
check_assets() {
    local pipeline=$1
    cd "sruth/$pipeline"
    uv run python -c "
from dagster_assets.definitions import defs
print(f'Total assets: {len(defs.assets)}')
for i, asset in enumerate(defs.assets[:10]):
    print(f'{i+1}. {asset.key.to_user_string()}')
"
}

# Usage:
check_assets oideachais
check_assets crypteolas
check_assets aleyum

# Test a single DLT source
test_dlt_source() {
    local pipeline=$1
    local source=$2
    cd "sruth/$pipeline"
    uv run python -c "
import dlt
from dlt_sources.$source import ${source}_source
info = dlt.pipeline(
    pipeline_name='test',
    destination='duckdb',
).run(${source}_source())
print(info)
"
}

# Test Dagster definitions load
test_definitions() {
    local pipeline=$1
    cd "sruth/$pipeline"
    uv run python -m dagster_definitions check
}
```

---

## Storage Backend Testing

```bash
# Test all storage backends
cat > test_storage.sh << 'EOF'
#!/bin/bash
echo "=== DuckDB ==="
uv run python -c "import duckdb; conn = duckdb.connect(':memory:'); print(conn.execute('SELECT 1').fetchall())"

echo "=== Lakekeeper ==="
curl -s $LAKEKEEPER_CATALOG_URI/v1/namespaces | jq .

echo "=== MotherDuck ==="
uv run python -c "from motherduck import connect; md = connect(); print(md.list_databases())"

echo "=== LanceDB ==="
uv run python -c "import lancedb; db = lancedb.connect('./lancedb'); print(db.table_names())"

echo "=== FalkorDB ==="
uv run python -c "from falkordb import Graph; graph = Graph(); print(graph.query('RETURN 1'))"
EOF

chmod +x test_storage.sh
./test_storage.sh
```

---

## Environment Variables Checklist

```bash
# Create a comprehensive .env file
cat > sruth/.env.example << 'EOF'
# Lakekeeper (Iceberg REST Catalog)
LAKEKEEPER_CATALOG_URI=http://lakekeeper:8181
ICEBERG_WAREHOUSE=s3://garage/warehouse

# Garage/R2 Storage
GARAGE_ENDPOINT_URL=http://garage:3900
GARAGE_ACCESS_KEY=minioadmin
GARAGE_SECRET_KEY=minioadmin

# MotherDuck
MOTHERDUCK_TOKEN=md_*
MOTHERDUCK_DATABASE=sruth

# Firecrawl
FIRECRAWL_API_KEY=fc-*

# OpenAI (for DSPy)
OPENAI_API_KEY=sk-*
OPENAI_MODEL=gpt-4o

# HuggingFace (for embeddings)
HF_TOKEN=hf_*
EMBEDDING_MODEL=BAAI/bge-m3
CODE_EMBEDDING_MODEL=microsoft/codebert-base
CLIP_MODEL=openai/clip-vit-large-patch14

# Langfuse (observability)
LANGFUSE_PUBLIC_KEY=pk-*
LANGFUSE_SECRET_KEY=sk-*

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# PostgreSQL (PlanetScale or local)
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/sruth

# LanceDB
LANCEDB_URI=s3://lance
LANCEDB_S3_BUCKET=lance

# FalkorDB
FALKORDB_URI=redis://localhost:6379
EOF
```
