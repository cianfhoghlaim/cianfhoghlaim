"""MotherDuck Flights for the Cianfhoghlaim lakehouse.

The Flights surface consists of two layers:

1. **8 stub Flights** at ``flights/`` that define
   ``FLIGHT_NAME`` / ``FLIGHT_CRON`` / ``FLIGHT_TIMEZONE`` constants
   and a ``build_<slug>()`` callable. These stubs previously
   imported a non-existent :func:`run_flight` helper at module
   load time; this module now provides that helper.

2. **5 fully-implemented Flights** (``lc_pdf_sync_flight``,
   ``ireland_lc_daily_sync_flight``, ``sct_wls_ni_flight``,
   ``crown_dependencies_flight``, plus the 13 BIEP v3 flights
   registered in ``flights/config.yaml``) that orchestrate Dagster
   asset materialisations + CocoIndex updates.

Registration path: the canonical BIEP v3 Flight registry lives at
``flights/config.yaml`` and is consumed by MotherDuck's Flight
scheduler (see ``openspec/changes/2026-08-12-biep-v3-motherduck-flights-v1``).
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("motherduck.flights")

# Re-export the canonical v1 daily flight entrypoint so that
# `from motherduck import lc_pdf_sync_flight_main` works.
from .lc_pdf_sync_flight import main as lc_pdf_sync_flight_main

# MotherDuck Flight API base URL (configurable via env var).
MOTHERDUCK_API_BASE = os.environ.get(
    "MOTHERDUCK_API_BASE", "https://api.motherduck.com"
)


def run_flight(
    *,
    name: str,
    cron: str,
    timezone: str = "UTC",
    schedule_kind: str = "cron",
    module: str | None = None,
    callable_name: str | None = None,
    started_at: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Register a Flight with the MotherDuck Flight scheduler.

    Parameters
    ----------
    name : str
        The canonical Flight name (e.g. ``lc_pdf_sync_flight``).
    cron : str
        Cron expression (5-field POSIX cron).
    timezone : str
        IANA timezone (default ``UTC``).
    schedule_kind : str
        ``cron`` (the only currently supported kind).
    module, callable_name : str, optional
        The Python entrypoint that MotherDuck should invoke when the
        cron fires. Defaults to ``motherduck.flights.<name>`` and
        ``main``.
    started_at : str, optional
        ISO-8601 timestamp. If omitted, MotherDuck defaults to the
        next cron tick.
    dry_run : bool
        If True, return the payload that *would* be POSTed without
        actually calling the API. Useful for CI + dry-run validation.

    Returns
    -------
    dict
        The MotherDuck API response. In ``dry_run`` mode, the
        payload + a ``dry_run: True`` flag.
    """
    payload: dict[str, Any] = {
        "name": name,
        "cron": cron,
        "timezone": timezone,
        "schedule_kind": schedule_kind,
        "module": module or f"motherduck.flights.{name}",
        "callable": callable_name or "main",
    }
    if started_at:
        payload["started_at"] = started_at

    if dry_run:
        logger.info("dry_run_run_flight: %s @ %s %s", name, cron, timezone)
        return {"dry_run": True, "payload": payload, "ok": True}

    api_key = os.environ.get("MOTHERDUCK_TOKEN", "")
    if not api_key:
        logger.warning("run_flight_no_token: %s (returning local-only ack)", name)
        return {
            "ok": True,
            "registered_locally": True,
            "payload": payload,
            "note": "MOTHERDUCK_TOKEN not set; flight is staged but not pushed to MotherDuck",
        }

    url = f"{MOTHERDUCK_API_BASE}/v1/flights"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
            return {"ok": True, "status_code": resp.status, "body": body, "payload": payload}
    except urllib.error.HTTPError as e:  # pragma: no cover — network
        logger.error("run_flight_http_error: %s — %s", name, e)
        return {"ok": False, "status_code": e.code, "error": str(e), "payload": payload}
    except urllib.error.URLError as e:  # pragma: no cover — network
        logger.error("run_flight_url_error: %s — %s", name, e)
        return {"ok": False, "error": str(e), "payload": payload}


__all__ = [
    "MOTHERDUCK_API_BASE",
    "lc_pdf_sync_flight_main",
    "run_flight",
]