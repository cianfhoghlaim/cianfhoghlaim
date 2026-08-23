"""
Leabharlann education notes — the cross-repo DLT source.

Bridges the `leabharlann/` separate repo (the personal archive) into
the Cianfhoghlaim lakehouse. The leabharlann/ repo contains:
  - leabharlann/ollscoil_na_gaillimhe/  (University of Galway notes)
  - leabharlann/mata/                  (maths notes)
  - leabharlann/ccs/                   (computer science notes)
  - leabharlann/gaeilge/               (Irish language notes)
  - leabharlann/aigne/                 (poetry)

This source reads the leabharlann/ filesystem (via the
`LEABHARLANN_PATH` env var) and emits a single DLT resource
`leabharlann_education_notes` that joins the personal archive to
the BIEP v3 5-phase pattern.

Reference: per the 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1
audit (Decision 3) — the cross-repo bridge for leabharlann maths + CS notes.

This is a DLT source stub — the actual file enumeration is implemented
in a follow-up change that adds the per-corpus leabharlann sources.
"""
from __future__ import annotations

import os
from pathlib import Path

import dlt


@dlt.source
def leabharlann_education_notes(
    leabharlann_path: str = os.environ.get("LEABHARLANN_PATH", "/leabharlann"),
):
    """Cross-repo DLT source for the leabharlann/ personal archive."""
    leabharlann = Path(leabharlann_path)
    if not leabharlann.exists():
        # Idempotent: emit empty resource if leabharlann/ is not mounted
        @dlt.resource(write_disposition="replace", name="leabharlann_education_notes")
        def empty_resource():
            return []

        return empty_resource

    @dlt.resource(
        write_disposition="merge",
        primary_key="file_hash",
        name="leabharlann_education_notes",
    )
    def leabharlann_notes():
        """Enumerate every leabharlann/ education file with subject + level."""
        import hashlib

        notes = []
        for subdir in ("mata", "ccs", "gaeilge", "aigne", "ollscoil_na_gaillimhe"):
            sub_path = leabharlann / subdir
            if not sub_path.exists():
                continue
            for f in sub_path.rglob("*"):
                if not f.is_file():
                    continue
                # Skip hidden + non-text files
                if f.name.startswith(".") or f.suffix.lower() in {
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".heic",
                    ".pdf",
                }:
                    continue
                try:
                    content = f.read_text(errors="ignore")
                except (UnicodeDecodeError, OSError):
                    continue
                file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                notes.append(
                    {
                        "file_hash": file_hash,
                        "file_path": str(f.relative_to(leabharlann)),
                        "subject": subdir,
                        "file_size": f.stat().st_size,
                        "snippet": content[:500],
                    }
                )
        yield notes

    return leabharlann_notes
