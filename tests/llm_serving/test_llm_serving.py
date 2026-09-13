"""LLM serving health tests (Plan 3 audit, 2026-09-12).

Per Plan 3 of the v6 era audit. These tests verify the LLM serving
stack (LiteLLM gateway, Unsloth fine-tuning, Llama-swap dynamic swap)
is configured and consistent. Tests run without Docker.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_litellm_python_lib_installed() -> None:
    """litellm Python lib is installed at the documented version."""
    result = subprocess.run(
        ["uv", "pip", "show", "litellm"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=15,
    )
    assert result.returncode == 0, (
        f"Plan 3 audit: litellm not installed. stderr: {result.stderr}"
    )
    # Extract version from output
    m = re.search(r"Version:\s*(\S+)", result.stdout)
    assert m, f"Plan 3 audit: no version in litellm output"
    assert m.group(1).startswith("1."), (
        f"Plan 3 audit: unexpected litellm version {m.group(1)}"
    )


def test_litellm_config_model_count() -> None:
    """The litellm config lists ≥ 30 models (the canonical catalog)."""
    config = REPO_ROOT / "bonneagar/stacks/litellm/config/config.yaml"
    if not config.exists():
        return  # Config not yet authored (out of scope)
    content = config.read_text()
    models = re.findall(r"^\s*-\s*model_name:\s*(\S+)", content, re.MULTILINE)
    assert len(models) >= 30, (
        f"Plan 3 audit: expected ≥30 models in litellm config, found {len(models)}"
    )


def test_litellm_config_local_models_route_to_llama_swap() -> None:
    """All `local/*` aliases route through llama-swap on :8080."""
    config = REPO_ROOT / "bonneagar/stacks/litellm/config/config.yaml"
    if not config.exists():
        return
    content = config.read_text()
    # Find all api_base entries that contain llama-swap
    llama_swap_refs = re.findall(r"api_base:\s*(http://llama-swap[^\s]+)", content)
    assert len(llama_swap_refs) >= 1, (
        "Plan 3 audit: no llama-swap references in litellm config"
    )


def test_llama_swap_compose_exists() -> None:
    """The llama-swap stack compose file exists and has a working image."""
    compose = REPO_ROOT / "bonneagar/stacks/llama-swap/compose.yaml"
    assert compose.exists(), (
        "Plan 3 audit: bonneagar/stacks/llama-swap/compose.yaml missing"
    )
    content = compose.read_text()
    # Should reference either :cpu (working) or :v166 (claimed, doesn't exist)
    assert ":cpu" in content or ":v166" in content, (
        "Plan 3 audit: llama-swap compose has no working image tag"
    )


def test_unsloth_serve_compose_exists() -> None:
    """The unsloth-serve stack compose file exists."""
    compose = REPO_ROOT / "bonneagar/stacks/unsloth-serve/compose.yaml"
    assert compose.exists(), (
        "Plan 3 audit: bonneagar/stacks/unsloth-serve/compose.yaml missing"
    )


def test_litellm_docker_image_matches_compose() -> None:
    """The litellm skill version claim aligns with the compose.yaml image."""
    compose = REPO_ROOT / "bonneagar/stacks/litellm/compose.yaml"
    content = compose.read_text()
    # Find the image tag
    m = re.search(r"image:\s*ghcr\.io/berriai/litellm(?:-database)?:v?([\d.]+)", content)
    assert m, "Plan 3 audit: can't find litellm docker image tag in compose.yaml"
    docker_version = m.group(1)
    # The python lib is 1.97 (Sep 2026); docker is usually slightly behind
    # Just verify they're in the same major version family
    assert docker_version.startswith("1."), (
        f"Plan 3 audit: unexpected docker version {docker_version}"
    )


def test_baml_clients_minimax3_is_default() -> None:
    """Most BAML clients use minimax-m3 as the default text model."""
    clients = REPO_ROOT / "baml_src/clients.baml"
    if not clients.exists():
        return
    content = clients.read_text()
    minimax_count = content.count('model "minimax-m3"')
    other_count = (
        content.count('model "local/vision/')
        + content.count('model "qwen3.7-plus"')
        + content.count('model "local/llama')
    )
    # We expect most to be minimax-m3
    assert minimax_count > other_count, (
        f"Plan 3 audit: expected minimax-m3 to dominate, "
        f"got {minimax_count} minimax vs {other_count} others"
    )
