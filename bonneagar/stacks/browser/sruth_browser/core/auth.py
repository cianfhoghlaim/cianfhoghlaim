"""Browser-side SSO login for the University of Galway Campus Identity portal.

Design spec: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/specs/
              cianfhoghlaim-uog-exam-papers/design/auth-credential-priority-chain.md

This module is **only** responsible for the login round-trip. It does not
know about DLT, Dagster, or anything else. Once authenticated, the
caller receives a Playwright `Page` whose storage state should be
persisted for the next run.

Persistent-context flow:

  +-----------------+       +----------------+       +--------------------+
  | SecretsResolver | ----> | UoGSsoLogin    | ----> | Playwright context |
  +-----------------+       | login(page, …) |       +--------------------+
                            +----------------+              |
                                                             v
                          +--------------------+      +----------------+
                          | storage_state.json | <--  | user_data_dir  |
                          +--------------------+      +----------------+

When `UoGSsoConfig.has_real_credentials() == False`, `login()` is a
no-op: it returns immediately and the caller is expected to handle the
fixture-only mode (write a `skipped_fixture` row to DLT instead of
launching Playwright).
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from ..exceptions import UoGAuthExpired
from .secrets import UoGSsoConfig

logger = structlog.get_logger(__name__)


UOG_SSO_BASE_URL: str = "https://auth.universityofgalway.ie"
UOG_SSO_LOGIN_URL: str = f"{UOG_SSO_BASE_URL}/idp/profile/SAML2/Redirect/SSO"
UOG_SSO_HEALTH_URL: str = "https://exams.universityofgalway.ie/"


@dataclass
class LoginResult:
    """Outcome of a single `UoGSsoLogin.login()` invocation."""

    authenticated: bool
    auth_kind: str  # "fresh" | "cached" | "fixture_only" | "failed"
    elapsed_ms: float
    error: str | None = None

    @classmethod
    def fixture_only(cls) -> LoginResult:
        return cls(
            authenticated=False,
            auth_kind="fixture_only",
            elapsed_ms=0.0,
        )


class UoGSsoLogin:
    """Log into the UoG Campus Identity portal once per process.

    Construct with a `UoGSsoConfig`; the same instance can be reused
    across multiple `login()` calls (the persistent context is the
    cache, not this Python object).
    """

    def __init__(self, config: UoGSsoConfig | None = None) -> None:
        self.config = config or UoGSsoConfig.from_resolver()

    async def login(self, page) -> LoginResult:  # type: ignore[no-untyped-def]
        """Drive a Playwright `page` through the SSO flow.

        Returns a `LoginResult`. In fixture-only mode the page is
        untouched and a `fixture_only` result is returned.
        """
        import time as _time

        if not self.config.has_real_credentials():
            logger.info(
                "uog_sso_skipped_fixture_only",
                hint="UoGSsoConfig.has_real_credentials()==False; "
                "caller is expected to write a `skipped_fixture` row.",
            )
            return LoginResult.fixture_only()

        t0 = _time.perf_counter()
        try:
            # 1. Try the cached health check first. If the persistent
            #    context already has a valid SSO cookie, we can skip
            #    the round-trip entirely.
            if await self._health_check_cached(page):
                elapsed_ms = (_time.perf_counter() - t0) * 1000
                logger.info(
                    "uog_sso_login_ok",
                    auth_kind="cached",
                    elapsed_ms=elapsed_ms,
                )
                return LoginResult(
                    authenticated=True,
                    auth_kind="cached",
                    elapsed_ms=elapsed_ms,
                )

            # 2. Walk through the SAML dance.
            await page.goto(UOG_SSO_HEALTH_URL, wait_until="load", timeout=30_000)
            # The SAML IdP redirects to a login form; we used
            # Stagehand-friendly `act()` semantics elsewhere; here we
            # fall back to native Playwright locators because the
            # login page is well-known and stable.
            await page.fill(
                "input[name='username']", self.config.student_id or ""
            )
            await page.fill(
                "input[name='password']", self.config.student_password or ""
            )
            await page.click("button[type='submit']")
            # Wait for the redirect back to the exams portal.
            await page.wait_for_url(
                f"{UOG_SSO_HEALTH_URL}**",
                timeout=30_000,
            )

            # 3. Save storage state for next time.
            if self.config.storage_state_path:
                self.config.storage_state_path.parent.mkdir(
                    parents=True, exist_ok=True
                )
                await page.context.storage_state(
                    path=str(self.config.storage_state_path)
                )

            elapsed_ms = (_time.perf_counter() - t0) * 1000
            logger.info(
                "uog_sso_login_ok",
                auth_kind="fresh",
                elapsed_ms=elapsed_ms,
            )
            return LoginResult(
                authenticated=True,
                auth_kind="fresh",
                elapsed_ms=elapsed_ms,
            )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = (_time.perf_counter() - t0) * 1000
            logger.error(
                "uog_sso_login_failed",
                error=str(exc),
                elapsed_ms=elapsed_ms,
            )
            raise UoGAuthExpired(f"UoG SSO login failed: {exc}") from exc

    async def _health_check_cached(self, page) -> bool:  # type: ignore[no-untyped-def]
        """Return True if the cached cookie can already reach the exams portal."""
        try:
            resp = await page.goto(
                UOG_SSO_HEALTH_URL,
                wait_until="domcontentloaded",
                timeout=5_000,
            )
            if resp is None:
                return False
            if resp.status == 200 and "Sign in" not in (await page.content()):
                return True
        except Exception:  # noqa: BLE001 — best-effort health check
            return False
        return False


__all__ = ["UoGSsoLogin", "LoginResult", "UOG_SSO_BASE_URL", "UOG_SSO_LOGIN_URL"]
