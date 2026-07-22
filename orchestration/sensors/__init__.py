"""
Dagster sensors package.

The 6 hand-rolled sensors that previously lived here
(author_archive_sensors, ccc_freshness_sensor, cognee_cron_sensor,
curriculum_freshness, domain_sensors, leabharlann_sensors) were
retired in the 2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture
change. Sensors are now emitted by:

- L1 CelticIngestionComponent (cron-driven; sensor not needed)
- L5 CelticAgentOpsComponent (auto-fires the 5_agent_ops/<framework>/<agent>/agent_down
  sensor when the health check returns healthy=False)
- Upstream package monitoring (the breaking-change sensor in
  ``upstream_breaking_change_sensor.py``), which polls
  ``md:cianfhoghlaim_upstream.upstream_monitoring`` for package-level
  breaking changes.

New sensors should normally be added as L5 CelticAgentOpsComponent
auto-generated sensors or as new defs in the relevant layer folder.
The upstream-package-monitoring capability keeps its standalone sensor
here because it is shared by the Firecrawl monitor scripts and the L3
CocoIndex upstream Apps.
"""

from __future__ import annotations

from .upstream_breaking_change_sensor import upstream_breaking_change_sensor

__all__ = ["upstream_breaking_change_sensor"]
