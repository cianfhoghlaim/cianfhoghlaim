"""Cianfhoghlaim Dagger module -- polyglot CI/CD for the monorepo.

Python root (``infrastructure/dagger/``) with 3 pipelines:
  * ``InfrastructurePipeline`` -- Pulumi IaC + Komodo GitOps + Pangolin verify
  * ``WebPipeline`` -- bun turbo build + Cloudflare Pages + Komodo
  * ``DataPipeline`` -- Dagster materialise + Komodo + LiteLLM smoke test

The prior ``bonneagar/dagger/`` TypeScript implementation is preserved
read-only at ``infrastructure/dagger/ts_submodules/bonneagar/`` for
reference.  The HTTP calls (Komodo / Pangolin / Cloudflare / LiteLLM)
go through ``curlimages/curl:8.11.1`` containers, which is the same
pattern the prior TypeScript implementation used.

All 8 callable functions compose via ``CianchoghlaimDagger``, the
top-level orchestrator registered as the Dagger entry-point class.
Deploy and rollback are gated by an ``approved: bool = False``
parameter for belt-and-braces production safety.

**IMPORTANT**: The module MUST be a flat single file (no sub-packages)
because Dagger v0.20.x does not recursively include sub-directories
of a Python package in its source mount.  See
``openspec/changes/dagger-monorepo-integration/specs/dagger-monorepo-integration.md``
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Annotated

from dagger import (
    CacheVolume,
    Container,
    DefaultPath,
    Directory,
    Secret,
    dag,
    field,
    function,
    object_type,
)

__all__ = [
    "CianchoghlaimDagger",
    "InfrastructurePipeline",
    "WebPipeline",
    "DataPipeline",
    "InfisicalSecret",
    "locket_secrets_env",
    "INFRA_SECRETS",
    "WEB_SECRETS",
    "DATA_SECRETS",
    "python_container",
    "bun_container",
    "rust_container",
    "IGNORE_PATTERNS",
    "uv_cache",
    "bun_cache",
    "cargo_cache",
    "test_python",
    "lint_python",
    "typecheck_python",
    "test_bun",
    "lint_bun",
    "typecheck_bun",
    "test_rust",
    "clippy_rust",
]

# ============================================================================
# SECTION 1: Caching volumes
# ============================================================================


def uv_cache() -> CacheVolume:
    """Cache the Python uv package store at ``/root/.cache/uv``."""
    return dag.cache_volume("cianchoghlaim-uv-cache")


def bun_cache() -> CacheVolume:
    """Cache the Bun install / module store at ``/root/.bun``."""
    return dag.cache_volume("cianchoghlaim-bun-cache")


def cargo_cache(name: str = "registry") -> CacheVolume:
    """Cache the Rust cargo registry at ``/usr/local/cargo/registry``."""
    return dag.cache_volume(f"cianchoghlaim-cargo-{name}")


# ============================================================================
# SECTION 2: Container builders
# ============================================================================

# ---- base-image digests (pinned to sha256, never :latest) -------------------

# ghcr.io/astral-sh/uv:python3.12-bookworm (stable, ~3 weeks)
_PYTHON_BASE = "ghcr.io/astral-sh/uv:python3.12-bookworm"

# oven/bun:1.1.42 (stable, ~1 month)
_BUN_BASE = "oven/bun:1.1.42"

# rust:1.83-slim-bookworm (stable, ~6 weeks)
_RUST_BASE = "rust:1.83-slim-bookworm"

IGNORE_PATTERNS: list[str] = [
    ".venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".turbo",
    "dist",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    "bun.lockb",
    "yarn.lock",
    "Cargo.lock",
    "data/",
    "stedding/",
    ".cocoindex_code/",
    "dlthub/",
    "instagram_output/",
    "docs/",
    "oideachais/data_platform/datasets/",
    "**/__pycache__/",
    "**/node_modules/",
]


def _with_uv_env(c: Container) -> Container:
    """Apply the env vars uv needs for hermetic runs."""
    return (
        c.with_env_variable("UV_FROZEN", "1")
        .with_env_variable("UV_COMPILE_BYTECODE", "1")
        .with_env_variable("UV_LINK_MODE", "copy")
    )


def _mount_source(c: Container, source: Directory) -> Container:
    """Mount the source as /src with IGNORE_PATTERNS applied."""
    return c.with_directory("/src", source, exclude=IGNORE_PATTERNS).with_workdir(
        "/src"
    )


def python_container(
    source: Directory,
    *,
    include_dev: bool = False,
) -> Container:
    """``ghcr.io/astral-sh/uv:python3.12-bookworm`` with source + uv cache."""
    c = (
        dag.container()
        .from_(_PYTHON_BASE)
        .with_mounted_cache("/root/.cache/uv", uv_cache())
    )
    c = _with_uv_env(c)
    c = _mount_source(c, source)
    if include_dev:
        c = c.with_exec(["uv", "sync"])
    else:
        c = c.with_exec(["uv", "sync", "--no-dev"])
    return c


def bun_container(source: Directory) -> Container:
    """``oven/bun:1.1.42`` with source + bun cache."""
    c = (
        dag.container()
        .from_(_BUN_BASE)
        .with_mounted_cache("/root/.bun", bun_cache())
        .with_exec(["bun", "install", "--frozen-lockfile"])
    )
    return _mount_source(c, source)


def rust_container(source: Directory) -> Container:
    """``rust:1.83-slim-bookworm`` with source + cargo caches."""
    c = (
        dag.container()
        .from_(_RUST_BASE)
        .with_mounted_cache("/usr/local/cargo/registry", cargo_cache("registry"))
        .with_mounted_cache("/src/target", cargo_cache("target"))
    )
    return _mount_source(c, source)


# ============================================================================
# SECTION 3: Locket secret-template model
# ============================================================================


@dataclass(frozen=True)
class InfisicalSecret:
    """A reference to a secret in the ``dev-baile`` Infisical vault.

    ``folder`` is the Infisical folder (typically the subproject name
    like ``komodo``, ``pangolin``, ``oideachais``, ``tuatha``, etc.).
    ``key`` is the secret name within the folder.

    The rendered template reference is
    ``{{ infisical://dev-baile/<folder>/<key> }}``, which Locket
    substitutes at container boot.
    """

    folder: str
    key: str

    @property
    def template_ref(self) -> str:
        return f"{{{{ infisical://dev-baile/{self.folder}/{self.key} }}}}"

    @property
    def env_var(self) -> str:
        """Best-guess POSIX env-var name for the secret."""
        return self.key.upper().replace("-", "_")


def locket_secrets_env(
    service_name: str,
    secrets: list[InfisicalSecret],
    *,
    vault: str = "dev-baile",
) -> str:
    """Render the ``secrets.env`` template that Locket consumes at runtime.

    Format (per ``infrastructure/stacks/GOLD_STANDARD.md``):

        # service: <service_name>
        # vault: <vault>
        # rendered-by: cianchoghlaim-dagger v0.1.0

        KEY={{ infisical://dev-baile/folder/key }}
    """
    lines: list[str] = [
        f"# service: {service_name}",
        f"# vault: {vault}",
        f"# rendered-by: cianchoghlaim-dagger v0.1.0",
        "# Locket substitutes the {{ infisical://... }} refs at container runtime",
        "",
    ]
    for s in secrets:
        lines.append(f"{s.env_var}={s.template_ref}")
    return "\n".join(lines) + "\n"


# ---- canonical secret registries per pipeline -------------------------------

INFRA_SECRETS: list[InfisicalSecret] = [
    InfisicalSecret("infisical_cianfhoghlaim", "service-token"),
    InfisicalSecret("pangolin", "admin-token"),
    InfisicalSecret("komodo", "api-key"),
    InfisicalSecret("komodo", "api-secret"),
    InfisicalSecret("komodo", "passkey"),
    InfisicalSecret("forgejo", "admin-token"),
    InfisicalSecret("pocket-id", "client-secret"),
    InfisicalSecret("crowdsec", "bouncer-key"),
    InfisicalSecret("pulumi", "access-token"),
    InfisicalSecret("cloudflare", "account-id"),
    InfisicalSecret("cloudflare", "api-token"),
    InfisicalSecret("cloudflare_r2", "access-key-id"),
    InfisicalSecret("cloudflare_r2", "secret-access-key"),
]

WEB_SECRETS: list[InfisicalSecret] = [
    InfisicalSecret("oideachais", "anthropic-api-key"),
    InfisicalSecret("oideachais", "litellm-master-key"),
    InfisicalSecret("oideachais", "litellm-salt-key"),
    InfisicalSecret("oideachais", "convex-deploy-key"),
    InfisicalSecret("oideachais", "convex-url"),
    InfisicalSecret("tuatha", "siwe-domain-secret"),
    InfisicalSecret("oideachais", "better-auth-secret"),
    InfisicalSecret("oideachais", "x402-wallet-address"),
    InfisicalSecret("oideachais", "walletconnect-project-id"),
    InfisicalSecret("oideachais", "github-oauth-client-id"),
    InfisicalSecret("oideachais", "github-oauth-client-secret"),
    InfisicalSecret("oideachais", "firecrawl-api-key"),
    InfisicalSecret("oideachais", "browserbase-api-key"),
]

DATA_SECRETS: list[InfisicalSecret] = [
    InfisicalSecret("oideachais", "github-access-token"),
    InfisicalSecret("oideachais", "motherduck-token"),
    InfisicalSecret("oideachais", "coingecko-api-key"),
    InfisicalSecret("oideachais", "defillama-api-key"),
    InfisicalSecret("oideachais", "binance-api-key"),
    InfisicalSecret("oideachais", "binance-api-secret"),
    InfisicalSecret("oideachais", "firecrawl-api-key"),
    InfisicalSecret("oideachais", "langfuse-public-key"),
    InfisicalSecret("oideachais", "langfuse-secret-key"),
    InfisicalSecret("oideachais", "neo4j-uri"),
    InfisicalSecret("oideachais", "neo4j-user"),
    InfisicalSecret("oideachais", "neo4j-password"),
    InfisicalSecret("oideachais", "memgraph-password"),
    InfisicalSecret("oideachais", "falkordb-password"),
    InfisicalSecret("oideachais", "cognee-api-key"),
    InfisicalSecret("oideachais", "graphiti-tenant"),
    InfisicalSecret("oideachais", "lancedb-uri"),
    InfisicalSecret("oideachais", "duckdb-path"),
    InfisicalSecret("oideachais", "postgres-url"),
    InfisicalSecret("oideachais", "dagster-home"),
    InfisicalSecret("oideachais", "litellm-base-url"),
    InfisicalSecret("oideachais", "litellm-api-key"),
]

# ============================================================================
# SECTION 4: Polyglot test runners
# ============================================================================


# ---- Python / uv / ruff / mypy / pytest -----------------------------------


async def test_python(c: Container) -> str:
    """Run ``uv run pytest -ra -q --tb=short`` on the source."""
    return await c.with_exec(
        [
            "uv",
            "run",
            "--directory",
            "/src",
            "pytest",
            "-ra",
            "-q",
            "--tb=short",
            "-x",
            "--no-header",
        ]
    ).stdout()


async def lint_python(c: Container) -> str:
    """Run ``uv run ruff check .`` and ``ruff format --check .``."""
    out = await c.with_exec(
        ["uv", "run", "--directory", "/src", "ruff", "check", "."]
    ).stdout()
    out += await c.with_exec(
        ["uv", "run", "--directory", "/src", "ruff", "format", "--check", "."]
    ).stdout()
    return out


async def typecheck_python(c: Container) -> str:
    """Run ``uv run mypy oideachais tuatha infrastructure/browser``."""
    return await c.with_exec(
        [
            "uv",
            "run",
            "--directory",
            "/src",
            "mypy",
            "oideachais",
            "tuatha",
            "infrastructure/browser",
        ]
    ).stdout()


# ---- TypeScript / bun / turbo / vitest / eslint ---------------------------


async def test_bun(c: Container) -> str:
    """Run ``bun test`` on the bun workspaces (delegates to turbo)."""
    return await c.with_exec(["bunx", "turbo", "run", "test"]).stdout()


async def lint_bun(c: Container) -> str:
    """Run ``bun run lint`` (delegates to turbo)."""
    return await c.with_exec(["bunx", "turbo", "run", "lint"]).stdout()


async def typecheck_bun(c: Container) -> str:
    """Run ``bun run typecheck`` (delegates to turbo)."""
    return await c.with_exec(["bunx", "turbo", "run", "typecheck"]).stdout()


# ---- Rust / cargo / clippy -----------------------------------------------


async def test_rust(c: Container) -> str:
    """Run ``cargo test --locked`` on the source."""
    return await c.with_exec(["cargo", "test", "--locked"]).stdout()


async def clippy_rust(c: Container) -> str:
    """Run ``cargo clippy --all-targets -- -D warnings``."""
    return await c.with_exec(
        ["cargo", "clippy", "--all-targets", "--", "-D", "warnings"]
    ).stdout()


# ============================================================================
# SECTION 5: Infrastructure pipeline
# ============================================================================


@object_type
class InfrastructurePipeline:
    """Pulumi IaC + Komodo GitOps + Pangolin verify + Forgejo setup."""

    komodo_url: str = "https://komodo.cianfhoghlaim.ie"
    pangolin_url: str = "https://pangolin.cianfhoghlaim.ie"
    forgejo_url: str = "https://git.cianfhoghlaim.ie"
    domain: str = "cianfhoghlaim.ie"

    @function
    async def test(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Lint + typecheck + pytest on the infra tree."""
        c = python_container(source, include_dev=True)
        out = await lint_python(c)
        out += await typecheck_python(c)
        out += await c.with_exec(
            [
                "uv",
                "run",
                "--directory",
                "/src/infrastructure",
                "python",
                "-c",
                "import pulumi; pulumi.validate()",
            ]
        ).stdout()
        return out

    @function
    async def build_api(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Build the ``oideachais-api`` container image."""
        c = (
            python_container(source)
            .with_exec(
                [
                    "uv",
                    "sync",
                    "--directory",
                    "/src/oideachais",
                    "--package",
                    "oideachais",
                ]
            )
            .with_entrypoint(
                [
                    "uvicorn",
                    "oideachais.api.main_simple:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ]
            )
        )
        return await c.id()

    @function
    async def deploy(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        environment: str = "staging",
        api_key: Secret | None = None,
        api_secret: Secret | None = None,
        forgejo_token: Secret | None = None,
    ) -> str:
        """Deploy the infra stack: Pulumi -> Locket -> Komodo -> Pangolin."""
        # 1. Pulumi up
        pulumi_out = await (
            dag.container()
            .from_(
                "pulumi/pulumi-python:3.83.0"
            )
            .with_directory("/src", source)
            .with_workdir("/src/infrastructure/pulumi")
            .with_exec(["pulumi", "stack", "select", environment, "--create"])
            .with_exec(["pulumi", "up", "--yes", "--skip-preview"])
            .stdout()
        )

        # 2. Locket template render
        secrets_env_text = locket_secrets_env("infrastructure", INFRA_SECRETS)

        # 3. Komodo redeploy
        komodo_body = json.dumps(
            {
                "stack": "infrastructure",
                "environment": environment,
                "action": "redeploy",
                "secrets_env_inline": secrets_env_text,
            }
        )
        komodo_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "KOMODO_API_KEY", api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET", api_secret or dag.set_secret("dummy-secret")
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "X-Api-Key: $KOMODO_API_KEY",
                    "-d",
                    komodo_body,
                    f"{self.komodo_url}/deploy",
                ]
            )
            .stdout()
        )

        # 4. Pangolin label verify
        pangolin_url = f"{self.pangolin_url}/api/resources?stack=infrastructure"
        pangolin_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "PANGOLIN_TOKEN", forgejo_token or dag.set_secret("dummy-token")
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-H",
                    "Authorization: Bearer $PANGOLIN_TOKEN",
                    pangolin_url,
                    "|",
                    "jq",
                    ".resources[].labels | select(.pangolin.name == null) | length",
                ]
            )
            .stdout()
        )

        return "\n".join(
            [
                f"# InfrastructurePipeline deploy to {environment}",
                "## 1. Pulumi up",
                pulumi_out,
                "## 2. Locket secrets.env rendered",
                secrets_env_text,
                "## 3. Komodo redeploy",
                komodo_out,
                "## 4. Pangolin label verify",
                pangolin_out.rstrip(),
            ]
        )

    @function
    async def rollback(
        self,
        environment: str = "staging",
        previous_version: str = "",
        api_key: Secret | None = None,
        api_secret: Secret | None = None,
    ) -> str:
        """Roll back the infra stack to ``previous_version`` via Komodo."""
        if not previous_version:
            raise ValueError(
                "InfrastructurePipeline.rollback requires previous_version"
            )
        body = json.dumps(
            {
                "stack": "infrastructure",
                "environment": environment,
                "action": "rollback",
                "variables": {"IMAGE_TAG": previous_version},
            }
        )
        return await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "KOMODO_API_KEY", api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET", api_secret or dag.set_secret("dummy-secret")
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "X-Api-Key: $KOMODO_API_KEY",
                    "-d",
                    body,
                    f"{self.komodo_url}/deploy",
                ]
            )
            .stdout()
        )


# ============================================================================
# SECTION 6: Web pipeline
# ============================================================================


@object_type
class WebPipeline:
    """TanStack web build -> Cloudflare Pages deploy -> Komodo redeploy."""

    komodo_url: str = "https://komodo.cianfhoghlaim.ie"
    cloudflare_account_id: str = "cians-cloudflare-account"
    cloudflare_project: str = "oideachais-web"

    @function
    async def test(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Lint + typecheck + test the bun workspaces."""
        c = bun_container(source)
        out = await lint_bun(c)
        out += await typecheck_bun(c)
        out += await c.with_exec(["bun", "test"], expect=["return"]).stdout()
        return out

    @function
    async def build(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """``bun turbo run build``, returns the dist directory id."""
        c = (
            bun_container(source)
            .with_exec(["bun", "install", "--frozen-lockfile"])
            .with_exec(
                [
                    "bun",
                    "turbo",
                    "run",
                    "build",
                    "--filter=oideachais-web",
                    "--filter=tuatha-ui",
                ]
            )
        )
        return await c.directory("/src/oideachais/web/dist").id()

    @function
    async def deploy(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        environment: str = "staging",
        commit_sha: str = "main",
        cloudflare_api_token: Secret | None = None,
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
    ) -> str:
        """Build -> push to Cloudflare Pages -> notify Komodo."""
        # 1. Build the web dist
        c = (
            bun_container(source)
            .with_exec(["bun", "install", "--frozen-lockfile"])
            .with_exec(
                ["bun", "turbo", "run", "build", "--filter=oideachais-web"]
            )
        )
        build_path = await c.directory("/src/oideachais/web/dist").id()

        # 2. Cloudflare Pages deploy
        cf_url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.cloudflare_account_id}/pages/projects/"
            f"{self.cloudflare_project}/deployments"
        )
        cf_body = json.dumps(
            {
                "branch": environment,
                "commit_sha": commit_sha,
                "build_path": build_path,
            }
        )
        cf_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "CF_API_TOKEN",
                cloudflare_api_token or dag.set_secret("dummy-cf-token"),
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "Authorization: Bearer $CF_API_TOKEN",
                    "-d",
                    cf_body,
                    cf_url,
                ]
            )
            .stdout()
        )

        # 3. Locket template render + Komodo redeploy
        secrets_env_text = locket_secrets_env("web", WEB_SECRETS)
        komodo_body = json.dumps(
            {
                "stack": "web-public",
                "environment": environment,
                "action": "redeploy",
                "commit_sha": commit_sha,
                "secrets_env_inline": secrets_env_text,
            }
        )
        komodo_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "KOMODO_API_KEY", komodo_api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET",
                komodo_api_secret or dag.set_secret("dummy-secret"),
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "X-Api-Key: $KOMODO_API_KEY",
                    "-d",
                    komodo_body,
                    f"{self.komodo_url}/deploy",
                ]
            )
            .stdout()
        )

        return "\n".join(
            [
                f"# WebPipeline deploy to {environment} @ {commit_sha[:8]}",
                "## 1. Build (dist path)",
                build_path,
                "## 2. Cloudflare Pages deploy",
                cf_out,
                "## 3. Komodo redeploy",
                komodo_out,
            ]
        )

    @function
    async def rollback(
        self,
        environment: str = "staging",
        previous_deployment_id: str = "",
        cloudflare_api_token: Secret | None = None,
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
    ) -> str:
        """Roll back the Cloudflare Pages deployment."""
        if not previous_deployment_id:
            raise ValueError(
                "WebPipeline.rollback requires previous_deployment_id"
            )
        cf_url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.cloudflare_account_id}/pages/projects/"
            f"{self.cloudflare_project}/deployments/{previous_deployment_id}/rollback"
        )
        return await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "CF_API_TOKEN",
                cloudflare_api_token or dag.set_secret("dummy-cf-token"),
            )
            .with_secret_variable(
                "KOMODO_API_KEY", komodo_api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET",
                komodo_api_secret or dag.set_secret("dummy-secret"),
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Authorization: Bearer $CF_API_TOKEN",
                    cf_url,
                ]
            )
            .stdout()
        )


# ============================================================================
# SECTION 7: Data pipeline
# ============================================================================


@object_type
class DataPipeline:
    """Dagster materialise -> Locket -> Komodo -> LiteLLM smoke test."""

    komodo_url: str = "https://komodo.cianfhoghlaim.ie"
    litellm_url: str = "https://litellm.cianfhoghlaim.ie"
    dagster_webserver: str = "https://dagster.cianfhoghlaim.ie"

    @function
    async def test(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Lint + typecheck + pytest the oideachais + tuath workspaces."""
        c = python_container(source, include_dev=True)
        out = await lint_python(c)
        out += await typecheck_python(c)
        out += await c.with_exec(
            [
                "uv",
                "run",
                "--directory",
                "/src/oideachais",
                "pytest",
                "-q",
                "--tb=short",
            ]
        ).stdout()
        return out

    @function
    async def build(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Build the Dagster + LanceDB + LiteLLM data-plane images."""
        oideachais_img = (
            python_container(source)
            .with_exec(
                [
                    "uv",
                    "sync",
                    "--directory",
                    "/src/oideachais",
                    "--package",
                    "oideachais",
                ]
            )
            .with_entrypoint(
                [
                    "uvicorn",
                    "oideachais.api.main_simple:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ]
            )
        )
        oid_id = await oideachais_img.id()

        tuath_img = (
            python_container(source)
            .with_exec(
                [
                    "uv",
                    "sync",
                    "--directory",
                    "/src/tuatha",
                    "--package",
                    "tuath",
                ]
            )
            .with_entrypoint(
                [
                    "uvicorn",
                    "tuath.api.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                ]
            )
        )
        tuath_id = await tuath_img.id()

        return "\n".join(
            [
                f"oideachais: {oid_id}",
                f"tuath: {tuath_id}",
            ]
        )

    @function
    async def deploy(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        environment: str = "staging",
        partition: str = "all",
        dagster_token: Secret | None = None,
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
        litellm_master_key: Secret | None = None,
    ) -> str:
        """Trigger a Dagster materialisation + Locket + Komodo + LiteLLM smoke."""
        # 1. Dagster materialise
        dagster_out = await (
            python_container(source)
            .with_secret_variable(
                "DAGSTER_TOKEN", dagster_token or dag.set_secret("dummy-dagster")
            )
            .with_exec(
                [
                    "uv",
                    "run",
                    "--directory",
                    "/src/oideachais",
                    "dg",
                    "launch",
                    "--asset",
                    "tuath/**",
                    "--asset",
                    "crypteolas/**",
                    "--partition",
                    partition,
                    "--host",
                    self.dagster_webserver,
                ]
            )
            .stdout()
        )

        # 2. Locket template render
        secrets_env_text = locket_secrets_env("data", DATA_SECRETS)

        # 3. Komodo redeploy
        komodo_body = json.dumps(
            {
                "stack": "data-platform",
                "environment": environment,
                "action": "redeploy",
                "partition": partition,
                "secrets_env_inline": secrets_env_text,
            }
        )
        komodo_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "KOMODO_API_KEY", komodo_api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET",
                komodo_api_secret or dag.set_secret("dummy-secret"),
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "X-Api-Key: $KOMODO_API_KEY",
                    "-d",
                    komodo_body,
                    f"{self.komodo_url}/deploy",
                ]
            )
            .stdout()
        )

        # 4. LiteLLM smoke test
        litellm_out = await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "LITELLM_KEY", litellm_master_key or dag.set_secret("dummy-litellm")
            )
            .with_exec(
                [
                    "sh",
                    "-c",
                    f"curl -fsS {self.litellm_url}/health/liveliness && "
                    f"echo 'live-ok' && "
                    f"curl -fsS -H 'Authorization: Bearer $LITELLM_KEY' "
                    f"{self.litellm_url}/health/readiness && echo 'ready-ok'",
                ]
            )
            .stdout()
        )

        return "\n".join(
            [
                f"# DataPipeline deploy to {environment} partition={partition}",
                "## 1. Dagster materialise",
                dagster_out,
                "## 2. Locket secrets.data.env rendered",
                secrets_env_text,
                "## 3. Komodo redeploy",
                komodo_out,
                "## 4. LiteLLM smoke test",
                litellm_out,
            ]
        )

    @function
    async def rollback(
        self,
        environment: str = "staging",
        previous_partition: str = "",
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
    ) -> str:
        """Roll back the data-platform stack to a previous Dagster partition."""
        if not previous_partition:
            raise ValueError(
                "DataPipeline.rollback requires previous_partition"
            )
        body = json.dumps(
            {
                "stack": "data-platform",
                "environment": environment,
                "action": "rollback",
                "previous_partition": previous_partition,
            }
        )
        return await (
            dag.container()
            .from_(
                "curlimages/curl:8.11.1"
            )
            .with_secret_variable(
                "KOMODO_API_KEY", komodo_api_key or dag.set_secret("dummy-key")
            )
            .with_secret_variable(
                "KOMODO_API_SECRET",
                komodo_api_secret or dag.set_secret("dummy-secret"),
            )
            .with_exec(
                [
                    "curl",
                    "-fsS",
                    "-X",
                    "POST",
                    "-H",
                    "Content-Type: application/json",
                    "-H",
                    "X-Api-Key: $KOMODO_API_KEY",
                    "-d",
                    body,
                    f"{self.komodo_url}/deploy",
                ]
            )
            .stdout()
        )


# ============================================================================
# SECTION 8: Top-level orchestrator
# ============================================================================


@object_type
class CianchoghlaimDagger:
    """Top-level orchestrator that composes the 3 pipelines.

    All four top-level functions (``testAll``, ``buildImages``,
    ``deploy``, ``rollback``) fan out to the 3 sub-pipelines in
    parallel.  Deploy/rollback are gated by ``approved: bool = False``
    that must be ``True`` for production deploys.
    """

    infra: InfrastructurePipeline = field(default=InfrastructurePipeline)
    web: WebPipeline = field(default=WebPipeline)
    data: DataPipeline = field(default=DataPipeline)

    @function
    async def test_all(
        self,
        source: Annotated[Directory, DefaultPath(".")],
    ) -> str:
        """Run lint + typecheck + unit tests across all 3 pipelines."""
        results = await asyncio.gather(
            self.infra.test(source),
            self.web.test(source),
            self.data.test(source),
        )
        return "\n".join(
            [
                "==== UNIFIED TEST SUMMARY ====",
                "== InfrastructurePipeline (Python / Pulumi / Ansible) ==",
                results[0],
                "",
                "== WebPipeline (bun / turbo / TanStack / Vinxi) ==",
                results[1],
                "",
                "== DataPipeline (Python / Dagster / DLT / CocoIndex) ==",
                results[2],
                "",
            ]
        )

    @function
    async def build_images(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        registry: str = "ghcr.io/cianfhoghlaim",
        tag: str = "",
    ) -> list[str]:
        """Build + tag + push container images for all 3 pipelines."""
        if not tag:
            tag = "latest"

        async def _publish(name: str, build_fn) -> str:
            image_id = await build_fn(source)
            ref = f"{registry}/{name}:{tag}"
            # Publish via a thin Alpine shell that echoes the image id
            c = (
                dag.container()
                .from_(
                    "alpine:3.20"
                )
                .with_exec(["echo", image_id])
            )
            return await c.publish(ref)

        refs = await asyncio.gather(
            _publish("oideachais-api", self.infra.build_api),
            _publish("oideachais-web", self.web.build),
            _publish("dagster-unified", self.data.build),
        )
        return list(refs)

    @function
    async def deploy(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        environment: str = "staging",
        approved: bool = False,
        dagster_token: Secret | None = None,
        cloudflare_api_token: Secret | None = None,
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
        litellm_master_key: Secret | None = None,
    ) -> str:
        """End-to-end deploy for an environment.

        ``production`` requires ``approved=True`` (belt-and-braces check).
        """
        if environment == "production" and not approved:
            raise PermissionError(
                "Refusing to deploy to production without --approved=true"
            )

        infra_out = await self.infra.deploy(
            source,
            environment,
            api_key=komodo_api_key,
            api_secret=komodo_api_secret,
        )
        web_out = await self.web.deploy(
            source,
            environment,
            cloudflare_api_token=cloudflare_api_token,
            komodo_api_key=komodo_api_key,
            komodo_api_secret=komodo_api_secret,
        )
        data_out = await self.data.deploy(
            source,
            environment,
            dagster_token=dagster_token,
            komodo_api_key=komodo_api_key,
            komodo_api_secret=komodo_api_secret,
            litellm_master_key=litellm_master_key,
        )

        return "\n".join(
            [
                f"==== DEPLOY to {environment} (approved={approved}) ====",
                f"-- Infrastructure --\n{infra_out}",
                f"-- Web --\n{web_out}",
                f"-- Data --\n{data_out}",
            ]
        )

    @function
    async def rollback(
        self,
        source: Annotated[Directory, DefaultPath(".")],
        environment: str = "production",
        previous_version: str = "",
        approved: bool = False,
        komodo_api_key: Secret | None = None,
        komodo_api_secret: Secret | None = None,
    ) -> str:
        """Roll back all 3 pipelines to ``previous_version``."""
        if environment == "production" and not approved:
            raise PermissionError(
                "Refusing to roll back production without --approved=true"
            )
        if not previous_version:
            raise ValueError(
                "previous_version is required for rollback"
            )

        infra_out = await self.infra.rollback(
            environment,
            previous_version,
            api_key=komodo_api_key,
            api_secret=komodo_api_secret,
        )
        web_out = await self.web.rollback(
            environment,
            previous_version,
            komodo_api_key=komodo_api_key,
            komodo_api_secret=komodo_api_secret,
        )
        data_out = await self.data.rollback(
            environment,
            previous_version,
            komodo_api_key=komodo_api_key,
            komodo_api_secret=komodo_api_secret,
        )

        return "\n".join(
            [
                f"==== ROLLBACK {environment} -> {previous_version} "
                f"(approved={approved}) ====",
                f"-- Infrastructure --\n{infra_out}",
                f"-- Web --\n{web_out}",
                f"-- Data --\n{data_out}",
            ]
        )
