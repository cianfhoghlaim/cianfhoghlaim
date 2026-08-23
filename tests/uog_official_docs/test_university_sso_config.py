"""Tests for the UoGSsoConfig + UniversitySsoConfig surface
(the WS4 lift of the 2026-08-23-uog-official-docs-and-nui-superset-v1
change)."""

from __future__ import annotations


def test_university_sso_config_reads_university_keys(monkeypatch):
    """GIVEN the new `UNIVERSITY_SSO_*` keys
    WHEN UniversitySsoConfig.from_resolver() is called
    THEN the resolved credentials are populated."""
    from sruth_browser.core.secrets import UniversitySsoConfig

    monkeypatch.setenv("UNIVERSITY_SSO_STUDENT_ID", "12345678")
    monkeypatch.setenv("UNIVERSITY_SSO_PASSWORD", "real-password")
    cfg = UniversitySsoConfig.from_resolver()
    assert cfg.student_id == "12345678"
    assert cfg.student_password == "real-password"
    assert cfg.has_real_credentials() is True


def test_university_sso_config_falls_back_to_per_institution(monkeypatch):
    """GIVEN per-institution `QUB_SSO_*` keys (but no generic
    UNIVERSITY_SSO_* keys)
    WHEN UniversitySsoConfig.from_resolver() is called
    THEN the QUB keys are picked up."""
    from sruth_browser.core.secrets import UniversitySsoConfig

    monkeypatch.setenv("QUB_SSO_STUDENT_ID", "qub99999")
    monkeypatch.setenv("QUB_SSO_PASSWORD", "qub-real-password")
    cfg = UniversitySsoConfig.from_resolver()
    assert cfg.student_id == "qub99999"
    assert cfg.student_password == "qub-real-password"


def test_university_sso_config_placeholder_is_rejected(monkeypatch):
    from sruth_browser.core.secrets import UniversitySsoConfig

    monkeypatch.setenv("UNIVERSITY_SSO_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("UNIVERSITY_SSO_PASSWORD", "fixture-only")
    cfg = UniversitySsoConfig.from_resolver()
    assert cfg.has_real_credentials() is False


def test_university_sso_config_motherduck_check(monkeypatch):
    """GIVEN a real `MOTHERDUCK_TOKEN`
    WHEN has_motherduck() is called
    THEN the result is True."""
    from sruth_browser.core.secrets import UniversitySsoConfig

    monkeypatch.setenv("MOTHERDUCK_TOKEN", "real-motherduck-token")
    cfg = UniversitySsoConfig.from_resolver()
    assert cfg.has_motherduck() is True


def test_university_sso_config_bonneagar_check(monkeypatch):
    """GIVEN a real `DUCKLAKE_POSTGRES_PASSWORD`
    WHEN has_bonneagar_lakehouse() is called
    THEN the result is True."""
    from sruth_browser.core.secrets import UniversitySsoConfig

    monkeypatch.setenv("DUCKLAKE_POSTGRES_PASSWORD", "real-postgres-password")
    cfg = UniversitySsoConfig.from_resolver()
    assert cfg.has_bonneagar_lakehouse() is True
