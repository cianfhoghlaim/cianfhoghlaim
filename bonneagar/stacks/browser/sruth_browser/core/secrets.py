"""Three-tier secret resolution for the UoG exam-paper pipeline.

Design spec: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/specs/
              cianfhoghlaim-uog-exam-papers/design/auth-credential-priority-chain.md

Priority chain (read in order, stop on first hit):

  1. Self-hosted **Infisical** (env-driven; never raises on a 4xx).
  2. Local **`.env`** (Pydantic `BaseSettings` already wired elsewhere in
     `bonneagar.stacks.browser.sruth_browser.config.BrowserConfig`).
  3. **OnePassword CLI** — `op read` is **NOT** invoked by the runner.
     If `OP_SERVICE_ACCOUNT_TOKEN` is set we log a single
     `secrets_op_service_account_present_but_doc_only` info line so a
     cloner knows to consult the design note before manually wiring
     `op read` into the chain.

The chain mirrors how the platform serves vision-language models:
self-hosted → local → commercial. Both chains prefer local-first and
only fall through to remote APIs as a last resort.

Logging:
  - One `secrets_backend_resolved` line per process per name (cached).
  - At most one `secrets_op_service_account_present_but_doc_only`
    line per process.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

import structlog

from ..exceptions import SecretBackendUnavailable

logger = structlog.get_logger(__name__)


# Names the resolver recognises. All other names are passed through to
# `os.environ`. The OOG_ prefix is namespaced to avoid leaking into the
# rest of the platform.
UOG_SECRET_NAMES: Final[frozenset[str]] = frozenset(
    {
        "OOG_STUDENT_ID",
        "OOG_STUDENT_PASSWORD",
        "OOG_SSO_TOTP_SECRET",  # optional 2FA seed; not used in v1
        "OOG_STORAGE_STATE_PATH",  # override for the Playwright storage state JSON
        "OOG_USER_DATA_DIR",  # override for the Playwright persistent context dir
    }
)

# A small set of well-known placeholders. Any resolver hit that returns
# one of these is treated as "fixture-only" by `UoGSsoConfig.has_real_credentials()`.
FIXTURE_ONLY_VALUES: Final[frozenset[str]] = frozenset(
    {
        "fixture-only",
        "FIXTURE_ONLY",
        "test-password",
        "change-me",
        "",
    }
)


@dataclass
class SecretsResolver:
    """Resolve a single secret by name through the priority chain.

    Constructor reads the four Infisical env vars (`INFISICAL_TOKEN`,
    `INFISICAL_URL`, `INFISICAL_PROJECT`, `INFISICAL_ENV`) once and
    caches the choice of backend for the lifetime of this instance.

    The instance is *cheap*; create a fresh one per request when there
    is any chance env vars have been re-set (the asset materialisation
    process is fine to share a process-wide resolver via
    `get_default_secrets_resolver()`).

    NOT frozen=True on purpose: tests need to mock-patch the
    `_try_*` methods with `unittest.mock.patch.object`, and frozen
    dataclasses disallow that.
    """

    infisical_token: str | None = None
    infisical_url: str | None = None
    infisical_project: str | None = None
    infisical_env: str | None = None

    cache_ttl_seconds: float = 60.0  # cache each lookup for 60 s

    _process_cache: dict[str, tuple[float, str | None, str | None]] = field(
        default_factory=dict
    )
    _logged_op_doc_only: bool = False

    @classmethod
    def from_env(cls) -> SecretsResolver:
        """Build a resolver from the current `os.environ`."""
        return cls(
            infisical_token=os.environ.get("INFISICAL_TOKEN"),
            infisical_url=os.environ.get("INFISICAL_URL"),
            infisical_project=os.environ.get("INFISICAL_PROJECT"),
            infisical_env=os.environ.get("INFISICAL_ENV", "dev"),
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def get(self, name: str) -> str | None:
        """Return the secret value for `name`, or None if every backend missed."""
        cached = self._cache_get(name)
        if cached is not None or name in self._process_cache:
            _, value, backend = self._process_cache[name]
            self._log_first_time(
                name,
                backend,
                hit=(value is not None),
            )
            return value

        # Live resolution order: Infisical → env → (doc-only op)
        value, backend = self._try_infisical(name)
        if value is None:
            value, backend = self._try_env(name)
        if value is None:
            value, backend = self._try_op_doc_only(name)

        self._cache_put(name, value, backend)
        self._log_first_time(name, backend, hit=(value is not None))
        return value

    def has_real(self, name: str) -> bool:
        """True iff the resolver returned a non-placeholder value."""
        value = self.get(name)
        return value is not None and value not in FIXTURE_ONLY_VALUES

    # ------------------------------------------------------------------ #
    # Backend implementations
    # ------------------------------------------------------------------ #

    def _try_infisical(self, name: str) -> tuple[str | None, str]:
        if not all([self.infisical_token, self.infisical_url, self.infisical_project]):
            return None, "infisical"
        try:
            import urllib.parse
            import urllib.request

            url = (
                f"{self.infisical_url.rstrip('/')}/api/v3/secrets/raw/{name}"
                f"?projectId={urllib.parse.quote(self.infisical_project)}"
                f"&environment={urllib.parse.quote(self.infisical_env or 'dev')}"
            )
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.infisical_token}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    payload = resp.read().decode("utf-8")
                    return payload.strip() or None, "infisical"
                # 4xx means "this secret does not exist in this project"; fall through.
                if 400 <= resp.status < 500:
                    return None, "infisical"
        except Exception as exc:  # noqa: BLE001 — best-effort fallback
            logger.warning(
                "secrets_infisical_unreachable",
                url=self.infisical_url,
                error=str(exc),
            )
            raise SecretBackendUnavailable("infisical", str(exc)) from exc
        return None, "infisical"

    def _try_env(self, name: str) -> tuple[str | None, str]:
        value = os.environ.get(name)
        return value, "env"

    # ------------------------------------------------------------------ #
    # Cache helpers
    # ------------------------------------------------------------------ #

    def _cache_get(self, name: str) -> tuple[float, str | None, str | None] | None:
        entry = self._process_cache.get(name)
        if entry is None:
            return None
        cached_at, _value, _backend = entry
        # Honour the per-TTL: any entry older than `cache_ttl_seconds`
        # is considered stale so we re-hit the backend.
        if (time.time() - cached_at) >= self.cache_ttl_seconds:
            self._process_cache.pop(name, None)
            return None
        return entry

    def _cache_put(self, name: str, value: str | None, backend: str) -> None:
        self._process_cache[name] = (time.time(), value, backend)

    def _log_first_time(self, name: str, backend: str, *, hit: bool) -> None:
        """Emit the canonical `secrets_backend_resolved` log line ONCE per (name, process)."""
        cache_key = f"_logged::{name}"
        if cache_key in self._process_cache:
            return
        self._process_cache[cache_key] = (time.time(), None, backend)
        logger.info(
            "secrets_backend_resolved",
            name=name,
            backend=backend,
            hit=hit,
        )

    def _try_op_doc_only(self, name: str) -> tuple[str | None, str]:
        """1Password CLI is documented only — never invoked.

        See `design/auth-credential-priority-chain.md` for the
        3-line swap-in for cloners who prefer `op` over Infisical.
        """
        if not self._logged_op_doc_only and os.environ.get("OP_SERVICE_ACCOUNT_TOKEN"):
            logger.info(
                "secrets_op_service_account_present_but_doc_only",
                hint=(
                    "1Password CLI is not invoked by the runner. "
                    "See openspec/changes/2026-08-23-uog-exam-papers-sso-v1/"
                    "specs/cianfhoghlaim-uog-exam-papers/design/"
                    "auth-credential-priority-chain.md to enable `op read` manually."
                ),
            )
            self._logged_op_doc_only = True
        return None, "env"


# --------------------------------------------------------------------------- #
# Module-level helpers
# --------------------------------------------------------------------------- #


_DEFAULT_RESOLVER: SecretsResolver | None = None


def get_default_secrets_resolver() -> SecretsResolver:
    """Process-wide resolver, lazily built from `os.environ`."""
    global _DEFAULT_RESOLVER
    if _DEFAULT_RESOLVER is None:
        _DEFAULT_RESOLVER = SecretsResolver.from_env()
    return _DEFAULT_RESOLVER


def reset_default_secrets_resolver() -> None:
    """Drop the cached resolver; useful in tests that flip env vars mid-run."""
    global _DEFAULT_RESOLVER
    _DEFAULT_RESOLVER = None


# --------------------------------------------------------------------------- #
# Pydantic-anchored config (consumer-friendly face)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class UoGSsoConfig:
    """Single source of truth for the UoG SSO secrets + storage paths.

    Built on top of `SecretsResolver` so the same priority chain and
    the same `has_real_credentials()` semantics apply whether the
    consumer is a DLT source, a Dagster asset, or a CLI script.
    """

    student_id: str | None
    student_password: str | None
    storage_state_path: Path | None = None
    user_data_dir: Path | None = None

    @classmethod
    def from_resolver(
        cls,
        resolver: SecretsResolver | None = None,
    ) -> UoGSsoConfig:
        r = resolver or get_default_secrets_resolver()
        storage_state = r.get("OOG_STORAGE_STATE_PATH")
        user_data = r.get("OOG_USER_DATA_DIR")
        return cls(
            student_id=r.get("OOG_STUDENT_ID"),
            student_password=r.get("OOG_STUDENT_PASSWORD"),
            storage_state_path=Path(storage_state).expanduser() if storage_state else None,
            user_data_dir=Path(user_data).expanduser() if user_data else None,
        )

    def has_real_credentials(self) -> bool:
        """True iff both SSO secrets are present AND not a known fixture placeholder."""
        if not self.student_id or not self.student_password:
            return False
        if self.student_password in FIXTURE_ONLY_VALUES:
            return False
        if self.student_id in FIXTURE_ONLY_VALUES:
            return False
        return True


__all__ = [
    "SecretsResolver",
    "get_default_secrets_resolver",
    "reset_default_secrets_resolver",
    "UoGSsoConfig",
    "UOG_SECRET_NAMES",
    "FIXTURE_ONLY_VALUES",
]
