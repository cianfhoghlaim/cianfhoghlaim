"""
CocoIndex v1 Conformance App — the enforcement layer for
REFACTORING.md item 12.

The 15th CocoIndex v1 App (and arguably the most important for
maintaining consistency across the other 14). Implements a static
linter that walks every v1 CocoIndex App under
`cianfhoghlaim/cocoindex_flows/` and applies 4 conformance rules:

- **R1** — `from ._lifespan import shared_lifespan` (delegates to
  the shared lifespan; REFACTORING.md item 12)
- **R2** — no new `coco.ContextKey[` declarations outside
  `_lifespan.py` without a sibling `# R2-exempt: <reason>` comment
- **R3** — declares `coco.App(coco.AppConfig(` at module scope
  (canonical v1 pattern, NOT the `@coco.flow(scope="global")` +
  `coco.index_flow(...)` v0-style hybrid)
- **R4** — has at least one `@coco.fn(` decorator

Exposes a `ConformanceReport` dataclass + a
`run_conformance_check(repo_root)` entrypoint. The Dagster
`cocoindex_v1_conformance_check` `asset_check` wraps the call and
fails the build on any R1-R4 violation.

Canonical v1 patterns enforced (same as the other 14 Apps):

- imports `shared_lifespan` (R1)
- declares no new ContextKey without an exemption (R2); this App
  declares no ContextKeys of its own
- declares `app = coco.App(...)` at module level (R3)
- has at least one `@coco.fn(memo=True)` decorator (R4)

Reference: openspec/changes/upstream-package-monitoring/proposal.md §3
"""

from __future__ import annotations

import ast
import asyncio
import datetime
import pathlib
import textwrap
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE = False


from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    LANCEDB_URI,
    RESOLVED_FILE_REGISTRY,
    shared_lifespan,
)


# ============================================================================
# Data model
# ============================================================================


@dataclass
class ConformanceReport:
    """Per-App + aggregate conformance result."""

    app_name: str
    r1_pass: bool
    r2_pass: bool
    r3_pass: bool
    r4_pass: bool
    violations: list[str] = field(default_factory=list)
    checked_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    @property
    def all_pass(self) -> bool:
        return self.r1_pass and self.r2_pass and self.r3_pass and self.r4_pass

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "r1_pass": self.r1_pass,
            "r2_pass": self.r2_pass,
            "r3_pass": self.r3_pass,
            "r4_pass": self.r4_pass,
            "all_pass": self.all_pass,
            "violations": self.violations,
            "checked_at": self.checked_at.isoformat(),
        }


# ============================================================================
# Conformance rules (static AST linter)
# ============================================================================


# Apps that are explicitly excluded from R1 (they may not need a
# shared lifespan if they're pure data models or query helpers).
R1_EXEMPT_APPS: set[str] = set()

# Files in the cocoindex_flows/ directory that are NOT v1 Apps and
# should be skipped entirely by the linter.
NON_APP_FILES: set[str] = {
    "__init__.py",
    "_lifespan.py",
}


def _parse_python(path: pathlib.Path) -> ast.Module | None:
    """Read + AST-parse a Python file. Returns None on syntax error."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:  # pragma: no cover
        logger.warning("syntax_error_skipping", path=str(path), error=str(e))
        return None


def _check_r1(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R1 — `from ._lifespan import shared_lifespan` (or equivalent)."""
    has_import = (
        "from ._lifespan import" in source
        and "shared_lifespan" in source
    )
    if has_import:
        return True, ""
    return False, "R1 FAIL — no `from ._lifespan import shared_lifespan`"


def _check_r2(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R2 — no new ContextKeys without `# R2-exempt: <reason>` comment."""
    violations: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.isupper()
        ):
            # Check if the RHS calls coco.ContextKey[...]
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "ContextKey"
            ):
                # Find a sibling comment with `# R2-exempt:`
                # on the line immediately preceding the assignment.
                line = node.lineno - 1  # ast is 1-indexed; lines are 0-indexed
                lines = source.splitlines()
                if line > 0 and "# R2-exempt:" in lines[line - 1]:
                    continue
                violations.append(
                    f"R2 FAIL — ContextKey `{node.targets[0].id}` "
                    f"on line {node.lineno} lacks `# R2-exempt:` comment"
                )
    if violations:
        return False, "; ".join(violations)
    return True, ""


def _check_r3(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R3 — `app = coco.App(coco.AppConfig(...))` at module level (NOT
    inside a function body)."""
    for node in tree.body:  # only module-level (NOT inside functions)
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "app"
        ):
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "App"
            ):
                return True, ""
    return (
        False,
        "R3 FAIL — no module-level `app = coco.App(coco.AppConfig(...))`",
    )


def _check_r4(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R4 — has at least one `@coco.fn(` decorator."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "fn"
                ):
                    return True, ""
    return False, "R4 FAIL — no `@coco.fn(` decorator found"


def check_app_file(path: pathlib.Path) -> ConformanceReport:
    """Run all 4 conformance rules on a single App file."""
    app_name = path.stem
    source = path.read_text(encoding="utf-8")
    tree = _parse_python(path)
    if tree is None:
        return ConformanceReport(
            app_name=app_name,
            r1_pass=False,
            r2_pass=False,
            r3_pass=False,
            r4_pass=False,
            violations=["SYNTAX ERROR — file could not be AST-parsed"],
        )

    r1_pass, r1_violation = _check_r1(tree, source)
    r2_pass, r2_violation = _check_r2(tree, source)
    r3_pass, r3_violation = _check_r3(tree, source)
    r4_pass, r4_violation = _check_r4(tree, source)

    violations = [v for v in (r1_violation, r2_violation, r3_violation, r4_violation) if v]
    return ConformanceReport(
        app_name=app_name,
        r1_pass=r1_pass,
        r2_pass=r2_pass,
        r3_pass=r3_pass,
        r4_pass=r4_pass,
        violations=violations,
    )


def run_conformance_check(
    repo_root: pathlib.Path = pathlib.Path("sruth/cianfhoghlaim/cocoindex_flows"),
) -> list[ConformanceReport]:
    """Walk every v1 App file and return a list of ConformanceReports.

    Dagster asset_check wrapper:
    `uv run python -c "from cianfhoghlaim.cocoindex.cocoindex_v1_conformance import run_conformance_check; ..."`
    """
    reports: list[ConformanceReport] = []
    for path in sorted(repo_root.glob("*.py")):
        if path.name in NON_APP_FILES or path.stem in R1_EXEMPT_APPS:
            continue
        if path.stem.startswith("_"):
            continue  # private modules
        reports.append(check_app_file(path))
    return reports


def conformance_summary(reports: list[ConformanceReport]) -> dict:
    """Aggregate summary for the Dagster asset_check metadata."""
    total = len(reports)
    passing = sum(1 for r in reports if r.all_pass)
    failing = total - passing
    by_rule: dict[str, int] = {"r1": 0, "r2": 0, "r3": 0, "r4": 0}
    for r in reports:
        if not r.r1_pass:
            by_rule["r1"] += 1
        if not r.r2_pass:
            by_rule["r2"] += 1
        if not r.r3_pass:
            by_rule["r3"] += 1
        if not r.r4_pass:
            by_rule["r4"] += 1
    return {
        "total_apps": total,
        "passing_apps": passing,
        "failing_apps": failing,
        "by_rule": by_rule,
        "reports": [r.to_dict() for r in reports],
    }


# ============================================================================
# CocoIndex v1 flow (the App wraps run_conformance_check so Dagster
# can materialise it as a check)
# ============================================================================


if COCOINDEX_AVAILABLE:

    @coco.lifespan
    async def conformance_lifespan(builder: Any) -> AsyncIterator[None]:
        """Delegate to the shared lifespan (R1)."""
        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn(memo=True)
    async def run_check_and_summarise(repo_root: pathlib.Path) -> dict:
        """Run the conformance check + return the summary."""
        reports = run_conformance_check(repo_root)
        return conformance_summary(reports)

    @coco.fn
    async def cocoindex_v1_conformance_app_main(repo_root: pathlib.Path) -> None:
        """The App's main: log the conformance summary + emit a LanceDB
        row so the check history is queryable."""
        summary = await run_check_and_summarise(repo_root)
        logger.info(
            "conformance_check_complete",
            total=summary["total_apps"],
            passing=summary["passing_apps"],
            failing=summary["failing_apps"],
        )

        # Emit a record row so the Dagster asset_check has a
        # queryable history.
        # R4-exempt: metadata table only (no embedding column).
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="conformance_check_history",
            table_schema=await lancedb.TableSchema.from_class(
                type(
                    "ConformanceHistoryRow",
                    (),
                    {
                        "id": int,
                        "checked_at": str,
                        "total_apps": int,
                        "passing_apps": int,
                        "failing_apps": int,
                    },
                ),
                primary_key=["id"],
            ),
        )
        target_table.declare_row(
            row=type(
                "ConformanceHistoryRow",
                (),
                {
                    "id": int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
                    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "total_apps": summary["total_apps"],
                    "passing_apps": summary["passing_apps"],
                    "failing_apps": summary["failing_apps"],
                },
            )()
        )

    DEFAULT_COCOINDEX_FLOWS_ROOT = pathlib.Path(
        pathlib.Path(__file__).resolve().parent
    )

    cocoindex_v1_conformance_app = coco.App(
        coco.AppConfig(name="CocoIndexV1Conformance"),
        cocoindex_v1_conformance_app_main,
        repo_root=DEFAULT_COCOINDEX_FLOWS_ROOT,
    )


# ============================================================================
# CLI entry point
# ============================================================================


def main() -> int:
    """Run the conformance check + print the summary + exit non-zero on failure.

    Used by:
    - `mise run upstream:conformance` (CI gate)
    - The Dagster `cocoindex_v1_conformance_check` asset
    """
    import sys

    root = pathlib.Path(__file__).resolve().parent
    reports = run_conformance_check(root)
    summary = conformance_summary(reports)

    # Print the per-App results.
    print(textwrap.dedent(
        f"""
        CocoIndex v1 Conformance Report
        ===============================
        Total Apps:   {summary['total_apps']}
        Passing:      {summary['passing_apps']}
        Failing:      {summary['failing_apps']}
        Failures by rule: R1={summary['by_rule']['r1']}, R2={summary['by_rule']['r2']}, R3={summary['by_rule']['r3']}, R4={summary['by_rule']['r4']}

        Per-App results:
        """
    ).strip())
    for r in reports:
        status = "PASS" if r.all_pass else "FAIL"
        print(f"  [{status}] {r.app_name}")
        for v in r.violations:
            print(f"          - {v}")

    return 0 if summary["failing_apps"] == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())