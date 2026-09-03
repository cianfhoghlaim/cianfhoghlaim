"""Tests for ``scripts/registry_audit.py`` — the drift detector.

Verifies the 5 canonical scenarios for the
``centralized-model-registry`` capability's lint gate:

1. ``test_audit_exits_zero_when_clean``: Run on the current repo,
   expect exit 0 + a "0 hardcoded" message in stdout.
2. ``test_audit_json_output_format``: Run with ``--json``, expect
   JSON output with a ``"findings"`` key.
3. ``test_audit_detects_hardcoded_string``: Create a temp
   ``agents/`` tree with a hardcoded model string, run audit
   pointing at that tree, expect drift count > 0.
4. ``test_audit_strict_mode_fails_on_drift``: Run with ``--strict``
   on the same temp tree, expect exit 1.
5. ``test_audit_filters_by_path``: Run with a temp ``--repo-root``
   that only contains a ``tests/`` subdir (not in ``_AUDIT_DIRS``),
   expect 0 drift — the audit skips ``tests/`` by design.

All tests are deterministic — no network, no live DB, no
subprocess calls to ``lint_drift_docs.py`` (the audit script
subprocess-times-out in 60 s but we patch that out via ``timeout``).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Path to the audit script under test.
_AUDIT_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "registry_audit.py"


# ─── 1 — clean repo exits 0 with "0 hardcoded" message ──────────


def test_audit_exits_zero_when_clean() -> None:
    """Run on the current repo, expect exit 0 + "0 hardcoded"
    message in stdout.

    We use ``timeout=120`` because the audit script also
    subprocess-runs ``lint_drift_docs.py`` (60 s timeout) — we
    bound the whole invocation to 120 s to avoid CI hangs.
    """
    result = subprocess.run(
        [sys.executable, str(_AUDIT_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(_AUDIT_SCRIPT.parent.parent),
    )
    assert result.returncode == 0, (
        f"audit should exit 0 on clean repo, got {result.returncode}\n"
        f"stderr={result.stderr}\nstdout={result.stdout}"
    )
    assert "0 hardcoded" in result.stdout, (
        f"Expected '0 hardcoded' in stdout, got:\n{result.stdout}"
    )


# ─── 2 — --json flag produces JSON output with "findings" key ────


def test_audit_json_output_format() -> None:
    """Run with ``--json``, expect JSON output with a
    ``"findings"`` key.
    """
    result = subprocess.run(
        [sys.executable, str(_AUDIT_SCRIPT), "--json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(_AUDIT_SCRIPT.parent.parent),
    )
    assert result.returncode == 0, (
        f"audit --json should exit 0, got {result.returncode}\n"
        f"stderr={result.stderr}"
    )
    payload = json.loads(result.stdout)
    assert "findings" in payload, (
        f"Expected 'findings' key in JSON output, got keys: "
        f"{list(payload.keys())}"
    )
    assert isinstance(payload["findings"], list)


# ─── 3 — audit detects a hardcoded model string ────────────────


def test_audit_detects_hardcoded_string(tmp_path: Path) -> None:
    """Create a temp ``agents/`` tree with a hardcoded model string,
    run audit pointing at that tree (via ``--repo-root``), expect
    drift count > 0.

    We use a string that matches a known family prefix but is NOT
    in the canonical ``_KNOWN_MODEL_KEYS`` whitelist (so the audit
    flags it as drift). ``"google/gemma-7b-it"`` is canonical HF
    org/model format that matches the ``google/`` prefix but is
    not in the registry's known keys.
    """
    # Build a minimal temp repo that mirrors the audited dirs.
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    drift_file = agents_dir / "drift_agent.py"
    drift_file.write_text(
        '"""A drift agent that hardcodes a model string."""\n'
        '\n'
        'HARDCODED_MODEL = "google/gemma-7b-it"\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_AUDIT_SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Audit should detect drift (exit 0 in non-strict mode,
    # but the JSON payload should have count > 0).
    payload = json.loads(result.stdout)
    assert payload["count"] > 0, (
        f"Expected audit to detect drift, got count=0\n"
        f"findings={payload['findings']}"
    )
    # At least one finding should be in our temp file.
    matching = [f for f in payload["findings"] if str(drift_file) in str(f.get("file", ""))]
    assert matching, (
        f"Expected at least one finding in {drift_file}, got: "
        f"{payload['findings']}"
    )


# ─── 4 — --strict mode exits 1 on drift ─────────────────────────


def test_audit_strict_mode_fails_on_drift(tmp_path: Path) -> None:
    """Run with ``--strict`` on the same temp tree, expect exit 1.

    This is the CI gate behaviour: drift = non-zero exit under
    ``--strict``.
    """
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    drift_file = agents_dir / "another_drift.py"
    drift_file.write_text(
        '"""Another hardcoded model string."""\n'
        '\n'
        'DRIFT_MODEL = "anthropic/claude-7-ultra-fake"\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_AUDIT_SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--strict",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 1, (
        f"Expected audit --strict to exit 1 on drift, got {result.returncode}\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )


# ─── 5 — tests/ is excluded from audit scope ────────────────────


def test_audit_filters_by_path(tmp_path: Path) -> None:
    """Run with a temp ``--repo-root`` that only contains a
    ``tests/`` subdir (not in the audit's ``_AUDIT_DIRS`` list),
    expect 0 drift — the audit skips ``tests/`` by design.

    Even if ``tests/`` contains a hardcoded model string, the
    audit's fixed list of audited directories
    (``agents/``, ``baml_src/``, ``notebooks/``, ``web/``,
    ``orchestration/``, ``spaces/``, ``meaisinfhoghlaim/``)
    excludes ``tests/``, so findings == 0.
    """
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    drift_in_tests = tests_dir / "test_drift_in_tests_dir.py"
    drift_in_tests.write_text(
        '"""A drift file inside tests/ (should be ignored)."""\n'
        '\n'
        'IGNORED_DRIFT = "google/gemma-7b-it"\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(_AUDIT_SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Expected clean audit on tests-only repo, got {result.returncode}\n"
        f"stderr={result.stderr}"
    )
    payload = json.loads(result.stdout)
    assert payload["count"] == 0, (
        f"Expected 0 findings for tests/-only repo, got "
        f"{payload['count']}: {payload['findings']}"
    )


# ─── 6 — _KNOWN_MODEL_KEYS stays in sync with MODEL_REGISTRY ────


def test_known_model_keys_covers_registry() -> None:
    """Every ``MODEL_REGISTRY`` key must appear in the audit's
    ``_KNOWN_MODEL_KEYS`` whitelist.

    ``_KNOWN_MODEL_KEYS`` is a hand-maintained set (kept
    import-free so the pre-commit hook stays fast — it does not
    import ``MODEL_REGISTRY``), which means "add a model to the
    registry" and "add it to this set" are two separate manual
    edits that can silently drift apart: a new registry key whose
    string form isn't whitelisted here would fail
    ``mise run lint:registry --strict`` the first time anyone's
    code legitimately references it. This test makes that drift a
    loud, immediate CI failure instead of a confusing lint error
    discovered later, without changing the audit script's speed or
    import profile.

    Only checks ``key`` (the canonical registry identifier) — not
    every ``unsloth_id``/``mlx_id``/``upstream_id``/``litellm_alias``
    variant also present in ``_KNOWN_MODEL_KEYS``, since those are
    denser and independently curated for prefix-matching reasons
    (see ``_PREFIXES`` in the audit script).
    """
    import importlib.util

    audit_spec = importlib.util.spec_from_file_location(
        "registry_audit", _AUDIT_SCRIPT
    )
    assert audit_spec is not None and audit_spec.loader is not None
    audit_module = importlib.util.module_from_spec(audit_spec)
    audit_spec.loader.exec_module(audit_module)

    from meaisinfhoghlaim.models.model_registry import MODEL_REGISTRY

    registry_keys = {entry.key for entry in MODEL_REGISTRY.filter()}
    missing = sorted(registry_keys - audit_module._KNOWN_MODEL_KEYS)
    assert not missing, (
        "MODEL_REGISTRY has keys not in scripts/registry_audit.py's "
        f"_KNOWN_MODEL_KEYS whitelist: {missing}. Add them to "
        "_KNOWN_MODEL_KEYS or mise run lint:registry --strict will "
        "fail the first time this key string is used in audited code."
    )
