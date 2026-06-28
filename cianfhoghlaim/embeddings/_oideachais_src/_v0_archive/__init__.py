"""
v0 CocoIndex modules (DEPRECATED 2026-06-24).

These 10 modules were written against the removed v0 DSL
(@cocoindex.flow_def, FlowBuilder, DataScope, cocoindex.sources,
cocoindex.targets). They raise ImportError on cocoindex==1.0.9.

The 11 v1 Apps at oideachais.cocoindex_flows.* cover the equivalent
use cases (see .agents/skills/oideachais-cocoindex-v1/SKILL.md).

Migration: the 10 v0 modules are preserved on disk for historical
reference only. No v0-to-v1 migration is planned in this change;
the migration is a 6-week project per oideachais/REFACTORING.md #6.

To migrate a v0 module to v1:
1. Read the v0 module's flow_builder.add_source(...) + collector.collect(...) pattern
2. Replace with @coco.lifespan + @coco.fn + lancedb.mount_table_target + table.declare_row(...)
3. Update the @dataclass to use Annotated[NDArray, EMBEDDER] for the embedding field
4. Add the App to oideachais/cocoindex_flows/__init__.py
5. Add a Dagster asset at oideachais/dagster_defs/assets/
6. Update oideachais/cocoindex_flows/README.md v0/v1 status table
"""
