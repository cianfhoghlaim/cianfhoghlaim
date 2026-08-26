"""
One-shot materialiser for the ncca-leaving-cert-syllabi-corpus change.

Downloads the currently-taught Leaving Certificate syllabi for a chosen set of
(subject, language) pairs into `stedding/ingest_queue/curriculumonline.ie/`.

This is the same download logic the `lc_syllabus_download` Dagster asset
runs, but invoked directly from the shell so you can populate the ingest
queue WITHOUT a live Dagster instance. After the files are in place, the
existing `pdf_processing_syllabus` daily asset picks them up automatically.

We write BOTH a canonical-name file AND a date-suffixed companion
(`{stem}_{YYYY-MM-DD}.pdf`) so the daily pipeline's
`**/*-{today_str}*.pdf` glob catches them.

Run:  uv run python -m scripts.materialise_lc_syllabus --pairs mathematics,en mathematics,ga gaeilge,ga english,en
"""

from __future__ import annotations

import argparse
import hashlib

# Stub the dlt_sources package so we can import our own new module
import importlib.util
import os
import sys
import types
from datetime import UTC, datetime
from pathlib import Path


def _stub_dlt_sources() -> None:
    stub = types.ModuleType("dlt_sources")
    stub_ie = types.ModuleType("dlt_sources.ie")
    stub_ie_edu = types.ModuleType("dlt_sources.ie.education")
    for name in [
        "ALL_JC_SUBJECTS",
        "ALL_LC_SUBJECTS",
        "ALL_LCA_SUBJECTS",
        "junior_cycle_exams_source",
        "leaving_certificate_source",
        "mathematics_exams_source",
        "science_subjects_exams_source",
        "agentic_discovery_source",
        "deep_research_source",
        "exam_pdf_download_source",
        "examinations_source",
        "oide_source",
        "oide_all_subjects_source",
        "oide_gaeilge_source",
        "oide_subject_source",
        "pdf_download_source",
        "sec_examinations_browser_source",
    ]:
        setattr(stub_ie_edu, name, (lambda *a, **kw: None) if name.endswith("source") else [])
    sys.modules["dlt_sources"] = stub
    sys.modules["dlt_sources.ie"] = stub_ie
    sys.modules["dlt_sources.ie.education"] = stub_ie_edu


_stub_dlt_sources()

_MOD_PATH = (
    Path(__file__).parent.parent
    / "cianfhoghlaim/pipelines/ingest/ie/education/curriculumonline_syllabi.py"
)
spec = importlib.util.spec_from_file_location("curriculumonline_syllabi_mat", _MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["curriculumonline_syllabi_mat"] = mod
spec.loader.exec_module(mod)

_scrape_subject_page = mod._scrape_subject_page
_extract_pdf_links_from_page = mod._extract_pdf_links_from_page
_filename_from_url = mod._filename_from_url

import requests  # noqa: E402

STEDDING_ROOT = Path(os.environ.get("STEDDING_ROOT") or "/stedding/ingest_queue")
# On developer machines /stedding is read-only or doesn't exist; fall back to
# the in-repo stedding/ tree which is gitignored but always writable.
if not STEDDING_ROOT.parent.exists():
    STEDDING_ROOT = Path(__file__).parent.parent / "stedding" / "ingest_queue"
INGEST_TARGET = STEDDING_ROOT / "curriculumonline.ie"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _download(
    url: str, target: Path, label: str, dated_target: Path | None = None
) -> tuple[bool, int, str | None]:
    """Download one PDF to its target path. Returns (downloaded?, http_status, error).

    If `dated_target` is provided, also write a date-suffixed companion file
    so the daily `pdf_processing_syllabus` asset picks it up via
    `**/*-{today_str}*.pdf`.
    """
    try:
        resp = requests.get(
            url, timeout=60, headers={"User-Agent": USER_AGENT}, allow_redirects=True
        )
        resp.raise_for_status()
        pdf_bytes = resp.content
    except Exception as exc:
        return (False, 0, f"download_failed: {exc}")

    sha = hashlib.sha256(pdf_bytes).hexdigest()
    skipped_canonical = False
    if target.exists():
        try:
            existing = hashlib.sha256(target.read_bytes()).hexdigest()
            if existing == sha:
                skipped_canonical = True
        except OSError:
            pass
    if not skipped_canonical:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf_bytes)
    # Always ensure the date-suffixed companion file exists (for the daily
    # pdf_processing_syllabus asset to find via `**/*-{today_str}*.pdf` glob).
    if dated_target is not None:
        dated_target.parent.mkdir(parents=True, exist_ok=True)
        if (
            not dated_target.exists()
            or hashlib.sha256(dated_target.read_bytes()).hexdigest() != sha
        ):
            dated_target.write_bytes(pdf_bytes)
    action = "skip" if skipped_canonical else "ok  "
    print(f"  [{action}] {label}: {target.name} ({len(pdf_bytes):,} bytes, sha={sha[:12]})")
    return (True, resp.status_code, None)


def materialise_one(subject: str, language: str) -> dict:
    """Discover + download all PDFs for one (subject, language) pair."""
    print(f"\n=== {subject} | {language} ===")
    pages = _scrape_subject_page(subject, language, use_local_scrapes=False)
    if not pages:
        print(f"  [warn] no pages scraped for {subject}/{language}")
        return {"subject": subject, "language": language, "files": []}

    discovered: list = []
    for page in pages:
        discovered.extend(_extract_pdf_links_from_page(page, subject, language))

    if not discovered:
        print(f"  [warn] no PDFs discovered for {subject}/{language}")
        return {"subject": subject, "language": language, "files": []}

    target_dir = INGEST_TARGET / subject / language
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")
    results: list[dict] = []
    for d in discovered:
        url = d.url
        filename = d.filename or _filename_from_url(url)
        target = target_dir / filename
        # Also write a date-suffixed companion file so pdf_processing_syllabus
        # picks it up via `**/*-{today_str}*.pdf` glob.
        dated_target = target_dir / f"{target.stem}_{today_str}.pdf"
        ok, status, err = _download(
            url, target, f"{subject}/{language}/{d.document_type}", dated_target
        )
        results.append(
            {
                "url": url,
                "filename": filename,
                "document_type": d.document_type,
                "target": str(target),
                "dated_target": str(dated_target),
                "ok": ok,
                "status": status,
                "error": err,
            }
        )
    return {"subject": subject, "language": language, "files": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pairs",
        nargs="+",
        required=True,
        help='One or more "subject,language" pairs, e.g. mathematics,en mathematics,ga',
    )
    args = parser.parse_args()

    pairs: list[tuple[str, str]] = []
    for raw in args.pairs:
        subj, lang = raw.split(",")
        pairs.append((subj.strip(), lang.strip()))

    print(f"Materialising {len(pairs)} (subject, language) pairs")
    print(f"Target root: {INGEST_TARGET}")
    print("Using local Firecrawl cache fallback is enabled via USE_LOCAL_SCRAPES=true")
    print()

    grand_total = 0
    grand_skipped = 0
    grand_errored = 0

    for subj, lang in pairs:
        result = materialise_one(subj, lang)
        for f in result["files"]:
            grand_total += 1
            if f["ok"]:
                if (
                    f.get("status") == 200
                    and f.get("error") is None
                    and "(sha256 matches)" in str(f)
                ):
                    grand_skipped += 1
                else:
                    pass
            else:
                grand_errored += 1

    print("\n=== SUMMARY ===")
    print(f"Pairs processed: {len(pairs)}")
    print(f"Total files: {grand_total}")
    print(f"Files skipped (already cached): {grand_skipped}")
    print(f"Files errored: {grand_errored}")
    print(f"\nFiles are at: {INGEST_TARGET}")
    print("Next run of `pdf_processing_syllabus` will pick them up automatically.")
    return 0 if grand_errored == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
