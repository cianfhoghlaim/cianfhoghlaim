"""
Audit every PDF in leabharlann/mata/ and emit a profile CSV.

Read-only — never modifies files. Uses pymupdf to walk each PDF and tally:
  - bytes, pages, pdf_version
  - image_count, image_bytes_total, image_pct_of_file
  - font_count, font_bytes_total
  - has_acroform (will benefit from flatten)
  - is_image_heavy, recommended_mode

Output:
  - leabharlann/mata/.compression_audit.csv   (gitignored)
  - prints a markdown table to stdout

Usage:
  uv run --with pymupdf python scripts/audit_leabharlann_mata.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterator

import pymupdf

MATA = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/mata")
AUDIT_CSV = MATA / ".compression_audit.csv"

IMAGE_HEAVY_THRESHOLD = 0.40  # >=40% of bytes are embedded images


def profile(pdf_path: Path) -> dict:
    doc = pymupdf.open(pdf_path)
    try:
        meta = doc.metadata or {}
        pages = doc.page_count
        format_str = meta.get("format", "") or ""
        pdf_version = format_str.replace("PDF ", "").strip() or "?"

        image_count = 0
        image_bytes = 0
        font_count = 0
        font_bytes = 0

        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                image_count += 1
                image_bytes += len(info.get("image", b""))

            for f in page.get_fonts(full=True):
                # f = (xref, ext, type, basefont, name, encoding, ?)
                xref = f[0]
                try:
                    buf = doc.extract_font(xref)
                    # buf = (basefont, ext, type, content_bytes)
                    content = buf[3] if isinstance(buf, tuple) and len(buf) >= 4 else b""
                    if content:
                        font_count += 1
                        font_bytes += len(content)
                except Exception:
                    continue

        has_acroform = bool(getattr(doc, "is_form_pdf", False))
    finally:
        doc.close()

    file_bytes = pdf_path.stat().st_size
    image_pct = (image_bytes / file_bytes) if file_bytes else 0.0
    is_image_heavy = image_pct >= IMAGE_HEAVY_THRESHOLD

    return {
        "file": pdf_path.name,
        "bytes": file_bytes,
        "mb": round(file_bytes / 1024 / 1024, 2),
        "pages": pages,
        "pdf_version": str(pdf_version),
        "image_count": image_count,
        "image_bytes": image_bytes,
        "image_pct": round(image_pct * 100, 1),
        "font_count": font_count,
        "font_bytes": font_bytes,
        "has_acroform": has_acroform,
        "is_image_heavy": is_image_heavy,
        "recommended_mode": "lossy" if is_image_heavy else "lossless",
    }


def iter_pdfs(root: Path) -> Iterator[Path]:
    for p in sorted(root.glob("*.pdf")):
        if p.name.startswith("."):
            continue
        yield p


def print_markdown_table(rows: list[dict]) -> None:
    print("\n## PDF Audit — leabharlann/mata/\n")
    print(f"  Total files: {len(rows)}")
    print(f"  Total size:  {sum(r['bytes'] for r in rows) / 1024 / 1024:.1f} MB")
    img_heavy = [r for r in rows if r["is_image_heavy"]]
    print(f"  Image-heavy (>={int(IMAGE_HEAVY_THRESHOLD * 100)}% image bytes): {len(img_heavy)}")
    print()
    header = "| File | MB | Pages | Imgs | Img % | Fonts | Form | Mode |"
    sep = "|---|---:|---:|---:|---:|---:|:---:|:---:|"
    print(header)
    print(sep)
    for r in sorted(rows, key=lambda r: -r["bytes"]):
        form = "Y" if r["has_acroform"] else "-"
        print(
            f"| {r['file'][:60]} | {r['mb']} | {r['pages']} | "
            f"{r['image_count']} | {r['image_pct']} | {r['font_count']} | {form} | "
            f"{r['recommended_mode']} |"
        )
    print()


def main() -> int:
    if not MATA.is_dir():
        print(f"ERROR: {MATA} is not a directory", file=sys.stderr)
        return 1

    pdfs = list(iter_pdfs(MATA))
    if not pdfs:
        print("No PDFs found")
        return 0

    print(f"Auditing {len(pdfs)} PDFs in {MATA}...")
    rows: list[dict] = []
    for i, p in enumerate(pdfs, 1):
        try:
            row = profile(p)
            rows.append(row)
            print(f"  [{i}/{len(pdfs)}] {p.name[:60]:<60}  {row['mb']} MB  pages={row['pages']}  imgs={row['image_count']}", flush=True)
        except Exception as e:
            print(f"  SKIP {p.name}: {e}", file=sys.stderr)
    print()

    fieldnames = [
        "file", "bytes", "mb", "pages", "pdf_version",
        "image_count", "image_bytes", "image_pct",
        "font_count", "font_bytes",
        "has_acroform", "is_image_heavy", "recommended_mode",
    ]
    with AUDIT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {AUDIT_CSV}")
    print_markdown_table(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
