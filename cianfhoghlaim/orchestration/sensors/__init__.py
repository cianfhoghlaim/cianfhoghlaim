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
- Upstream package monitoring (the breaking_change_sensor in
  cianfhoghlaim.orchestration/assets/upstream_monitoring_assets.py — kept
  in the new tree under 3_model_lifecycle/upstream_monitoring_assets/)

This package is intentionally empty. New sensors should be added as
L5 CelticAgentOpsComponent auto-generated sensors or as new defs
in the relevant layer folder.
"""
