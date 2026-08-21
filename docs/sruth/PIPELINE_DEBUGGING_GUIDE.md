# Sruth Pipeline Debugging & Research Guide

## Current Status Assessment

### ✅ What's Working (Existing Implementation)
- `sruth/oideachais/dagster_defs/definitions.py` - Fully functional Dagster assets
- `sruth/oideachais/dagster_defs/assets/` - Working DLT assets for all nations
- `sruth/oideachais/dagster_defs/assets/pdf_assets.py` - PDF processing

### ⚠️ What's Incomplete (New Component Approach)
- Component loaders return placeholder `AssetSpec` definitions
- YAML configs exist but aren't parsed/executed
- No actual Dagster `@asset` functions created from components

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OIDEACHAS PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. SOURCE LAYER                                                            │
│     ├─ NCCA Curriculum Online (Firecrawl)                                   │
│     ├─ SEC Exam Papers (Firecrawl)                                          │
│     └─ Gov.ie Circulars (Firecrawl)                                         │
│                                                                             │
│  2. DLT EXTRACTION (@dlt_assets)                                            │
│     ├─ curriculum_dlt_assets → ireland/curriculum/{cycle}                   │
│     ├─ wales_curriculum_dlt_assets → wales/curriculum/{key_stage}           │
│     └─ scotland_curriculum_dlt_assets → scotland/curriculum/{level}         │
│                                                                             │
│  3. PDF PROCESSING                                                           │
│     ├─ pdf_downloads_asset → Downloads PDFs to S3                           │
│     └─ pdf_extracted_text_asset → OCR extraction (Docling/PaddleOCR)        │
│                                                                             │
│  4. EMBEDDINGS (CocoIndex flows)                                            │
│     └─ pdf_embedding.py → BGE-M3 embeddings → LanceDB                       │
│                                                                             │
│  5. STORAGE                                                                 │
│     ├─ DuckLake (PostgreSQL + S3) via Lakekeeper                            │
│     ├─ DuckDB (fallback/local)                                              │
│     └─ LanceDB (vector search)                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Debugging Walkthrough

### Phase 1: Environment Setup

```bash
# 1. Navigate to oideachais
cd sruth/oideachais

# 2. Create/copy environment file
cp .env.example .env

# 3. Edit .env with your credentials
# Required variables:
#   - LAKEKEEPER_CATALOG_URI=http://lakekeeper:8181
#   - ICEBERG_WAREHOUSE=s3://garage/warehouse
#   - GARAGE_ENDPOINT_URL=http://garage:3900
#   - GARAGE_ACCESS_KEY=...
#   - GARAGE_SECRET_KEY=...
#   - FIRECRAWL_API_KEY=...
#   - OPENAI_API_KEY=... (for DSPy extraction)

# 4. Verify environment
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required = ['LAKEKEEPER_CATALOG_URI', 'ICEBERG_WAREHOUSE', 'FIRECRAWL_API_KEY']
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f'Missing: {missing}')
else:
    print('All required env vars set')
"
```

### Phase 2: Test Dagster Definitions

```bash
# 1. Verify Dagster can load definitions
uv run python -c "
from dagster_defs import defs
print(f'Loaded {len(defs.assets)} assets')
print(f'Loaded {len(defs.jobs)} jobs')
print(f'Loaded {len(defs.schedules)} schedules')
for asset in defs.assets[:5]:
    print(f'  - {asset.key.to_user_string()}')
"

# 2. Start Dagster UI
DAGSTER_HOME=.dagster uv run dagster dev -m dagster_defs.definitions

# 3. Open http://localhost:3000
# Navigate to Assets → ireland → curriculum
```

### Phase 3: Test Individual Assets

```bash
# Create a test script for debugging individual assets
cat > debug_asset_materialization.py << 'EOF'
"""Debug script for materializing individual assets."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

from dagster import materialize
from dagster_defs.assets.ireland import curriculum_dlt_assets

# Test materializing a single partition
result = materialize(
    assets=[curriculum_dlt_assets[0]],  # First asset
    partition_value="junior_cycle|mathematics|en",
)

print(f"Success: {result.success}")
for event in result:
    if event.event_type_value == "asset_materialization":
        print(f"Materialized: {event.asset_key}")
EOF

# Run the debug script
uv run python debug_asset_materialization.py
```

### Phase 4: Test DLT Pipeline Directly

```bash
# Test DLT pipeline without Dagster
cat > debug_dlt_pipeline.py << 'EOF'
"""Debug DLT pipeline directly."""
import dlt
from dlt.sources.helpers import requests

# Simple DLT pipeline test
def test_dlt_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="test_curriculum",
        destination="duckdb",
        dataset_name="test",
    )

    # Simple REST source
    @dlt.resource(name="test_data")
    def test_resource():
        yield [
            {"id": 1, "name": "Test Document", "content": "Test content"},
            {"id": 2, "name": "Another Doc", "content": "More content"},
        ]

    # Run pipeline
    info = pipeline.run(test_resource)
    print(f"Pipeline run: {info}")

if __name__ == "__main__":
    test_dlt_pipeline()
EOF

uv run python debug_dlt_pipeline.py
```

### Phase 5: Test PDF Processing

```bash
# Test PDF download and OCR
cat > debug_pdf_processing.py << 'EOF'
"""Debug PDF processing pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from dagster import materialize
from dagster_defs.assets.pdf_assets import (
    pdf_downloads_asset,
    pdf_extracted_text_asset,
)

# Test with a small sample
result = materialize(
    assets=[pdf_downloads_asset],
    partition_key="junior_cycle|mathematics",
)

print(f"Download result: {result.success}")

# Then test extraction
result2 = materialize(
    assets=[pdf_extracted_text_asset],
    partition_key="junior_cycle|mathematics",
)

print(f"Extraction result: {result2.success}")
EOF

uv run python debug_pdf_processing.py
```

### Phase 6: Test Storage Backends

```bash
# Test DuckLake connection
cat > debug_storage.py << 'EOF'
"""Debug storage backends."""
import os
from dotenv import load_dotenv

load_dotenv()

# Test DuckDB
print("Testing DuckDB...")
import duckdb
conn = duckdb.connect(":memory:")
conn.execute("SELECT 1 as test")
print(f"DuckDB: {conn.fetchall()}")

# Test Lakekeeper
print("\nTesting Lakekeeper...")
from sruth.shared.storage.lakekeeper_client import LakekeeperClient
client = LakekeeperClient(
    uri=os.getenv("LAKEKEEPER_CATALOG_URI", "http://localhost:8181"),
    warehouse="test"
)
namespaces = client.list_namespaces()
print(f"Lakekeeper namespaces: {namespaces}")

# Test MotherDuck
print("\nTesting MotherDuck...")
if os.getenv("MOTHERDUCK_TOKEN"):
    import motherduck
    md = motherduck.connect(token=os.getenv("MOTHERDUCK_TOKEN"))
    print(f"MotherDuck databases: {md.list_databases()}")

# Test LanceDB
print("\nTesting LanceDB...")
from sruth.shared.storage.lance_namespace import LanceNamespaceManager
lance_mgr = LanceNamespaceManager()
print(f"Lance namespaces: {lance_mgr.EDUCATION_NAMESPACES}")
EOF

uv run python debug_storage.py
```

### Phase 7: Test Embedding Generation

```bash
# Test embedding pipeline
cat > debug_embeddings.py << 'EOF'
"""Debug embedding generation."""
import os
from dotenv import load_dotenv

load_dotenv()

from sentence_transformers import SentenceTransformer
import numpy as np

# Test BGE-M3 model
print("Loading BGE-M3 model...")
model = SentenceTransformer('BAAI/bge-m3')

# Test embeddings
texts = [
    "This is a test document about mathematics.",
    "Another document for testing embeddings.",
]

print(f"Generating embeddings for {len(texts)} texts...")
embeddings = model.encode(texts, normalize_embeddings=True)

print(f"Embedding shape: {embeddings.shape}")
print(f"Embedding norm: {np.linalg.norm(embeddings[0]):.4f}")

# Test batch processing (CRITICAL: min 100 for performance)
print("\nTesting batch processing...")
batch_texts = [f"Test document {i}" for i in range(100)]
batch_embeddings = model.encode(batch_texts, normalize_embeddings=True)
print(f"Batch embeddings shape: {batch_embeddings.shape}")
EOF

uv run python debug_embeddings.py
```

### Phase 8: Test DSPy Extraction

```bash
# Test DSPy extraction
cat > debug_dspy.py << 'EOF'
"""Debug DSPy extraction."""
import os
from dotenv import load_dotenv

load_dotenv()

import dspy
from sruth.shared.extraction.dspy_modules import CurriculumExtractor

# Configure DSPy
llm = dspy.OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
dspy.configure(lm=llm)

# Test extraction
print("Testing DSPy extraction...")
extractor = CurriculumExtractor()

result = extractor.extract(
    pdf_content="Junior Certificate Mathematics syllabus includes algebra, geometry, and statistics."
)

print(f"Extraction result: {result}")
EOF

uv run python debug_dspy.py
```

---

## Research & Investigation Commands

### Inspect Existing DLT Assets

```bash
# View all DLT assets
uv run python -c "
from dagster_defs.assets.ireland import curriculum_dlt_assets
for asset in curriculum_dlt_assets:
    print(f'{asset.key.to_user_string()}')
    print(f'  Keys: {asset.keyspartition_keys}')
    print(f'  Partitions: {asset.partitions_def}')
"
```

### Check CocoIndex Flows

```bash
# View CocoIndex flow definitions
uv run python -c "
from pathlib import Path
import ast

flow_files = [
    'cocoindex_flows/pdf_embedding.py',
    'cocoindex_flows/curriculum_embedding.py',
]

for flow_file in flow_files:
    path = Path(flow_file)
    if path.exists():
        print(f'\n=== {flow_file} ===')
        print(path.read_text()[:500])
"
```

### Inspect Storage Schemas

```bash
# Check what tables exist
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()

import duckdb

# Connect to local DuckDB with DuckLake
conn = duckdb.connect('sruth.duckdb')

# List all tables
tables = conn.execute('SHOW TABLES').fetchall()
print('Tables:', tables)

# Check a specific table
for table, in tables[:5]:
    schema = conn.execute(f'DESCRIBE {table}').fetchall()
    print(f'\n{table}:')
    for col in schema:
        print(f'  {col[0]}: {col[1]}')
"
```

---

## Integration: From Component to Working Asset

### Pattern: Converting YAML Component to Executable Asset

```python
# sruth/oideachais/dagster_defs/assets/component_based_assets.py
"""Assets created from component definitions."""

from dagster import asset, AssetSpec
from sruth.oideachais.dagster_defs.components import PDFPipelineComponent
import pandas as pd

# Initialize component
component = PDFPipelineComponent()

# Example: Creating an actual asset from component config
@asset(
    key=["oideachais", "sources", "ncca_curriculum"],
    partitions_def=StaticPartitionDef(component.cycles),
)
def ncca_curriculum_source(context) -> pd.DataFrame:
    """Fetch curriculum data from NCCA."""
    # Use component's source configuration
    source = component.create_dlt_source("ncca")

    # Actual extraction logic here
    # ...

    return pd.DataFrame([
        {"subject": "mathematics", "cycle": "junior_cycle", "url": "..."},
    ])

@asset(
    key=["oideachais", "pdfs", "extracted_text"],
    deps=[ncca_curriculum_source],
)
def pdf_extracted_text(context, ncca_curriculum_source: pd.DataFrame) -> pd.DataFrame:
    """Extract text from PDFs using OCR."""
    # Use component's storage config
    storage = component.get_storage_config()

    # Actual extraction logic here
    # ...

    return pd.DataFrame([
        {"subject": "mathematics", "text": "...", "pages": 10},
    ])
```

---

## Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing env vars | `KeyError: 'LAKEKEEPER_CATALOG_URI'` | Create `.env` file with all required variables |
| DuckDB concurrency | Segmentation fault | Ensure `CONCURRENCY_LIMITS = {"duckdb": 1}` is set |
| Firecrawl rate limit | 429 errors | Add `op_tags={"dagster/concurrency_key": "firecrawl"}` to assets |
| Embedding slow | Takes >10s for 100 docs | Ensure `batch_size >= 100` for embeddings |
| Lakekeeper connection | Connection refused | Check Lakekeeper is running: `docker ps \| grep lakekeeper` |

---

## Next Steps

1. **Run Phase 1-3** above to verify environment and Dagster setup
2. **Materialize a single asset** to test end-to-end flow
3. **Check logs** in Dagster UI for each step
4. **Verify storage** - check data landed in DuckDB/Lakekeeper
5. **Iterate** - fix issues one at a time

For component-based implementation, we need to:
1. Implement YAML parsing in component loaders
2. Generate actual `@asset` functions from component specs
3. Integrate component assets into main `definitions.py`
