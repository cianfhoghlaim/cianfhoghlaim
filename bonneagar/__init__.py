"""cianfhoghlaim.bonneagar — IaC fleet (PostgreSQL migrations, GitOps resources, Pulumi IaC, Komodo resource-syncs, Pangolin client, Infisical clients, the Locket Rust secrets sidecar, deploy runbooks).

This directory contains both TypeScript (Pulumi + Dagger + Komodo
resource-syncs) and Python (IaC clients + commands) sources. The
canonical entry-point is `cianchoghlaim.bonneagar.iac.main` (the Pulumi
orchestrator). Standalone scripts (`scripts/stack-doctor.sh`,
`scripts/marimo_wasm_export.py`, etc.) are not part of this sub-module.

This `__init__.py` exists only to make the directory a proper Python
package (so future `from cianfhoghlaim.bonneagar.iac import X` imports
resolve).
"""
