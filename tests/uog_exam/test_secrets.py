"""Tests for the SecretsResolver priority chain.

Spec: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/specs/
      cianfhoghlaim-uog-exam-papers/design/auth-credential-priority-chain.md

Priority chain:
  1. Self-hosted Infisical (env-driven; never raises on a 4xx).
  2. Local `.env` (Pydantic `BaseSettings`).
  3. OnePassword CLI is NOT invoked by the runner.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from sruth_browser.core import secrets as secrets_module
from sruth_browser.core.secrets import (
    FIXTURE_ONLY_VALUES,
    SecretsResolver,
    UoGSsoConfig,
    reset_default_secrets_resolver,
)


@pytest.fixture(autouse=True)
def _clean_secrets_state(monkeypatch):
    """Ensure each test starts with a clean resolver cache + no env leaks."""
    for var in (
        "INFISICAL_TOKEN",
        "INFISICAL_URL",
        "INFISICAL_PROJECT",
        "INFISICAL_ENV",
        "OP_SERVICE_ACCOUNT_TOKEN",
        "OOG_STUDENT_ID",
        "OOG_STUDENT_PASSWORD",
    ):
        monkeypatch.delenv(var, raising=False)
    reset_default_secrets_resolver()
    yield
    reset_default_secrets_resolver()


def test_env_backend_wins_when_nothing_else_configured(monkeypatch):
    """GIVEN a fresh process with no Infisical configured
    AND a value in `os.environ`
    WHEN SecretsResolver().get("OOG_STUDENT_PASSWORD") is called
    THEN env returns the value (and Infisical is not contacted)."""
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "real-password")
    r = SecretsResolver()
    sentinel = patch.object(r, "_try_infisical", return_value=(None, "infisical"))

    with sentinel as spy:
        value = r.get("OOG_STUDENT_PASSWORD")

    assert value == "real-password"
    spy.assert_not_called()


def test_infisical_wins_when_configured(monkeypatch):
    """GIVEN a configured Infisical backend (mocked HTTP)
    AND a different value in `os.environ`
    WHEN SecretsResolver().get("OOG_STUDENT_PASSWORD") is called
    THEN Infisical's value is returned."""
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "old-env-password")
    monkeypatch.setenv("INFISICAL_TOKEN", "t")
    monkeypatch.setenv("INFISICAL_URL", "https://infisical.local")
    monkeypatch.setenv("INFISICAL_PROJECT", "uog-exam-pipeline")
    monkeypatch.setenv("INFISICAL_ENV", "dev")

    fake_payload = "real-infisical-password".encode()
    with patch("urllib.request.urlopen") as fake_urlopen:
        fake_response = fake_urlopen.return_value.__enter__.return_value
        fake_response.status = 200
        fake_response.read.return_value = fake_payload

        r = SecretsResolver.from_env()
        value = r.get("OOG_STUDENT_PASSWORD")

    assert value == "real-infisical-password"
    fake_urlopen.assert_called_once()


def test_infisical_404_falls_through_to_env(monkeypatch):
    """GIVEN Infisical returns a 4xx (secret missing from this project)
    AND a value in `os.environ`
    WHEN get() is called
    THEN env wins."""
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "env-password")
    monkeypatch.setenv("INFISICAL_TOKEN", "t")
    monkeypatch.setenv("INFISICAL_URL", "https://infisical.local")
    monkeypatch.setenv("INFISICAL_PROJECT", "uog")
    monkeypatch.setenv("INFISICAL_ENV", "dev")

    with patch("urllib.request.urlopen") as fake_urlopen:
        fake_response = fake_urlopen.return_value.__enter__.return_value
        fake_response.status = 404
        r = SecretsResolver.from_env()
        value = r.get("OOG_STUDENT_PASSWORD")
    assert value == "env-password"


def test_onepassword_cli_is_not_invoked(monkeypatch):
    """GIVEN OP_SERVICE_ACCOUNT_TOKEN is set (cloner scenario)
    AND no Infisical configured
    WHEN get() is called
    THEN `op` is NOT invoked (no subprocess)."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "fake-token")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "real-password")

    import subprocess

    with patch.object(subprocess, "check_output") as spy:
        r = SecretsResolver()
        value = r.get("OOG_STUDENT_PASSWORD")

    assert value == "real-password"
    spy.assert_not_called()


def test_onepassword_does_not_call_subprocess_check_output(monkeypatch):
    """Same as above but more explicit — `op` is doc-only."""
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "fake")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "real-password")

    import subprocess

    with patch.object(subprocess, "check_output") as spy:
        SecretsResolver().get("OOG_STUDENT_PASSWORD")
    spy.assert_not_called()


def test_fixture_only_password_treated_as_placeholder(monkeypatch):
    """GIVEN OOG_STUDENT_PASSWORD is a known fixture-only string
    WHEN UoGSsoConfig.has_real_credentials() is called
    THEN it returns False (the SSO round-trip is skipped)."""
    for placeholder in FIXTURE_ONLY_VALUES:
        monkeypatch.setenv("OOG_STUDENT_ID", "12345678")
        monkeypatch.setenv("OOG_STUDENT_PASSWORD", placeholder)
        cfg = UoGSsoConfig.from_resolver()
        assert cfg.has_real_credentials() is False, (
            f"placeholder={placeholder!r} should not count as real credentials"
        )


def test_real_password_marks_config_as_having_real_credentials(monkeypatch):
    """GIVEN a non-placeholder password
    WHEN UoGSsoConfig.has_real_credentials() is called
    THEN it returns True."""
    monkeypatch.setenv("OOG_STUDENT_ID", "12345678")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "this-is-real-do-not-leak")
    cfg = UoGSsoConfig.from_resolver()
    assert cfg.has_real_credentials() is True


def test_resolver_caches_across_calls_within_ttl(monkeypatch):
    """GIVEN a configured Infisical backend
    WHEN get() is called twice in quick succession
    THEN the second call does NOT re-hit the network."""
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "real")
    monkeypatch.setenv("INFISICAL_TOKEN", "t")
    monkeypatch.setenv("INFISICAL_URL", "https://infisical.local")
    monkeypatch.setenv("INFISICAL_PROJECT", "uog")
    monkeypatch.setenv("INFISICAL_ENV", "dev")

    with patch("urllib.request.urlopen") as fake_urlopen:
        # First call hits Infisical
        fake_response = fake_urlopen.return_value.__enter__.return_value
        fake_response.status = 200
        fake_response.read.return_value = b"real"
        r = SecretsResolver.from_env()
        assert r.get("OOG_STUDENT_PASSWORD") == "real"
        # Subsequent call should be cached (no fresh urlopen call).
        assert r.get("OOG_STUDENT_PASSWORD") == "real"

    assert fake_urlopen.call_count == 1
