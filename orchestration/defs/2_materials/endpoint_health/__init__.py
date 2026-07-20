"""endpoint_health L2 module — exports the sink + alerts assets."""
import importlib as _il
_alerts = _il.import_module("orchestration.defs.2_materials.endpoint_health.alerts")
_sink = _il.import_module("orchestration.defs.2_materials.endpoint_health.sink")
endpoint_health_alerts = _alerts.endpoint_health_alerts
endpoint_health_sink = _sink.endpoint_health_sink
__all__ = ["endpoint_health_alerts", "endpoint_health_sink"]
