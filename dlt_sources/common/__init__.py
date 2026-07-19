"""endpoint_recovery package — exposes the canonical 3-strategy helper."""

from dlt_sources.common.endpoint_recovery import (
    BackendUsed,
    EndpointRecoveryStrategy,
    PROBE_LIST,
    RecoveredPage,
    declare_asset_check,
    fetch,
    probe_all_39,
)

__all__ = [
    "BackendUsed",
    "EndpointRecoveryStrategy",
    "PROBE_LIST",
    "RecoveredPage",
    "declare_asset_check",
    "fetch",
    "probe_all_39",
]
