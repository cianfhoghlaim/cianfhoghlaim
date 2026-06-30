"""DLT filesystem source for the Croilar author personal-document folder.

This source ingests every file under
`<repo_root>/author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/`,
EXCEPT the `zotero/` subdirectory (which is deferred to a future
`zotero_sql` source). The stream is `cv`; the source is marked
`local_only=True` and SHALL NOT upload to R2.

For each file we record:

    {
        "path":       absolute path,
        "subdir":     top-level subdir name (e.g. "achievement"),
        "filename":   basename,
        "ext":        suffix (lowercase, no dot),
        "mtime":      ISO-8601 modification time,
        "size":       bytes,
        "sha256":     hex digest of file content,
        "ingested_at": ISO-8601 ingest time,
    }

One DLT resource per subdirectory is emitted so downstream consumers
can pick a subdir slice. All resources share the same primary key
(`path`).

Why DLT filesystem? The source keeps the streaming, resumable, and
parquet-on-disk semantics of DLT while staying on the local box.
For sensitive corpora (CV PDFs, identity documents) this is the
only acceptable ingest path; nothing leaves the laptop.

Usage:
    from pipelines.fs_author import fs_author_source

    source = fs_author_source()
    load_info = pipeline.run(source)
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
from _shared.config.paths import get_author_dir, resolve_path

CHUNK_SIZE = 1 << 16  # 64 KiB


def _default_exclude() -> tuple[str, ...]:
    return ("zotero/",)


def _default_subresources() -> tuple[str, ...]:
    return (
        "achievement",
        "catharnacht",
        "deacy",
        "disability",
        "gemini_deep_research",
        "identity",
        "politics",
        "teaching",
        "university_of_galway",
        "vetting",
    )


def _is_excluded(path: Path, excludes: tuple[str, ...]) -> bool:
    p = str(path).replace("\\", "/")
    return any(ex in p for ex in excludes)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_for(path: Path, author_root: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError:
        return {}
    rel = path.relative_to(author_root)
    subdir = rel.parts[0] if len(rel.parts) > 1 else ""
    return {
        "path": str(path),
        "subdir": subdir,
        "filename": path.name,
        "ext": path.suffix.lstrip(".").lower(),
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "size": stat.st_size,
        "sha256": _sha256(path),
        "ingested_at": datetime.now(tz=UTC).isoformat(),
    }


def fs_author_source(
    author_root: str | Path | None = None,
    excludes: tuple[str, ...] | None = None,
    subresources: tuple[str, ...] | None = None,
) -> list[Any]:
    """Return one DLT resource per top-level subdirectory of the author folder.

    Args:
        author_root: Absolute path to the author folder. Defaults to
            `<repo_root>/author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/`.
            Can be overridden via the `CROILAR_AUTHOR_ROOT` env var.
        excludes: Path fragments to skip (substring match). Defaults to
            `("zotero/",)`.
        subresources: Explicit list of subdir names to emit as resources.
            If None, every top-level subdir except those in `excludes` is used.

    Returns:
        A list of DLT resources (one per subdir). Each resource has
        `table_name=f"fs_author_{subdir}"`, `write_disposition="replace"`,
        and `primary_key="path"`.
    """
    if author_root is None:
        env = os.environ.get("CROILAR_AUTHOR_ROOT")
        author_root = resolve_path(env) if env else get_author_dir()

    author_root = Path(author_root).expanduser().resolve()
    if not author_root.exists():
        raise FileNotFoundError(f"author root does not exist: {author_root}")

    excl = excludes if excludes is not None else _default_exclude()

    if subresources is None:
        subresources = _default_subresources()

    out: list[Any] = []

    for subdir in subresources:
        sub_path = author_root / subdir
        if not sub_path.exists() or not sub_path.is_dir():
            continue

        def _make_resource(d: str = subdir) -> Any:
            @dlt.resource(
                name=f"fs_author_{d}",
                write_disposition="replace",
                primary_key="path",
            )
            def _iter() -> Iterator[dict[str, Any]]:
                root = author_root / d
                for child in sorted(root.rglob("*")):
                    if not child.is_file():
                        continue
                    if _is_excluded(child, excl):
                        continue
                    rec = _record_for(child, author_root)
                    if rec:
                        yield rec

            return _iter

        out.append(_make_resource())

    return out


def run_fs_author_pipeline(
    author_root: str | Path | None = None,
    destination: str | Any | None = None,
    dataset_name: str = "fs_author_data",
) -> Any:
    """Run the full author-folder filesystem ingestion pipeline.

    Always uses a LOCAL DuckDB destination — never R2. The dataset
    lives at `./data/local/fs_author.duckdb` by default.
    """
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination(local_only=True)

    pipeline = dlt.pipeline(
        pipeline_name="fs_author_croilar",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    return pipeline.run(fs_author_source(author_root=author_root))


__all__ = [
    "fs_author_source",
    "run_fs_author_pipeline",
]
