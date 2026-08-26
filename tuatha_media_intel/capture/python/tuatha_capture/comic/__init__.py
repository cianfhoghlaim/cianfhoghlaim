"""Comic book panel extractor — walks CBZ files, emits page PNGs.

For each .cbz in cbz_dir:
  1. Open the archive (CBZ = ZIP; pages are JPEG/PNG/WEBP)
  2. Render each page to PNG (decompress to disk)
  3. Run optional panel detection (DeepPanel ML model)
  4. Extract the dominant color palette per page (k-means k=6)
  5. Write a per-page metadata JSONL alongside the PNGs

shippable=false invariant: page PNGs go to the private Pangolin-backed
out_dir only; the metadata JSONL is what the CocoIndex flow consumes.
The BAML ExtractComicParticle function then operates on a downsampled
≤768px thumb from the same per-page PNG.
"""
from __future__ import annotations

import json
import pathlib
import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from io import BytesIO

import structlog

log = structlog.get_logger("tuatha_capture.comic")


def comic_doctor() -> None:
    """Verify Pillow + comicbox + (optional) DeepPanel availability."""
    try:
        import PIL  # type: ignore[import-not-found]

        print(f"[ok ] Pillow {PIL.__version__}")
    except ImportError:
        print("[err] Pillow not installed — run: uv pip install pillow")

    try:
        import comicbox  # type: ignore[import-not-found]

        print(f"[ok ] comicbox {comicbox.__version__}")
    except ImportError:
        print("[warn] comicbox not installed — run: uv pip install comicbox")

    try:
        import deeppanel  # type: ignore[import-not-found]

        print(f"[ok ] deeppanel available ({deeppanel.__version__})")
    except ImportError:
        print(
            "[warn] deeppanel not installed — panel extraction skipped\n"
            "       install via: uv pip install deeppanel-ml (optional)"
        )


def comic_ingest(
    *,
    cbz_dir: pathlib.Path,
    out_dir: pathlib.Path,
    panel_detector: str = "deeppanel",
) -> dict[str, int]:
    """Walk a directory of CBZ files, write pages + metadata to out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pages_out = out_dir / "pages"
    pages_out.mkdir(exist_ok=True)
    meta_out = out_dir / "pages.jsonl"

    counts = {"issues": 0, "pages": 0, "panels": 0}

    with meta_out.open("w") as meta_f:
        for cbz in sorted(cbz_dir.rglob("*.cbz")):
            issue_id = cbz.stem
            counts["issues"] += 1
            log.info("comic_ingest_started", cbz=str(cbz), issue_id=issue_id)
            for page_idx, page_bytes in enumerate(_iter_cbz_pages(cbz)):
                page_no = page_idx + 1
                out_png = pages_out / f"{issue_id}-page-{page_no:03d}.png"
                _render_page(page_bytes, out_png)
                counts["pages"] += 1

                palette = _dominant_palette(out_png, k=6)

                meta = {
                    "issue_id": issue_id,
                    "page_number": page_no,
                    "source_path": str(out_png.relative_to(out_dir)),
                    "color_palette": palette,
                    "ingested_at": datetime.now(UTC).isoformat(),
                }
                meta_f.write(json.dumps(meta) + "\n")
    log.info("comic_ingest_done", counts=counts)
    return counts


def _iter_cbz_pages(cbz: pathlib.Path) -> Iterator[bytes]:
    """Yield each page's bytes in archive order."""
    with zipfile.ZipFile(cbz) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            with z.open(name) as f:
                yield f.read()


def _render_page(page_bytes: bytes, out_png: pathlib.Path) -> None:
    from PIL import Image

    img = Image.open(BytesIO(page_bytes))
    img.convert("RGB").save(out_png, "PNG", optimize=True)


def _dominant_palette(png_path: pathlib.Path, *, k: int = 6) -> list[str]:
    """k-means dominant colors, returned as hex strings."""
    from PIL import Image

    from sklearn.cluster import KMeans  # type: ignore[import-not-found]

    img = Image.open(png_path).convert("RGB")
    small = img.resize((128, 128))
    arr = __import__("numpy").asarray(small).reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, n_init=4, random_state=42)
    kmeans.fit(arr)
    centers = kmeans.cluster_centers_.astype(int)
    centers.sort(axis=0)
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, in centers.tolist() for b in [centers[0, 2]]]
