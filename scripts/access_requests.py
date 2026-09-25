#!/usr/bin/env python3
"""CLARIN + institutional data-access request tracker.

Phase 3 of the 5-phase Celtic pipeline overhaul requires access to 5
institutional corpora + CLARIN VLO. The actual email submissions are
external — this script tracks them.

For each request, the tracker holds:
- corpus name + URL
- contact email + request URL
- license terms
- expected delivery date (4-week lead time)
- status (pending / submitted / approved / denied)

Run:
    python scripts/access_requests.py list          # show all requests
    python scripts/access_requests.py submit <key>  # mark as submitted (interactive)
    python scripts/access_requests.py approve <key> # mark as approved
    python scripts/access_requests.py deny <key>    # mark as denied
    python scripts/access_requests.py template <key> # print the email template
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
TRACKER_PATH = REPO_ROOT / "stedding" / "sister-lifts" / "ACCESS_REQUESTS.json"

# The 5 institutional + CLARIN-UK requests.
# Submit date placeholder = TBD; user will fill in when the email is actually sent.
REQUESTS = {
    "cng": {
        "corpus": "Corpas Náisiúnta na Gaeilge",
        "url": "https://www.corpas.ie/en/",
        "scale": "100M words, balanced written + spoken, 2000-2024",
        "license": "Research use only (Foras na Gaeilge + DCU Gaois)",
        "contact": "gaois@computing.dcu.ie (Brian Ó Raghallaigh, Gaois Research Group)",
        "request_url": "https://www.gaois.ie/en/about/info (enquiry form)",
        "expected_delivery_days": 28,
        "depends_on": None,
        "submitted_on": None,
        "approved_on": None,
        "notes": "The 100M-word corpus is the single largest Irish-language training resource. Required for Phase 3.1 + Phase 3.7 (institutional_embedding.py).",
    },
    "ria_corpas": {
        "corpus": "Royal Irish Academy Corpas (historical 1600-1926)",
        "url": "https://corpas.ria.ie/",
        "scale": "3000+ historical Irish texts, 1600-1926",
        "license": "Research use (Royal Irish Academy)",
        "contact": "corpas@ria.ie",
        "request_url": "https://corpas.ria.ie/contact (request form on the RIA site)",
        "expected_delivery_days": 28,
        "depends_on": None,
        "submitted_on": None,
        "approved_on": None,
        "notes": "Required for Phase 3.6 (dialect_ria_corpas.py). Modern Irish (post-1926) is covered by CNG; RIA Corpas is for historical Irish.",
    },
    "corcencc": {
        "corpus": "CorCenCC (Corpws Cenedlaethol Cymraeg Cyfoes)",
        "url": "https://corcencc.org/",
        "scale": "11M words / 14.4M tokens, written + spoken + electronic, Cardiff Uni",
        "license": "Research use (request-only download; Cardiff Research Data:27053194)",
        "contact": "knightd@cardiff.ac.uk (Dawn Knight, Cardiff University)",
        "request_url": "https://cardiff.onlinesurveys.ac.uk/corpus-request (Cardiff Uni form)",
        "expected_delivery_days": 21,
        "depends_on": None,
        "submitted_on": None,
        "approved_on": None,
        "notes": "Required for Phase 4.3 (welsh_institutional.py). The Mozilla Data Collective hosts a mirror: https://mozilladatacollective.com/datasets/cmm3gotrz00j8nt07bsjz2znh — use as fallback.",
    },
    "arcosg": {
        "corpus": "ARCOSG (Annotated Reference Corpus of Scottish Gaelic)",
        "url": "https://datashare.is.ed.ac.uk/handle/10283/2011",
        "scale": "~80K words across 8 registers (4 spoken + 4 written)",
        "license": "Research use (University of Edinburgh Datashare)",
        "contact": "datashare@ed.ac.uk (Edinburgh Datashare support)",
        "request_url": "https://datashare.is.ed.ac.uk/handle/10283/2011 (request access link)",
        "expected_delivery_days": 7,
        "depends_on": None,
        "submitted_on": None,
        "approved_on": None,
        "notes": "Required for Phase 3.6 strengthening (Scottish Gaelic overlay). Already publicly available via Datashare; the request is for the full download + license clarification.",
    },
    "term_ofis_breton": {
        "corpus": "Ofis Publik ar Brezhoneg TermOfis (Breton terminology)",
        "url": "https://www.fr.brezhoneg.bzh/",
        "scale": "constantly updated terminology database (thousands of terms)",
        "license": "Public API + scraping allowed",
        "contact": "kontakt@ofis-bzh.org (OPLB)",
        "request_url": "https://www.fr.brezhoneg.bzh/kontakt (contact form)",
        "expected_delivery_days": 14,
        "depends_on": None,
        "submitted_on": None,
        "approved_on": None,
        "notes": "Required for Phase 4.6 (breton_hf.py) — terminology layer. Note: there's also a Mozilla Data Collective mirror: https://mozilladatacollective.com/datasets/cmpzkqaqu0065nv070bdv5hfj",
    },
    "clarin_vlo": {
        "corpus": "CLARIN Virtual Language Observatory (VLO) public dataset catalogue",
        "url": "https://vlo.clarin.eu/",
        "scale": "millions of records, multi-jurisdiction Celtic + Germanic + Romance",
        "license": "Per-resource (VLO is a search index; each record links to the underlying licence)",
        "contact": "support@clarin.eu",
        "request_url": "No request needed — VLO is public + has a JSON API at https://vlo.clarin.eu/api/v1",
        "expected_delivery_days": 0,
        "depends_on": None,
        "submitted_on": "2026-09-25 (no request needed)",
        "approved_on": "2026-09-25 (VLO is public)",
        "notes": "The wholesale-copied ciancheiltis `dlt_sources/language/clarin.py` already uses VLO's JSON API. Phase 3.1 will land this in cianfhoghlaim proper.",
    },
}


def _load_state() -> dict:
    if TRACKER_PATH.exists():
        return json.loads(TRACKER_PATH.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict) -> None:
    TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_PATH.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def _now_iso() -> str:
    return dt.date.today().isoformat()


def cmd_list() -> None:
    state = _load_state()
    print(f"\n{'KEY':<24} {'CORPUS':<48} {'STATUS':<16} {'SUBMITTED':<12} {'EXPECTED':<12}")
    print("-" * 120)
    for key, req in REQUESTS.items():
        s = state.get(key, {})
        status = "approved" if s.get("approved_on") else ("denied" if s.get("denied_on") else ("submitted" if s.get("submitted_on") else "pending"))
        submitted = s.get("submitted_on", "-")[:10] if s.get("submitted_on") else "-"
        expected = req.get("expected_delivery_days", 0)
        print(f"{key:<24} {req['corpus'][:46]:<48} {status:<16} {submitted:<12} {expected:>10}d")
    print()


def cmd_submit(key: str) -> None:
    if key not in REQUESTS:
        raise SystemExit(f"Unknown request: {key}. Known: {list(REQUESTS)}")
    state = _load_state()
    today = _now_iso()
    state[key] = state.get(key, {})
    state[key]["submitted_on"] = today
    _save_state(state)
    print(f"Marked {key} as submitted on {today}.")


def cmd_approve(key: str) -> None:
    if key not in REQUESTS:
        raise SystemExit(f"Unknown request: {key}")
    state = _load_state()
    today = _now_iso()
    state[key] = state.get(key, {})
    if not state[key].get("submitted_on"):
        state[key]["submitted_on"] = today
    state[key]["approved_on"] = today
    _save_state(state)
    print(f"Marked {key} as approved on {today}.")


def cmd_deny(key: str) -> None:
    if key not in REQUESTS:
        raise SystemExit(f"Unknown request: {key}")
    state = _load_state()
    today = _now_iso()
    state[key] = state.get(key, {})
    state[key]["denied_on"] = today
    _save_state(state)
    print(f"Marked {key} as denied on {today}.")


def cmd_template(key: str) -> None:
    if key not in REQUESTS:
        raise SystemExit(f"Unknown request: {key}")
    req = REQUESTS[key]
    template = f"""To: {req['contact']}
Subject: Research access request — {req['corpus']}

Dear Colleagues,

I am writing on behalf of the cianfhoghlaim monorepo (an open-source
British-Isles Education Pipeline platform, https://github.com/cianfhoghlaim/cianfhoghlaim)
to request research access to {req['corpus']} ({req['url']}).

We are developing NLP infrastructure for the 8 Celtic languages
(Irish, Scottish Gaelic, Welsh, Manx, Cornish, Breton) and English as
part of an open-source BIEP (British-Isles Education Pipeline) project.
The corpus would be used for:

1. Language modelling research (UD parsing, grammatical-pattern extraction,
   Celtic-language BAML extractors).
2. Embedding pretraining (CocoIndex + LanceDB Lance namespace
   `cianhoghlaim.celtic.*`).
3. Educational dashboard marimo notebooks (operator-facing) — no
   user-facing PII.

Dataset profile:
    Scale: {req['scale']}
    License: {req['license']}

We will respect the corpus licence and cite it in any derivative work.
All outputs will be open-sourced under MIT + BUSL-1.1 (the cianfhoghlaim
licence mix). No commercial use of the raw corpus is planned.

The dataset will be loaded via the ciancheiltis sister repo's CLARIN VLO
loader at `dlt_sources/language/clarin.py` (the canonical pattern, per
openspec/changes/2026-09-25-clarin-uk-institutional-v1).

Please let me know if you need any further documentation or a Data
Processing Agreement. We can wait the standard 28-day review window.

Thank you for your time.

— cianfhoghlaim build-agent (autonomous)
   research@cianfhoghlaim.ie (placeholder)
   {req['request_url']}
"""
    print(template)


def main() -> int:
    parser = argparse.ArgumentParser(description="CLARIN + institutional access request tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Show all requests + status")
    sub.add_parser("submit", help="Mark a request as submitted (interactive)").add_argument("key")
    sub.add_parser("approve", help="Mark a request as approved").add_argument("key")
    sub.add_parser("deny", help="Mark a request as denied").add_argument("key")
    sub.add_parser("template", help="Print the email template for a request").add_argument("key")

    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "submit":
        cmd_submit(args.key)
    elif args.cmd == "approve":
        cmd_approve(args.key)
    elif args.cmd == "deny":
        cmd_deny(args.key)
    elif args.cmd == "template":
        cmd_template(args.key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
