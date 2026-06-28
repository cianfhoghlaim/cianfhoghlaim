"""Tests for `spaces._common.hf_hub_push.push_model_to_hub`.

The 2 `gradio-ensemble-pattern` HF Hub scenarios from
`openspec/changes/celtic-data-engineering-patterns/specs/gradio-ensemble-pattern/spec.md`
are validated here. We mock the `huggingface_hub.HfApi` so the tests do not
require a real HF token or network access.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from spaces._common.hf_hub_push import push_model_to_hub


def test_push_model_to_hub_resolves_token_from_env(tmp_path: Path) -> None:
    """`HF_TOKEN` from env is used when no kwarg is passed."""
    (tmp_path / "weights.bin").write_bytes(b"\x00\x01\x02")
    fake_sha = "deadbeef" * 5
    mock_api = MagicMock()
    mock_api.upload_folder.return_value.oid = fake_sha
    with patch.dict(os.environ, {"HF_TOKEN": "hf_test_xxx"}):
        with patch("spaces._common.hf_hub_push.HfApi", return_value=mock_api) as api_cls:
            sha = push_model_to_hub(
                local_dir=tmp_path,
                repo_id="cianfhoghlaim/test",
                commit_message="Initial upload",
            )
    assert sha == fake_sha
    api_cls.assert_called_once_with(token="hf_test_xxx")
    mock_api.upload_folder.assert_called_once()
    call_kwargs = mock_api.upload_folder.call_args.kwargs
    assert call_kwargs["repo_id"] == "cianfhoghlaim/test"
    assert call_kwargs["repo_type"] == "model"
    assert call_kwargs["commit_message"] == "Initial upload"


def test_push_model_to_hub_explicit_token_overrides_env(tmp_path: Path) -> None:
    """`token=` kwarg overrides the `HF_TOKEN` env var."""
    (tmp_path / "weights.bin").write_bytes(b"\x00\x01\x02")
    mock_api = MagicMock()
    mock_api.upload_folder.return_value.oid = "cafebabe" * 5
    with patch.dict(os.environ, {"HF_TOKEN": "hf_env_token"}):
        with patch("spaces._common.hf_hub_push.HfApi", return_value=mock_api) as api_cls:
            push_model_to_hub(
                local_dir=tmp_path,
                repo_id="cianfhoghlaim/test",
                commit_message="Initial",
                token="hf_explicit_token",
            )
    api_cls.assert_called_once_with(token="hf_explicit_token")


def test_push_model_to_hub_missing_token_raises(tmp_path: Path) -> None:
    """No token (env or kwarg) raises ValueError."""
    (tmp_path / "weights.bin").write_bytes(b"\x00\x01\x02")
    env_without_token = {k: v for k, v in os.environ.items() if k != "HF_TOKEN"}
    with patch.dict(os.environ, env_without_token, clear=True):
        with pytest.raises(ValueError, match="HF_TOKEN is required"):
            push_model_to_hub(
                local_dir=tmp_path,
                repo_id="cianfhoghlaim/test",
                commit_message="Initial",
            )


def test_push_model_to_hub_missing_dir_raises(tmp_path: Path) -> None:
    """Non-existent local_dir raises FileNotFoundError."""
    bogus = tmp_path / "does-not-exist"
    with pytest.raises(FileNotFoundError, match="local_dir does not exist"):
        push_model_to_hub(
            local_dir=bogus,
            repo_id="cianfhoghlaim/test",
            commit_message="Initial",
            token="hf_xxx",
        )


def test_push_model_to_hub_supports_dataset_and_space_repos(tmp_path: Path) -> None:
    """`repo_type` accepts `dataset` and `space` in addition to `model`."""
    (tmp_path / "data.csv").write_text("a,b\n1,2\n")
    mock_api = MagicMock()
    mock_api.upload_folder.return_value.oid = "abc" * 14
    for repo_type in ("dataset", "space"):
        mock_api.reset_mock()
        with patch("spaces._common.hf_hub_push.HfApi", return_value=mock_api):
            push_model_to_hub(
                local_dir=tmp_path,
                repo_id=f"cianfhoghlaim/test-{repo_type}",
                commit_message=f"Upload as {repo_type}",
                token="hf_xxx",
                repo_type=repo_type,
            )
        assert mock_api.upload_folder.call_args.kwargs["repo_type"] == repo_type
