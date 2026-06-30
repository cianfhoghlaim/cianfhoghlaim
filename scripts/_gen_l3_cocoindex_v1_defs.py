"""Generator script: emit one L3 CelticModelLifecycleComponent YAML defs file
per CocoIndex v1 App. Run as `python3 scripts/_gen_l3_cocoindex_v1_defs.py`.

Each emitted file lives at
`cianfhoghlaim/dagster/defs/3_model_lifecycle/cocoindex_v1/<slug>/defs.yaml`
and contains the canonical CelticModelLifecycleComponent YAML pointing
at the source module + the v1 App name.
"""
from __future__ import annotations

import os
from pathlib import Path


# The 17 CocoIndex v1 Apps (from the oideachais-cocoindex-v1 skill).
# Each tuple: (app_name, source_module, slug).
V1_APPS = [
    ("ApiIndex", "cianfhoghlaim.cocoindex.api_indexing", "api_index"),
    ("CocoIndexV1Conformance", "cianfhoghlaim.cocoindex.cocoindex_v1_conformance", "cocoindex_v1_conformance"),
    ("CodebaseGraph", "cianfhoghlaim.cocoindex.codebase_indexing", "codebase_graph"),
    ("CodebaseIndex", "cianfhoghlaim.cocoindex.codebase_indexing", "codebase_index"),
    ("ConfigIndex", "cianfhoghlaim.cocoindex.config_indexing", "config_index"),
    ("culture_heritage_embedding", "cianfhoghlaim.cocoindex.culture_heritage_embedding", "culture_heritage_embedding"),
    ("DocsSkillsConsolidation", "cianfhoghlaim.cocoindex.docs_skills_consolidation", "docs_skills_consolidation"),
    ("FilesystemIndex", "cianfhoghlaim.cocoindex.filesystem_indexing", "filesystem_index"),
    ("LeabharlannBooksEmbedding", "cianfhoghlaim.cocoindex.leabharlann_embedding", "leabharlann_books"),
    ("LeabharlannInboxEmbedding", "cianfhoghlaim.cocoindex.leabharlann_embedding", "leabharlann_inbox"),
    ("LeabharlannTakeoutEmbedding", "cianfhoghlaim.cocoindex.leabharlann_embedding", "leabharlann_takeout"),
    ("LeabharlannZoteroEmbedding", "cianfhoghlaim.cocoindex.leabharlann_embedding", "leabharlann_zotero"),
    ("StorageIndex", "cianfhoghlaim.cocoindex.storage_indexing", "storage_index"),
    ("UnifiedEmbedding", "cianfhoghlaim.cocoindex.unified_embedding", "unified_embedding"),
    ("CodeEmbedding", "cianfhoghlaim.cocoindex.unified_embedding", "code_embedding"),
    ("UniversityCoursesApp", "cianfhoghlaim.cocoindex.university_courses", "university_courses"),
    ("UniversityModulesApp", "cianfhoghlaim.cocoindex.university_modules", "university_modules"),
    ("UpstreamApiSurface", "cianfhoghlaim.cocoindex.upstream_api_surface", "upstream_api_surface"),
    ("UpstreamBlogMonitor", "cianfhoghlaim.cocoindex.upstream_blog_monitor", "upstream_blog_monitor"),
]

OUT_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dagster/defs/3_model_lifecycle/cocoindex_v1"
)


TEMPLATE = """# defs/3_model_lifecycle/cocoindex_v1/{slug}/defs.yaml
#
# L3 CelticModelLifecycleComponent for the {app_name} v1 App.
# Per the oideachais-cocoindex-v1 skill, the R1–R4 conformance contract
# is enforced at build_defs time by the Component. is_virtual=True so
# the LanceDB table mirrors its L1 upstream automatically.
type: cianfhoghlaim.dagster.components.CelticModelLifecycleComponent
attributes:
  app_name: {app_name}
  module: {module}
  embedding_model: BAAI/bge-large-en-v1.5
  hnsw_index: true
  conformance_required: true
"""


def main() -> int:
    written = 0
    for app_name, module, slug in V1_APPS:
        target_dir = OUT_ROOT / slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "defs.yaml"
        target_file.write_text(
            TEMPLATE.format(slug=slug, app_name=app_name, module=module)
        )
        written += 1
    print(f"Wrote {written} v1 App YAML defs files under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
