"""
Takeout path configuration for `google_takeout.py`.

Per-account configuration is loaded from a YAML file (default:
`./author_archive_accounts.yaml` at the repo root, override with the
`AUTHOR_ARCHIVE_ACCOUNTS_PATH` environment variable). The file is optional;
an empty / missing file yields zero accounts and the takeout source becomes
a no-op (it logs a warning, never fails).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# Default account domains the user is likely to use.
DEFAULT_TAKEOUT_DOMAINS: set[str] = {
    "drive",
    "gmail",
    "docs",
    "gemini",
    "keep",
    "photos",
    "other",
}


@dataclass(frozen=True)
class TakeoutAccountConfig:
    """
    One Google account's takeout configuration.

    Attributes:
        account_label: Short label used in DuckDB `account` column
            (e.g. "cian_personal", "cian_academic").
        takeout_path: Absolute or repo-relative path to the extracted
            `Takeout/<account_label>/` directory.
        default_domain: One of the Takeout product areas (`drive`, `gmail`,
            `docs`, `gemini`, `keep`, `photos`, `other`). Used to populate
            the `domain` column when a file's relative path doesn't already
            encode one.
        gpg_encrypt_paths: List of relative-path prefixes whose content SHALL
            be GPG-encrypted before storage. Empty by default. See
            `google-takeout-ingestion` spec.
    """

    account_label: str
    takeout_path: Path
    default_domain: str = "other"
    gpg_encrypt_paths: list[str] = field(default_factory=list)

    def is_gpg_path(self, relative_path: str) -> bool:
        """Return True if `relative_path` matches one of the GPG prefixes."""
        rel = relative_path.lstrip("/")
        for prefix in self.gpg_encrypt_paths:
            clean_prefix = prefix.lstrip("/").rstrip("/")
            if not clean_prefix:
                continue
            if rel == clean_prefix or rel.startswith(clean_prefix + "/"):
                return True
        return False


@dataclass
class TakeoutAccounts:
    """Collection of `TakeoutAccountConfig`, loaded from a YAML file."""

    accounts: list[TakeoutAccountConfig] = field(default_factory=list)

    def __iter__(self) -> Iterator[TakeoutAccountConfig]:  # type: ignore[override]
        return iter(self.accounts)

    def __len__(self) -> int:
        return len(self.accounts)

    def __bool__(self) -> bool:
        return bool(self.accounts)


def _try_load_yaml() -> Any | None:
    """Lazy-load PyYAML; return None if not installed."""
    try:
        import yaml  # type: ignore[import-untyped]

        return yaml
    except ImportError:
        logger.warning("yaml_not_available_takeout_config_disabled")
        return None


def _parse_account_entry(entry: dict[str, Any]) -> TakeoutAccountConfig | None:
    """Parse one YAML entry into a `TakeoutAccountConfig`, validating required keys."""
    label = entry.get("account_label")
    raw_path = entry.get("takeout_path")
    if not label or not raw_path:
        logger.warning(
            "takeout_account_entry_invalid",
            entry=entry,
            reason="missing account_label or takeout_path",
        )
        return None

    takeout_path = Path(raw_path).expanduser()
    if not takeout_path.is_absolute():
        # Resolve relative paths against the repo root (parent of the YAML file).
        # The YAML is usually at the repo root, so we resolve against CWD.
        takeout_path = (Path.cwd() / takeout_path).resolve()

    default_domain = entry.get("default_domain", "other")
    if default_domain not in DEFAULT_TAKEOUT_DOMAINS:
        logger.warning(
            "takeout_default_domain_unknown",
            account_label=label,
            default_domain=default_domain,
            allowed=sorted(DEFAULT_TAKEOUT_DOMAINS),
        )
        default_domain = "other"

    gpg_paths = entry.get("gpg_encrypt_paths", []) or []

    return TakeoutAccountConfig(
        account_label=str(label),
        takeout_path=takeout_path,
        default_domain=str(default_domain),
        gpg_encrypt_paths=[str(p) for p in gpg_paths],
    )


def load_takeout_accounts(
    config_path: str | Path | None = None,
) -> TakeoutAccounts:
    """
    Load takeout account configuration from a YAML file.

    Args:
        config_path: Override path. If None, uses `AUTHOR_ARCHIVE_ACCOUNTS_PATH`
            env var or the default `./author_archive_accounts.yaml` at CWD.

    Returns:
        A `TakeoutAccounts` collection (empty if the file is missing/empty/invalid).
    """
    yaml = _try_load_yaml()
    if yaml is None:
        return TakeoutAccounts()

    if config_path is None:
        config_path = os.environ.get(
            "AUTHOR_ARCHIVE_ACCOUNTS_PATH",
            str(Path.cwd() / "author_archive_accounts.yaml"),
        )

    path = Path(config_path)
    if not path.exists():
        logger.info("takeout_config_file_absent", path=str(path))
        return TakeoutAccounts()

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (OSError, UnicodeDecodeError) as parse_err:
        logger.warning(
            "takeout_config_parse_failed",
            path=str(path),
            error=str(parse_err),
        )
        return TakeoutAccounts()

    entries = data.get("accounts", []) if isinstance(data, dict) else []
    accounts: list[TakeoutAccountConfig] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        cfg = _parse_account_entry(entry)
        if cfg is not None:
            accounts.append(cfg)

    if not accounts:
        logger.info("takeout_config_empty", path=str(path))

    return TakeoutAccounts(accounts=accounts)


__all__ = [
    "DEFAULT_TAKEOUT_DOMAINS",
    "TakeoutAccountConfig",
    "TakeoutAccounts",
    "load_takeout_accounts",
]
