"""Orchestrator: run both Tuatha dlt sources back-to-back with shared observability."""

from __future__ import annotations

import json
import sys

from .player_assets import run as run_player_assets
from .credential_events import run as run_credential_events


def run_all() -> int:
    """Run player_assets then credential_events; aggregate the receipts."""
    receipts = {}
    for name, fn in (
        ("player_assets", run_player_assets),
        ("credential_events", run_credential_events),
    ):
        try:
            rc = fn()
            receipts[name] = {"status": "ok" if rc == 0 else "failed", "rc": rc}
        except Exception as exc:  # pragma: no cover
            receipts[name] = {"status": "error", "error": repr(exc)}
            print(json.dumps(receipts), file=sys.stderr)
            return 1

    print(json.dumps(receipts, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run_all())
