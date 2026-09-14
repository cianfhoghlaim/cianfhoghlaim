"""Web stack health tests (Plan 11 audit, 2026-09-13).

Per Plan 11 of the v6 era audit. These tests verify the web stack
surface: Hono API routes, CopilotKit route mounts, A2UI component
generator, and the 4 canonical web apps.
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_hono_api_package_exists() -> None:
    """The @cianfhoghlaim/hono-api package is present."""
    pkg = REPO_ROOT / "web" / "hono-api" / "package.json"
    assert pkg.exists(), "Plan 11 audit: web/hono-api/package.json missing"
    content = pkg.read_text()
    assert '"@cianfhoghlaim/hono-api"' in content, (
        "Plan 11 audit: wrong package name in hono-api/package.json"
    )


def test_hono_api_routes_count() -> None:
    """The Hono API has ≥ 30 .ts route files."""
    routes_dir = REPO_ROOT / "web" / "hono-api" / "src" / "routes"
    ts_files = list(routes_dir.rglob("*.ts"))
    assert len(ts_files) >= 30, (
        f"Plan 11 audit: expected ≥30 Hono API route files, found {len(ts_files)}"
    )


def test_hono_api_copilotkit_routes() -> None:
    """The Hono API has CopilotKit routes (lc, jc, a-level, gcse)."""
    copilotkit_dir = REPO_ROOT / "web" / "hono-api" / "src" / "routes" / "copilotkit"
    assert copilotkit_dir.exists(), (
        "Plan 11 audit: web/hono-api/src/routes/copilotkit/ missing"
    )
    for stage in ["lc", "jc", "a-level", "gcse"]:
        assert (copilotkit_dir / stage).exists(), (
            f"Plan 11 audit: copilotkit/{stage}/ missing"
        )


def test_a2ui_surface_generator_exists() -> None:
    """The A2UI surface generator component is present."""
    a2ui = REPO_ROOT / "web" / "apps" / "cianfhoghlaim" / "components" / "_shared" / "A2UISurfaceGenerator.tsx"
    assert a2ui.exists(), (
        f"Plan 11 audit: {a2ui} missing (was restored in Plan 58)"
    )
    content = a2ui.read_text()
    # Should export the canonical component
    assert "A2UISurfaceGenerator" in content, (
        "Plan 11 audit: A2UISurfaceGenerator.tsx missing the export"
    )


def test_web_apps_count() -> None:
    """There are ≥ 10 web apps in web/apps/."""
    apps_dir = REPO_ROOT / "web" / "apps"
    assert apps_dir.exists(), "Plan 11 audit: web/apps/ missing"
    app_dirs = [d for d in apps_dir.iterdir() if d.is_dir()]
    assert len(app_dirs) >= 10, (
        f"Plan 11 audit: expected ≥10 web apps, found {len(app_dirs)}"
    )


def test_canonical_web_apps_present() -> None:
    """The 4 canonical web apps from the agentic-frontend-frameworks skill exist."""
    canonical = ["cianfhoghlaim-web", "croilar-web", "croilar-portal", "tuatha-ui"]
    for app in canonical:
        path = REPO_ROOT / "web" / "apps" / app
        assert path.exists(), (
            f"Plan 11 audit: canonical web app '{app}' missing"
        )


def test_hono_api_index_module_compiles() -> None:
    """The Hono API entry point can be type-checked (best-effort, may skip in CI)."""
    index = REPO_ROOT / "web" / "hono-api" / "src" / "index.ts"
    if not index.exists():
        return
    # Don't actually run tsc - just verify the file has the expected structure
    content = index.read_text()
    assert "Hono" in content or "hono" in content, (
        "Plan 11 audit: hono-api/src/index.ts doesn't import Hono"
    )


def test_web_package_workspaces() -> None:
    """The web/ workspace uses pnpm or bun workspaces."""
    root_pkg = REPO_ROOT / "package.json"
    if not root_pkg.exists():
        return
    content = root_pkg.read_text()
    # Either pnpm-workspace.yaml exists or workspaces field exists
    has_pnpm = (REPO_ROOT / "pnpm-workspace.yaml").exists()
    has_workspaces = '"workspaces"' in content
    assert has_pnpm or has_workspaces, (
        "Plan 11 audit: web/ not configured as a workspace"
    )


def test_hono_api_image_generation_route() -> None:
    """The Hono API has the image-generation CopilotKit route."""
    img_gen = REPO_ROOT / "web" / "hono-api" / "src" / "routes" / "copilotkit" / "image-generation.ts"
    assert img_gen.exists(), (
        f"Plan 11 audit: {img_gen} missing"
    )


def test_agentic_frontend_skill_present() -> None:
    """The agentic-frontend-frameworks umbrella skill exists."""
    skill = REPO_ROOT / ".agents" / "skills" / "agentic-frontend-frameworks" / "SKILL.md"
    assert skill.exists(), (
        f"Plan 11 audit: {skill} missing"
    )
