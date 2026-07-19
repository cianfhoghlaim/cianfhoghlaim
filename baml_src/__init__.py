"""cianfhoghlaim.baml_src — BAML schema source (post-v7 flattening).

This directory contains 318+ `.baml` files organised under jurisdiction +
cluster. The `.baml` files are loaded by `baml-cli generate` (see
`mise run baml:generate`) and the generated Python client is emitted
into `baml_client/`. They are NOT imported as a Python module at runtime
— the BAML runtime reads the directory directly via the codegen tool.

This `__init__.py` exists only to make the directory importable as a
namespace package (so that future `from cianfhoghlaim.baml_src import X`
imports resolve via the v7 flattened package layout).
"""
