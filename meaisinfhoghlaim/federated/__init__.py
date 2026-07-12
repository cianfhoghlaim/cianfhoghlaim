"""Federated learning for Irish OCR + handwriting recognition.

Per T4 of the 5-tangent modernization (the
`2026-07-09-agent-fleet-and-observability-facade-v1` change), the
federated OCR subsystem was moved from
`cianfhoghlaim.meaisinfhoghlaim.process.irish_ocr_federated` (which
was orphaned after the v4 consolidation) into this package. The
Dagster asset at
`cianfhoghlaim/orchestration/defs/3_model_lifecycle/irish_ocr_federated_assets.py`
materialises `irish_ocr_federated_smoke` on a 30-minute cadence to
keep the federated server simulator warm.

Canonical entry points (re-exported):

- `IrishOCRFederatedServer` / `IrishOCRFederatedClient`
- `create_dialect_specialized_clients(...)`
- `run_federated_training(...)`
- `FederatedConfig`, `ClientUpdate`, `ServerState`
- `FedAvgStrategy`, `FedProxStrategy`
- `MOBILE_PROFILES`, `IRISH_DIALECTS`
"""
from __future__ import annotations

from .irish_ocr_federated import (
    ClientUpdate,
    FedAvgStrategy,
    FederatedConfig,
    FederatedStrategy,
    FedProxStrategy,
    IRISH_DIALECTS,
    IrishOCRFederatedClient,
    IrishOCRFederatedServer,
    MOBILE_PROFILES,
    ServerState,
    create_dialect_specialized_clients,
    run_federated_training,
)

__all__ = [
    "ClientUpdate",
    "FedAvgStrategy",
    "FedProxStrategy",
    "FederatedConfig",
    "FederatedStrategy",
    "IRISH_DIALECTS",
    "IrishOCRFederatedClient",
    "IrishOCRFederatedServer",
    "MOBILE_PROFILES",
    "ServerState",
    "create_dialect_specialized_clients",
    "run_federated_training",
]
