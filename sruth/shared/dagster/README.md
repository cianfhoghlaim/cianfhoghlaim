# Shared Dagster Resources for Sruth Pipelines

This module provides reusable Dagster resources for common infrastructure components used across all sruth data flows in the Cianfhoghlaim project.

## Available Resources

### LakeKeeperResource

**Purpose**: Integration with LakeKeeper (Lance REST catalog) for managing LanceDB table metadata.

**Location**: `sruth/shared/dagster/lakekeeper_resource.py`

**Key Features**:
- Namespace management
- Table registration with metadata
- Asset materialization helpers
- Embedding table support
- Health checks
- Automatic retries

**Documentation**:
- Full Guide: `/LAKEKEEPER_DAGSTER.md`
- Quick Start: `/LAKEKEEPER_QUICKSTART.md`
- Examples: `sruth/crypteolas/dagster_assets/lakekeeper_examples.py`

**Basic Usage**:

```python
from dagster import asset, Definitions
from sruth.shared.dagster import LakeKeeperResource

@asset
def my_asset(lakekeeper: LakeKeeperResource):
    lakekeeper.create_namespace_if_not_exists("my_project")
    lakekeeper.register_table(
        table_name="my_table",
        location="s3://bucket/lance/my_table.lance",
        namespace="my_project",
    )

defs = Definitions(
    assets=[my_asset],
    resources={"lakekeeper": LakeKeeperResource()},
)
```

## Installation

The resources are part of the project and already integrated. No additional installation needed.

## Configuration

### Environment Variables

Create a `.env` file in your sruth directory:

```bash
# LakeKeeper configuration
LAKEKEEPER_URL=http://localhost:8181
LAKEKEEPER_WAREHOUSE=crypteolas
LAKEKEEPER_NAMESPACE=embeddings
LAKEKEEPER_API_KEY=

# PostgreSQL backend (optional, for production)
PLANETSCALE_HOST=localhost
PLANETSCALE_PORT=5432
PLANETSCALE_DATABASE=lakekeeper
PLANETSCALE_USERNAME=postgres
PLANETSCALE_PASSWORD=postgres
```

See `sruth/crypteolas/.env.lakekeeper.example` for a complete example.

### Resource Configuration in Dagster Definitions

```python
# In your sruth/dagster_assets/definitions.py
from sruth.shared.dagster import LakeKeeperResource
import os

lakekeeper_resource = LakeKeeperResource(
    url=os.getenv("LAKEKEEPER_URL", "http://localhost:8181"),
    warehouse=os.getenv("LAKEKEEPER_WAREHOUSE", "my_sruth"),
    default_namespace=os.getenv("LAKEKEEPER_NAMESPACE", "embeddings"),
    api_key=os.getenv("LAKEKEEPER_API_KEY", ""),
)

defs = Definitions(
    assets=[...],
    resources={"lakekeeper": lakekeeper_resource},
)
```

## Integration by Sruth

### Crypteolas
- **Location**: `sruth/crypteolas/dagster_assets/`
- **Definitions**: Updated with LakeKeeper resource
- **Assets**: `embedding_assets.py` uses LakeKeeper for table registration
- **Examples**: `lakekeeper_examples.py` provides comprehensive examples

### Aleyum
- **Location**: `sruth/aleyum/dagster_assets/`
- **Definitions**: Updated with LakeKeeper resource
- **Status**: Ready for integration with embedding assets

### Oideachais
- **Location**: `sruth/oideachais/` (to be added)
- **Status**: Ready for integration

## Best Practices

### 1. Resource Naming

Use consistent resource names across sruth:

```python
defs = Definitions(
    resources={
        "lakekeeper": LakeKeeperResource(),  # Always use "lakekeeper"
    },
)
```

### 2. Namespace Organization

Organize namespaces by sruth and purpose:

```python
# Crypteolas
warehouse="crypteolas"
default_namespace="crypteolas"
# Namespaces: embeddings, staging, experiments

# Oideachais
warehouse="oideachais"
default_namespace="curriculum"
# Namespaces: curriculum, exams, circulars
```

### 3. Property Standards

Use consistent property keys:

```python
properties = {
    # Embedding tables
    "embedding-model": "BAAI/bge-m3",
    "embedding-dimension": "1024",
    "source-type": "curriculum",

    # Data tables
    "row-count": str(len(data)),
    "source": "ncca_api",
    "created-at": datetime.utcnow().isoformat(),
}
```

### 4. Error Handling

The resource includes automatic retries. Handle specific errors:

```python
@asset
def robust_asset(lakekeeper: LakeKeeperResource):
    try:
        lakekeeper.register_table(...)
    except Exception as e:
        context.log.error(f"Failed: {e}")
        raise
```

## Adding New Resources

To add a new shared resource:

1. Create resource file: `sruth/shared/dagster/my_resource.py`
2. Implement as `dagster.ConfigurableResource`
3. Add to `sruth/shared/dagster/__init__.py`
4. Create documentation
5. Add examples
6. Update this README

Example resource structure:

```python
# sruth/shared/dagster/my_resource.py
import dagster as dg
from pydantic import Field

class MyResource(dg.ConfigurableResource):
    """Description of the resource."""

    config_param: str = Field(description="Configuration parameter")

    def do_something(self) -> None:
        """Resource method."""
        pass
```

## Testing

### Test Resource Connection

```python
# test_resource.py
from sruth.shared.dagster import LakeKeeperResource

resource = LakeKeeperResource()
is_healthy = resource.health_check()
print(f"Healthy: {is_healthy}")
```

### Test in Dagster

```bash
# From sruth/crypteolas
dagster dev

# Navigate to http://localhost:3000
# Check that resource is loaded
# Materialize an asset that uses the resource
```

## Troubleshooting

### Resource Not Found

**Error**: `Resource "lakekeeper" not found`

**Solution**: Add resource to Definitions:
```python
defs = Definitions(
    assets=[my_asset],
    resources={"lakekeeper": LakeKeeperResource()},  # Must be added
)
```

### Connection Issues

**Error**: Cannot connect to LakeKeeper

**Solution**:
1. Check server is running: `curl http://localhost:8181/health`
2. Verify environment variables: `echo $LAKEKEEPER_URL`
3. Check resource configuration in definitions

### Import Errors

**Error**: `No module named 'sruth.shared.dagster'`

**Solution**:
1. Ensure you're running from project root
2. Check Python path: `export PYTHONPATH=/path/to/mogadishu:$PYTHONPATH`
3. Verify file exists: `ls sruth/shared/dagster/__init__.py`

## Documentation

- **LakeKeeper Full Guide**: `LAKEKEEPER_DAGSTER.md`
- **LakeKeeper Quick Start**: `LAKEKEEPER_QUICKSTART.md`
- **Crypteolas Examples**: `sruth/crypteolas/dagster_assets/lakekeeper_examples.py`
- **LakeKeeper Client**: `sruth/crypteolas/storage/lakekeeper_client.py`

## Related Projects

- **LakeKeeper**: https://github.com/Lakekeeper/lakekeeper
- **Dagster**: https://dagster.io/
- **LanceDB**: https://lancedb.github.io/lancedb/

## Support

For issues or questions:

1. Check resource documentation
2. Review examples in crypteolas
3. Check LakeKeeper logs
4. Verify Dagster asset materialization in UI
