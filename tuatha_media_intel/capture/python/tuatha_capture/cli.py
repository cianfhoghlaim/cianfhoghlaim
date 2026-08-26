"""the CLI entry point. Uses cyclopts for a clean subcommand surface."""
from __future__ import annotations

import sys
from pathlib import Path

import cyclopts


from .gba import gba_doctor, gba_capture
from .comic import comic_doctor, comic_ingest


app = cyclopts.App(
    name="tuatha-capture",
    help="Python capture shims for the Tuatha media-intel pipeline.",
    version="0.1.0",
)


@app.command
def doctor():
    """Verify permissions + deps for both the GBA + comic pipelines."""
    print("==> tuatha-capture doctor")
    print()
    gba_doctor()
    print()
    comic_doctor()
    print()
    print("==> doctor: healthy")


@app.command
def gba(
    rom: Path,
    save: Path,
    out_dir: Path,
    *,
    frames: int = 60,
    fps: int = 30,
):
    """Headless mGBA playthrough capture.

    Loads <rom> + <save>, advances N frames at <fps>, writes PNGs to
    <out_dir>/frame-NNNNNN.png. Designed for reproducible GBA capture.
    """
    gba_capture(rom=rom, save=save, out_dir=out_dir, frames=frames, fps=fps)


@app.command
def comic(
    cbz_dir: Path,
    out_dir: Path,
    *,
    panel_detector: str = "deeppanel",
):
    """Walk a directory of .cbz files, extract pages, write them to <out_dir>."""
    comic_ingest(cbz_dir=cbz_dir, out_dir=out_dir, panel_detector=panel_detector)


def main() -> int:
    try:
        app()
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
