"""Tests for the multi-target deployment factory (Stage 4).

Covers:

- The 3 canonical targets (DEV, STAGING, PROD) have the expected shape
- `get_target(name)` honours the OIDEACHAIS_TARGET env var
- `validate_target_secrets(target)` raises for missing env vars
- `create_dev_pipeline()` / `create_staging_pipeline()` /
  `create_prod_pipeline()` work
- The make_target.sh script is syntactically valid and respects
  `OIDEACHAIS_TARGET`
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


class TestCanonicalTargets:
    """The 3 canonical targets must have the expected shape."""

    def test_dev_target(self) -> None:
        from oideachais.dlt_utils.target_factory import DEV

        assert DEV.name == "dev"
        assert DEV.destination == "duckdb"
        assert DEV.dataset_name_prefix == "author_archive_dev"
        assert DEV.requires_secrets == ()
        assert DEV.is_production is False

    def test_staging_target(self) -> None:
        from oideachais.dlt_utils.target_factory import STAGING

        assert STAGING.name == "staging"
        assert STAGING.destination == "motherduck"
        assert STAGING.dataset_name_prefix == "author_archive_staging"
        assert "MOTHERDUCK_TOKEN" in STAGING.requires_secrets
        assert STAGING.is_production is False

    def test_prod_target(self) -> None:
        from oideachais.dlt_utils.target_factory import PROD

        assert PROD.name == "prod"
        assert PROD.destination == "ducklake"
        assert PROD.dataset_name_prefix == "author_archive"
        assert PROD.is_production is True
        # 6 required secrets
        assert len(PROD.requires_secrets) == 6
        assert "DUCKLAKE_POSTGRES_HOST" in PROD.requires_secrets
        assert "DUCKLAKE_POSTGRES_PASSWORD" in PROD.requires_secrets
        assert "BUCKET" in PROD.requires_secrets

    def test_all_targets_dict(self) -> None:
        from oideachais.dlt_utils.target_factory import ALL_TARGETS, DEV, STAGING, PROD

        assert set(ALL_TARGETS) == {"dev", "staging", "prod"}
        assert ALL_TARGETS["dev"] is DEV
        assert ALL_TARGETS["staging"] is STAGING
        assert ALL_TARGETS["prod"] is PROD


class TestGetTarget:
    """The `get_target` function must select the right Target."""

    def test_default_is_dev(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OIDEACHAIS_TARGET", raising=False)
        from oideachais.dlt_utils.target_factory import get_target, DEV

        assert get_target() is DEV
        assert get_target("dev") is DEV

    def test_explicit_staging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OIDEACHAIS_TARGET", raising=False)
        from oideachais.dlt_utils.target_factory import get_target, STAGING

        assert get_target("staging") is STAGING

    def test_explicit_prod(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OIDEACHAIS_TARGET", raising=False)
        from oideachais.dlt_utils.target_factory import get_target, PROD

        assert get_target("prod") is PROD

    def test_env_var_overrides_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OIDEACHAIS_TARGET", "prod")
        from oideachais.dlt_utils.target_factory import get_target, PROD

        assert get_target() is PROD

    def test_unknown_target_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OIDEACHAIS_TARGET", raising=False)
        from oideachais.dlt_utils.target_factory import get_target

        with pytest.raises(ValueError, match="Unknown target"):
            get_target("unknown")


class TestValidateTargetSecrets:
    """The `validate_target_secrets` function must raise for missing vars."""

    def test_dev_target_no_secrets_needed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MOTHERDUCK_TOKEN", raising=False)
        monkeypatch.delenv("DUCKLAKE_POSTGRES_HOST", raising=False)
        from oideachais.dlt_utils.target_factory import DEV, validate_target_secrets

        # Should not raise
        validate_target_secrets(DEV)

    def test_staging_missing_motherduck_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MOTHERDUCK_TOKEN", raising=False)
        from oideachais.dlt_utils.target_factory import STAGING, validate_target_secrets

        with pytest.raises(EnvironmentError, match="MOTHERDUCK_TOKEN"):
            validate_target_secrets(STAGING)

    def test_staging_with_motherduck_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MOTHERDUCK_TOKEN", "test-token")
        from oideachais.dlt_utils.target_factory import STAGING, validate_target_secrets

        # Should not raise
        validate_target_secrets(STAGING)

    def test_prod_missing_all_secrets(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for var in (
            "DUCKLAKE_POSTGRES_HOST",
            "DUCKLAKE_POSTGRES_PORT",
            "DUCKLAKE_POSTGRES_DB",
            "DUCKLAKE_POSTGRES_USER",
            "DUCKLAKE_POSTGRES_PASSWORD",
            "BUCKET",
        ):
            monkeypatch.delenv(var, raising=False)
        from oideachais.dlt_utils.target_factory import PROD, validate_target_secrets

        with pytest.raises(EnvironmentError) as exc_info:
            validate_target_secrets(PROD)
        # Error message should mention at least one of the missing vars
        assert "DUCKLAKE" in str(exc_info.value) or "BUCKET" in str(exc_info.value)

    def test_prod_with_all_secrets(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for var in (
            "DUCKLAKE_POSTGRES_HOST",
            "DUCKLAKE_POSTGRES_PORT",
            "DUCKLAKE_POSTGRES_DB",
            "DUCKLAKE_POSTGRES_USER",
            "DUCKLAKE_POSTGRES_PASSWORD",
            "BUCKET",
        ):
            monkeypatch.setenv(var, f"test-{var}")
        from oideachais.dlt_utils.target_factory import PROD, validate_target_secrets

        # Should not raise
        validate_target_secrets(PROD)


class TestCreatePipelines:
    """The shortcut pipeline functions must work end-to-end."""

    def test_create_dev_pipeline(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OIDEACHAIS_DEV_DB", raising=False)
        from oideachais.dlt_utils.target_factory import create_dev_pipeline

        pipeline = create_dev_pipeline(
            pipeline_name="test_dev", dataset_name="my_data"
        )
        # Pipeline name should be preserved
        assert pipeline.pipeline_name == "test_dev"
        # Dataset name should be prefixed
        assert "author_archive_dev" in pipeline.dataset_name

    def test_create_staging_pipeline_missing_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MOTHERDUCK_TOKEN", raising=False)
        from oideachais.dlt_utils.target_factory import create_staging_pipeline

        with pytest.raises(EnvironmentError, match="MOTHERDUCK_TOKEN"):
            create_staging_pipeline(
                pipeline_name="test_staging", dataset_name="my_data"
            )

    def test_create_staging_pipeline_with_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MOTHERDUCK_TOKEN", "test-token")
        from oideachais.dlt_utils.target_factory import create_staging_pipeline

        pipeline = create_staging_pipeline(
            pipeline_name="test_staging", dataset_name="my_data"
        )
        assert pipeline.pipeline_name == "test_staging"
        assert "author_archive_staging" in pipeline.dataset_name

    def test_create_prod_pipeline_missing_secrets(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for var in (
            "DUCKLAKE_POSTGRES_HOST",
            "DUCKLAKE_POSTGRES_PORT",
            "DUCKLAKE_POSTGRES_DB",
            "DUCKLAKE_POSTGRES_USER",
            "DUCKLAKE_POSTGRES_PASSWORD",
            "BUCKET",
        ):
            monkeypatch.delenv(var, raising=False)
        from oideachais.dlt_utils.target_factory import create_prod_pipeline

        with pytest.raises(EnvironmentError):
            create_prod_pipeline(
                pipeline_name="test_prod", dataset_name="my_data"
            )


class TestMakeTargetScript:
    """The make_target.sh CLI helper must respect OIDEACHAIS_TARGET."""

    def test_script_exists_and_is_executable(self) -> None:
        script = Path("oideachais/scripts/make_target.sh")
        assert script.exists()
        assert os.access(script, os.X_OK)

    def test_default_target_is_dev(self) -> None:
        result = subprocess.run(
            ["bash", "oideachais/scripts/make_target.sh"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OIDEACHAIS_TARGET=dev" in result.stdout

    def test_explicit_target(self) -> None:
        result = subprocess.run(
            ["bash", "oideachais/scripts/make_target.sh", "dev"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OIDEACHAIS_TARGET=dev" in result.stdout

    def test_explicit_target_with_command(self) -> None:
        result = subprocess.run(
            [
                "bash",
                "oideachais/scripts/make_target.sh",
                "dev",
                "echo",
                "OIDEACHAIS_TARGET=$OIDEACHAIS_TARGET",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OIDEACHAIS_TARGET=dev" in result.stdout

    def test_unknown_target_rejected(self) -> None:
        result = subprocess.run(
            ["bash", "oideachais/scripts/make_target.sh", "production"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 2
        assert "unknown target" in result.stderr

    def test_help_flag(self) -> None:
        result = subprocess.run(
            ["bash", "oideachais/scripts/make_target.sh", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "staging" in result.stdout
        assert "prod" in result.stdout
