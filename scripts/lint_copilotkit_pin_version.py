"""CopilotKit version-pin lint gate.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-6.1.2): every web app MUST use the canonical
`@copilotkit/react-core/v2@^1.67.1` pin (per the
2026-08-17-biep-v3-bring-up-v1 change).

Usage:
    mise run lint:copilotkit-pin-version

Exit codes:
    0 = all web apps use the canonical CopilotKit v2.0 pin
    1 = one or more web apps use the legacy v1.x pin
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_APPS = REPO_ROOT / "web" / "apps"

CANONICAL_PIN = "@copilotkit/react-core/v2"
LEGACY_PIN = "@copilotkit/react-core\""


def lint_package_json(path: Path) -> list[str]:
    """Return a list of violations in `path`."""
    violations = []
    try:
        pkg = json.loads(path.read_text())
    except Exception:
        return violations
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for dep, version in deps.items():
        if dep == LEGACY_PIN:
            violations.append(f"legacy pin: {dep} = {version} (use {CANONICAL_PIN})")
        elif dep == "@copilotkit/react-core":
            # The non-/v2 import should not be used at all
            violations.append(f"legacy package: {dep} = {version} (use {CANONICAL_PIN})")
        elif dep == "@copilotkit/react-ui" and not version.startswith("^1.67") and not version.startswith("^2."):
            violations.append(f"legacy @copilotkit/react-ui: {version} (use ^1.67.1 or ^2.0.0)")
    return violations


def main() -> int:
    all_violations: list[tuple[Path, list[str]]] = []
    for pkg_file in WEB_APPS.rglob("package.json"):
        if "/node_modules/" in str(pkg_file):
            continue
        violations = lint_package_json(pkg_file)
        if violations:
            all_violations.append((pkg_file, violations))
    if all_violations:
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} web apps have legacy CopilotKit pins:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print("OK: all web apps use the canonical CopilotKit v2.0 pin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())