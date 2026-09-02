#!/usr/bin/env python3
"""
HF Hub liveness watchdog for the v4 OCR/VLM registry.

Runs as a daily cron job (or in a loop) and verifies every
`unsloth_id` / `mlx_id` / `upstream_id` in
`cianfhoghlaim.ocr.models.VISION_MODELS` against the HF Hub API.

On any 404 or non-2xx response, the script:
1. Logs the failure to stderr
2. Writes a JSON report to `/var/log/hf-watchdog/report.json`
3. Exits with code 1 (so the cron can alert on failure)

Usage:
    python watchdog.py                    # one-shot
    python watchdog.py --watch --interval 86400  # loop every 24h
    python watchdog.py --slack-webhook <url>     # POST to Slack on failure
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Ensure the registry is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

warnings.filterwarnings("ignore")
from meaisinfhoghlaim.ocr.models import VISION_MODELS  # noqa: E402

HF_HUB_API = "https://huggingface.co/api/models/{model_id}"
HF_HUB_TIMEOUT = 10.0
REPORT_PATH = Path("/var/log/hf-watchdog/report.json")


def check_model(model_id: str, timeout: float = HF_HUB_TIMEOUT) -> dict[str, object]:
    """Check if a HF model_id is live."""
    url = HF_HUB_API.format(model_id=model_id)
    req = urllib.request.Request(url, headers={"User-Agent": "cianfhoghlaim-ocr-hf-watchdog/1.0"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {
                "model_id": model_id,
                "url": url,
                "status": resp.status,
                "ok": True,
                "elapsed_ms": int((time.time() - start) * 1000),
            }
    except urllib.error.HTTPError as e:
        return {
            "model_id": model_id,
            "url": url,
            "status": e.code,
            "ok": False,
            "error": str(e),
            "elapsed_ms": int((time.time() - start) * 1000),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {
            "model_id": model_id,
            "url": url,
            "status": 0,
            "ok": False,
            "error": str(e),
            "elapsed_ms": int((time.time() - start) * 1000),
        }


def audit_registry() -> dict[str, object]:
    """Audit every model_id in VISION_MODELS."""
    results: list[dict[str, object]] = []
    n_ok = 0
    n_fail = 0
    failures: list[dict[str, object]] = []

    for key, model in VISION_MODELS.items():
        for field, model_id in (
            ("unsloth_id", model.unsloth_id),
            ("mlx_id", model.mlx_id),
            ("upstream_id", model.upstream_id),
        ):
            if not model_id:
                continue
            r = check_model(model_id)
            r["registry_key"] = key
            r["id_field"] = field
            results.append(r)
            if r["ok"]:
                n_ok += 1
            else:
                n_fail += 1
                failures.append(r)
            time.sleep(0.1)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "registry_size": len(VISION_MODELS),
        "n_ids_checked": len(results),
        "n_ok": n_ok,
        "n_fail": n_fail,
        "failures": failures,
        "all_results": results,
    }


def post_to_slack(webhook_url: str, report: dict[str, object]) -> None:
    """POST a failure alert to Slack."""
    if report["n_fail"] == 0:
        return
    payload = {
        "text": (
            f":rotating_light: *HF Watchdog* — {report['n_fail']} of "
            f"{report['n_ids_checked']} model IDs are NOT live on HF Hub\n\n"
            + "\n".join(
                f"• `{f['registry_key']}.{f['id_field']}`: "
                f"`{f['model_id']}` (HTTP {f.get('status', '?')})"
                for f in report["failures"][:10]
            )
        )
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as _:
            pass
    except Exception as e:
        print(f"WARNING: failed to POST to Slack: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run continuously (every --interval seconds)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=86400,  # 24 hours
        help="Watch interval in seconds (default: 86400 = 24h)",
    )
    parser.add_argument(
        "--slack-webhook",
        default=os.environ.get("SLACK_WEBHOOK_URL"),
        help="Slack webhook URL for failure alerts",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=REPORT_PATH,
        help="Path to write the JSON report",
    )
    args = parser.parse_args()

    while True:
        report = audit_registry()
        print(
            f"[{report['timestamp']}] "
            f"{report['n_ok']}/{report['n_ids_checked']} OK "
            f"({report['n_fail']} failures)"
        )

        # Write report
        try:
            args.report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(args.report_path, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"WARNING: failed to write report: {e}", file=sys.stderr)

        # Slack alert
        if args.slack_webhook:
            post_to_slack(args.slack_webhook, report)

        if not args.watch:
            return 1 if report["n_fail"] > 0 else 0

        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
