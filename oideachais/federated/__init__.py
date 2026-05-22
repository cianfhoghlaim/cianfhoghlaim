"""
Federated Learning Module for Irish OCR.

Provides privacy-preserving distributed training for Irish handwriting
recognition across schools, mobile devices, and community contributors.

Features:
- Flower federated aggregation (FedAvg, FedProx)
- SyftBox secure computation integration
- Dialect-specialized model training
- Mobile-optimized deployment
- Differential privacy support

Based on:
- meaisínfhoghlaim/federated/flwr (Flower framework)
- meaisínfhoghlaim/federated/syft-flwr (SyftBox protocol)
"""

from .irish_ocr_federated import (
    IRISH_DIALECTS,
    MOBILE_PROFILES,
    ClientUpdate,
    FedAvgStrategy,
    FederatedConfig,
    FederatedStrategy,
    FedProxStrategy,
    IrishOCRFederatedClient,
    IrishOCRFederatedServer,
    ServerState,
    create_dialect_specialized_clients,
    run_federated_training,
)

__all__ = [
    "IrishOCRFederatedServer",
    "IrishOCRFederatedClient",
    "FederatedConfig",
    "ClientUpdate",
    "ServerState",
    "FederatedStrategy",
    "FedAvgStrategy",
    "FedProxStrategy",
    "MOBILE_PROFILES",
    "IRISH_DIALECTS",
    "create_dialect_specialized_clients",
    "run_federated_training",
]
