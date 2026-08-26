"""tuatha_capture — Python capture shims for the Tuatha media-intel pipeline.

Three subcommands:
  - tuatha-capture gba <rom> <save> <out_dir>   (headless mGBA playthrough)
  - tuatha-capture comic <cbz_dir> <out_dir>   (CBZ panel extractor)
  - tuatha-capture doctor                      (permissions + deps check)

Both GBA + comic flows honor the shippable=false invariant:
raw frames live only in the private Pangolin volume; the CocoIndex
flow re-extracts structured fields via BAML.
"""
from __future__ import annotations

from .cli import app

__all__ = ["app"]
__version__ = "0.1.0"
