"""
Dagster sensors package.

The 8 jurisdiction registry sensors (NCCA + SQA + CCEA + WJEC + JCQ +
IoM + Jersey + Guernsey) watch each jurisdiction's official
curriculum/syllabus registry for changes and emit Dagster
`RunRequest`s to re-ingest the affected cohorts. Each polls every
300s and is wired to its jurisdiction's change-detection job.

Plus 3 cross-cutting sensors:
- `garage_pdf_arrival_sensor` — polls the Garage S3 bucket for new
  PDFs (24 BIEP v3 prefixes × 300s)
- `upstream_breaking_change_sensor` — polls the MotherDuck
  `md:cianfhoghlaim_upstream.upstream_monitoring` schema for
  package-level breaking changes (motherduck / dlthub / lancedb /
  cocoindex)
- `ocr_completion_sensor` — emits a Dagster asset materialization
  when the BIEP v2 OCR ensemble completes a job

New sensors should normally be added as L5 `CelticAgentOpsComponent`
auto-generated sensors or as new defs in the relevant layer folder.
The upstream-package-monitoring capability keeps its standalone sensor
here because it is shared by the Firecrawl monitor scripts and the L3
CocoIndex upstream Apps.

Historical note: The previous version of this file (per the
2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture
change) only re-exported `upstream_breaking_change_sensor` — the
8 jurisdiction registry sensors were not re-exported. Post-v8 they
are re-exported here so the dagster load_defs walker picks them up.
"""
from __future__ import annotations

# 8 jurisdiction registry sensors (1 per BI jurisdiction)
from .ncca_registry_sensor import ncca_registry_sensor
from .sqa_registry_sensor import sqa_registry_sensor
from .ccea_registry_sensor import ccea_registry_sensor
from .wjec_registry_sensor import wjec_registry_sensor
from .jcq_registry_sensor import jcq_registry_sensor
from .isle_of_man_registry_sensor import isle_of_man_registry_sensor
from .jersey_registry_sensor import jersey_registry_sensor
from .guernsey_registry_sensor import guernsey_registry_sensor

# 3 cross-cutting sensors
from .garage_pdf_arrival_sensor import garage_pdf_arrival_job, garage_pdf_arrival_sensor
from .ocr_completion_sensor import ocr_completion_sensor
from .upstream_breaking_change_sensor import upstream_breaking_change_sensor


__all__ = [
    # 8 jurisdiction registry sensors
    "ncca_registry_sensor",
    "sqa_registry_sensor",
    "ccea_registry_sensor",
    "wjec_registry_sensor",
    "jcq_registry_sensor",
    "isle_of_man_registry_sensor",
    "jersey_registry_sensor",
    "guernsey_registry_sensor",
    # 3 cross-cutting sensors
    "garage_pdf_arrival_sensor",
    "garage_pdf_arrival_job",
    "ocr_completion_sensor",
    "upstream_breaking_change_sensor",
]