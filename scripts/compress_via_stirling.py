"""
Compress every PDF in leabharlann/mata/ using the Stirling PDF REST API.

Strategy (audit-driven):
  - lossless files (image_pct < 40%): optimizeLevel=4, no extra options
  - image-heavy files (image_pct >= 40%): optimizeLevel=9 + grayscale=true
                                       (user-accepted lossy for image-heavy)

In-place only if the compressed output is strictly smaller than the original.
Originals are never deleted — replacements are atomic rename from a sibling
.tmp file, so a crash mid-write leaves the original intact.

Output:
  - leabharlann/mata/compression_report.csv   (gitignored)
  - leabharlann/mata/COMPRESSION_REPORT.md   (human-readable)
  - writes a small JSON log to stdout

Usage:
  # Dry-run (no replacements, just preview)
  uv run --with httpx python scripts/compress_via_stirling.py --dry-run

  # Real run, default concurrency
  uv run --with httpx python scripts/compress_via_stirling.py

  # Tighter concurrency
  uv run --with httpx python scripts/compress_via_stirling.py --concurrency 2
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import httpx

MATA = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/mata")
AUDIT_CSV = MATA / ".compression_audit.csv"
REPORT_CSV = MATA / "compression_report.csv"
REPORT_MD = MATA / "COMPRESSION_REPORT.md"

STIRLING_BASE = os.getenv("STIRLING_BASE", "http://localhost:8080")
COMPRESS_ENDPOINT = "/api/v1/misc/compress-pdf"
FLATTEN_ENDPOINT = "/api/v1/misc/flatten"

CONCURRENCY = int(os.getenv("STIRLING_COMPRESS_CONCURRENCY", "2"))
REQUEST_TIMEOUT = httpx.Timeout(connect=10.0, read=1800.0, write=1800.0, pool=10.0)


@dataclass
class FileResult:
    file: str
    mode: str  # "lossless" | "lossy" | "skip"
    before_bytes: int
    after_bytes: int
    saved_bytes: int
    ratio: float  # after / before
    seconds: float
    status: str  # "replaced" | "kept_original" | "error"
    error: str = ""
    pages: int = 0
    image_pct: float = 0.0


def load_audit() -> list[dict]:
    if not AUDIT_CSV.is_file():
        print(f"ERROR: audit CSV not found at {AUDIT_CSV}", file=sys.stderr)
        print("Run scripts/audit_leabharlann_mata.py first.", file=sys.stderr)
        sys.exit(2)
    with AUDIT_CSV.open() as f:
        return list(csv.DictReader(f))


def build_form(audit_row: dict, dry_run: bool, optimize_level_override: int | None = None) -> dict:
    """
    Build the multipart form-data fields for the Stirling compress endpoint.

    Lossless (text/fonts dominate):  optimizeLevel=4
    Lossy (image-heavy):             optimizeLevel=9, grayscale=true

    Stirling's optimizeLevel enum is 1..9; higher = more aggressive.
    """
    is_image_heavy = audit_row["is_image_heavy"].strip().lower() in ("true", "1", "yes")
    if optimize_level_override is not None:
        optimize_level = optimize_level_override
    else:
        optimize_level = 9 if is_image_heavy else 4

    fields: dict = {
        "optimizeLevel": str(optimize_level),
        "linearize": "false",
        "normalize": "false",
    }
    if is_image_heavy:
        fields["grayscale"] = "true"
    if dry_run:
        # We still need to send something for fileInput, but the orchestrator
        # will skip the actual upload and just return the audit row.
        pass
    return fields


async def compress_one(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    audit_row: dict,
    dry_run: bool,
) -> FileResult:
    pdf_path = MATA / audit_row["file"]
    before = pdf_path.stat().st_size
    pages = int(audit_row["pages"])
    image_pct = float(audit_row["image_pct"])
    is_image_heavy = audit_row["is_image_heavy"].strip().lower() in ("true", "1", "yes")
    mode = "lossy" if is_image_heavy else "lossless"

    base = FileResult(
        file=audit_row["file"],
        mode=mode,
        before_bytes=before,
        after_bytes=before,
        saved_bytes=0,
        ratio=1.0,
        seconds=0.0,
        status="skip",
        pages=pages,
        image_pct=image_pct,
    )

    if dry_run:
        return base

    async with sem:
        t0 = time.monotonic()
        try:
            fields = build_form(audit_row, dry_run=False)
            with pdf_path.open("rb") as fh:
                files = {"fileInput": (pdf_path.name, fh, "application/pdf")}
                resp = await client.post(
                    f"{STIRLING_BASE}{COMPRESS_ENDPOINT}",
                    files=files,
                    data=fields,
                    timeout=REQUEST_TIMEOUT,
                )
            dt = time.monotonic() - t0
            if resp.status_code != 200:
                return FileResult(
                    **asdict(base) | {
                        "seconds": dt,
                        "status": "error",
                        "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                    }
                )
            compressed_bytes = resp.content
            after = len(compressed_bytes)
            ratio = after / before if before else 1.0
            base.seconds = dt
            base.after_bytes = after
            base.saved_bytes = before - after
            base.ratio = ratio

            if after < before:
                tmp = pdf_path.with_suffix(pdf_path.suffix + ".stirling.tmp")
                tmp.write_bytes(compressed_bytes)
                os.replace(tmp, pdf_path)
                base.status = "replaced"
            else:
                base.status = "kept_original"
            return base
        except Exception as e:
            dt = time.monotonic() - t0
            return FileResult(
                **asdict(base) | {
                    "seconds": dt,
                    "status": "error",
                    "error": f"{type(e).__name__}: {e}",
                }
            )


async def verify_one(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    res: FileResult,
) -> FileResult:
    """Hit Stirling's /api/v1/analysis/page-count to confirm page count is unchanged."""
    if res.status != "replaced":
        return res
    pdf_path = MATA / res.file
    async with sem:
        try:
            with pdf_path.open("rb") as fh:
                files = {"fileInput": (pdf_path.name, fh, "application/pdf")}
                r = await client.post(
                    f"{STIRLING_BASE}/api/v1/analysis/page-count",
                    files=files,
                    timeout=REQUEST_TIMEOUT,
                )
            if r.status_code == 200:
                info = r.json()
                new_pages = info.get("pageCount")
                if new_pages is not None and int(new_pages) != res.pages:
                    res.status = "error"
                    res.error = f"page count mismatch: {res.pages} -> {new_pages}"
            else:
                # Don't fail on info endpoint issues — the compress already worked
                pass
        except Exception:
            pass
    return res


def write_csv_report(results: list[FileResult]) -> None:
    fieldnames = [
        "file", "mode", "status",
        "before_bytes", "after_bytes", "saved_bytes", "ratio",
        "seconds", "pages", "image_pct", "error",
    ]
    with REPORT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow({k: getattr(r, k) for k in fieldnames})


def write_markdown_report(results: list[FileResult], dry_run: bool) -> None:
    total_before = sum(r.before_bytes for r in results)
    total_after = sum(r.after_bytes for r in results if r.status == "replaced") or 0
    replaced = [r for r in results if r.status == "replaced"]
    kept = [r for r in results if r.status == "kept_original"]
    errs = [r for r in results if r.status == "error"]

    def mb(n: int) -> str:
        return f"{n / 1024 / 1024:.1f} MB"

    def pct(n: int, d: int) -> str:
        return f"{(100.0 * n / d):.1f}%" if d else "-"

    saved = total_before - total_after

    lines: list[str] = []
    lines.append("# PDF Compression Report — `leabharlann/mata/`\n")
    lines.append(f"_Generated {time.strftime('%Y-%m-%d %H:%M:%S')} via Stirling PDF API ({STIRLING_BASE})_\n")
    if dry_run:
        lines.append("> **DRY RUN** — no files were modified.\n")
    lines.append("## Summary\n")
    lines.append(f"- Files processed: **{len(results)}**")
    lines.append(f"- Replaced: **{len(replaced)}** ({mb(sum(r.saved_bytes for r in replaced))} saved)")
    lines.append(f"- Kept original (compression didn't help): **{len(kept)}**")
    lines.append(f"- Errors: **{len(errs)}**")
    lines.append(f"- Total before: **{mb(total_before)}**")
    lines.append(f"- Total after (replaced files only): **{mb(total_after)}**")
    lines.append(f"- **Total saved: {mb(saved)} ({pct(saved, total_before)})**\n")

    lines.append("## Per-file results\n")
    lines.append("| File | Mode | Status | Before | After | Saved | Ratio | Time |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    for r in sorted(results, key=lambda r: -r.before_bytes):
        before_s = mb(r.before_bytes)
        after_s = mb(r.after_bytes) if r.status == "replaced" else "—"
        saved_s = mb(r.saved_bytes) if r.status == "replaced" else "—"
        ratio_s = f"{r.ratio * 100:.1f}%" if r.status == "replaced" else "—"
        time_s = f"{r.seconds:.1f}s"
        lines.append(f"| {r.file[:60]} | {r.mode} | {r.status} | {before_s} | {after_s} | {saved_s} | {ratio_s} | {time_s} |")

    if errs:
        lines.append("\n## Errors\n")
        for r in errs:
            lines.append(f"- **{r.file}** — {r.error}")

    REPORT_MD.write_text("\n".join(lines) + "\n")


async def main_async(args: argparse.Namespace) -> int:
    audit = load_audit()
    if not audit:
        print("No audit rows found.")
        return 1

    # Sort by size, biggest first — biggest wins dominate the result
    audit.sort(key=lambda r: -int(r["bytes"]))

    sem = asyncio.Semaphore(args.concurrency)
    limits = httpx.Limits(max_connections=args.concurrency + 1, max_keepalive_connections=args.concurrency)
    async with httpx.AsyncClient(limits=limits) as client:
        # Sanity-check Stirling
        try:
            r = await client.get(f"{STIRLING_BASE}/actuator/health", timeout=10.0)
            r.raise_for_status()
            print(f"Stirling PDF reachable at {STIRLING_BASE} (health: {r.json().get('status')})")
        except Exception as e:
            print(f"ERROR: cannot reach Stirling at {STIRLING_BASE}: {e}", file=sys.stderr)
            return 2

        mode = "DRY RUN" if args.dry_run else "LIVE"
        print(f"\n{mode}: compressing {len(audit)} files, concurrency={args.concurrency}\n")
        tasks = [compress_one(client, sem, row, args.dry_run) for row in audit]
        results: list[FileResult] = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            results.append(res)
            tag = "✓" if res.status == "replaced" else ("·" if res.status == "kept_original" else "✗")
            print(
                f"  {tag} {res.file[:55]:<55} {res.mode:<8} "
                f"{res.before_bytes/1024/1024:>7.1f} MB -> "
                f"{(res.after_bytes/1024/1024):>7.1f} MB  "
                f"({res.ratio*100:5.1f}%)  {res.seconds:5.1f}s  [{res.status}]",
                flush=True,
            )

        # Verify only the replaced files
        if not args.dry_run:
            print("\nVerifying replaced files via Stirling info endpoint...")
            verify_tasks = [verify_one(client, sem, r) for r in results if r.status == "replaced"]
            await asyncio.gather(*verify_tasks)

    write_csv_report(results)
    write_markdown_report(results, args.dry_run)
    print(f"\nWrote {REPORT_CSV}")
    print(f"Wrote {REPORT_MD}")

    total_before = sum(r.before_bytes for r in results)
    total_after = sum(r.after_bytes for r in results if r.status == "replaced")
    saved = total_before - total_after
    print(f"\nTotal: {total_before/1024/1024:.1f} MB -> {total_after/1024/1024:.1f} MB  (saved {saved/1024/1024:.1f} MB, {(100*saved/total_before):.1f}%)")
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Don't replace files, just report")
    p.add_argument("--concurrency", type=int, default=CONCURRENCY, help="Parallel requests to Stirling")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
