from pathlib import Path

from dagster import Definitions, load_assets_from_modules

from defs.curriculum import sources, processing
from defs.curriculum.resources import (
    DLTResource,
    LanceDBResource,
    CocoIndexResource,
    ColPaliResource,
    Qwen3VLResource,
)
from defs.fibo_generation import assets as fibo_assets
from defs.fibo_generation.resources import FiboResource, ValidationResource


# Load all assets from modules
all_assets = load_assets_from_modules([sources, processing, fibo_assets])

# Instantiate resources with keys matching asset parameter names
resources = {
    "dlt_resource": DLTResource(),
    "lancedb_resource": LanceDBResource(),
    "cocoindex_resource": CocoIndexResource(),
    "colpali_resource": ColPaliResource(),
    "qwen3vl_resource": Qwen3VLResource(),
    "fibo_resource": FiboResource(),
    "validation_resource": ValidationResource(),
}

defs = Definitions(
    assets=all_assets,
    resources=resources,
)
