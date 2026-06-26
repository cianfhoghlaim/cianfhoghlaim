# Proposal: Round 11 Phase 11 (tuatha Phase 3) — Fix tuatha packaging issue + add 5 missing `__init__.py` + fix 3 wrong import names + add `fix-pth.sh`

## Why

The tuatha quadrant has 3 packaging problems that prevent
`import tuatha` from working (the canonical package name
matches the on-disk directory `sruth/tuatha/`):

### Problem 1: `sruth/tuatha/__init__.py` does not exist

Without `sruth/tuatha/__init__.py`, `tuatha` is NOT a real
Python package — it's a PEP 420 namespace package with
unpredictable import resolution. The README "Known issues"
table row #3 acknowledges this:

> `sruth/tuatha/__init__.py` does not exist, and
> `sruth/tuatha/pyproject.toml` declares only sub-packages
> under `[tool.hatch.build.targets.wheel].packages`. The
> `tuatha` package itself is not importable.
> `sruth/tuatha/tests/conftest.py:8` does
> `from tuath.api.main import app` which fails. This blocks
> pytest collection (the conftest can't even load).
> Workaround: run `pytest --noconftest`.

The croilar quadrant fixed the same issue in commit
`e9e0fc7d2` ("fix(croilar): close issue #17 — packaging fix
for the dagster code-location"). The fix has 4 parts:
1. Create `croilar/__init__.py`
2. Change `[tool.hatch.build.targets.wheel]` `.packages = ["."]`
   so hatch auto-detects subdirs with `__init__.py`
3. Create `croilar/scripts/fix-pth.sh` post-install script
   that rewrites the broken uv-generated `.pth` file
4. Modify `croilar/tests/conftest.py` + `croilar/tests/dagster_defs/test_definitions_loads.py`

### Problem 2: 3 sub-packages in `pyproject.toml` lack `__init__.py`

`sruth/tuatha/pyproject.toml` lists 12 sub-packages under
`[tool.hatch.build.targets.wheel].packages`. Three of them
don't have `__init__.py`:

| Sub-package | Status |
|:--|:--|
| `dlt_sources` | ✓ HAS `__init__.py` |
| `dagster_assets` | ✓ HAS `__init__.py` |
| `cocoindex_flows` | ✗ **MISSING** `__init__.py` |
| `knowledge_graph` | ✓ HAS `__init__.py` |
| `agents` | ✗ **MISSING** `__init__.py` |
| `api` | ✗ **MISSING** `__init__.py` |
| `storage` | ✓ HAS `__init__.py` |
| `asset_generation` | ✓ HAS `__init__.py` |
| `dlt_utils` | ✓ HAS `__init__.py` |
| `fibo_generation` | ✓ HAS `__init__.py` |
| `demo` | ✓ HAS `__init__.py` |
| `tests` | ✓ HAS `__init__.py` |

The 3 missing `__init__.py` files are an actual hatch build
risk — if hatch is strict about validating the manifest
matches filesystem reality, the build will fail. PEP 420
namespace packages happen to work because Python falls back
to them, but they're fragile (especially for the `transforms/`
subdir of `cocoindex_flows/`, which is a sub-package inside
a sub-package — PEP 420 namespace packages CANNOT contain
sub-packages at all).

### Problem 3: 3 test files use wrong import name (`tuath` instead of `tuatha`)

Three test files were aspirationally written against an
incorrect import name (probably a typo that was never run):

| File | Wrong | Correct |
|:--|:--|:--|
| `sruth/tuatha/tests/conftest.py:8` | `from tuath.api.main import app` | `from tuatha.api.main import app` |
| `sruth/tuatha/tests/test_graphiti_integration.py:8` | `from tuath.knowledge_graph.graphiti import ...` | `from tuatha.knowledge_graph.graphiti import ...` |
| `sruth/tuatha/tests/test_hybrid_search.py:8` | `from tuath.knowledge_graph import ...` | `from tuatha.knowledge_graph import ...` |

The directory is `sruth/tuatha/` (with the trailing 'a') so
the import name MUST be `tuatha`, not `tuath`. The pyproject
distribution name is `tuath` (without 'a') which is fine —
distribution name and import name can differ (e.g. `pip install tuath` →
`import tuatha`). The tests use the import name `tuath`, which
never worked against any directory.

## Verification (pre-flight, all done)

```
$ uv run python -c "import tuath"
ModuleNotFoundError: No module named 'tuath'

$ PYTHONPATH=./sruth/tuatha uv run python -c "from tuath.api.main import app"
ModuleNotFoundError: No module named 'tuath'

$ PYTHONPATH=./sruth/tuatha uv run python -c \
    "from cocoindex_flows.transforms.celtic_multilingual import ..."
ModuleNotFoundError: No module named 'cocoindex_flows.transforms.celtic_multilingual'
```

The 3rd test fails because `cocoindex_flows/` is a PEP 420
namespace package — namespace packages can't contain
**sub-packages** (they're only allowed to contain modules).
Adding `__init__.py` to `cocoindex_flows/` AND `transforms/`
fixes this (but the canonical import is now
`from tuatha.cocoindex_flows.transforms.X` since `cocoindex_flows`
is a sub-package of `tuatha`).

## What changes

### 1. CREATE `sruth/tuatha/__init__.py` (canonical package marker)

A 14-line docstring matching the croilar pattern. This
makes `tuatha` a real Python package (importable as
`from tuatha.X import Y`).

### 2. CREATE `sruth/tuatha/api/__init__.py` (empty package marker)

Empty file — converts `api/` from PEP 420 namespace
package to a real package. 1-line content.

### 3. CREATE `sruth/tuatha/agents/__init__.py` (empty package marker)

Empty file — converts `agents/` from PEP 420 namespace
package to a real package. 1-line content.

### 4. CREATE `sruth/tuatha/cocoindex_flows/__init__.py` (empty package marker)

Empty file — converts `cocoindex_flows/` from PEP 420
namespace package to a real package. 1-line content.

### 5. CREATE `sruth/tuatha/cocoindex_flows/transforms/__init__.py` (empty package marker)

Empty file — allows `from tuatha.cocoindex_flows.transforms.X`
to work. PEP 420 namespace packages cannot contain
sub-packages; only real packages can. 1-line content.

### 6. MODIFY `sruth/tuatha/pyproject.toml`

Change the explicit sub-packages list:

```diff
 [tool.hatch.build.targets.wheel]
-# Sub-packages included in the tuath wheel. After the consolidation of
-# códeolas, crypteolas, and crypteolas_demo into tuatha/, this list is
-# extended to include the new sub-packages and the previously-omitted
-# ones (asset_generation, dlt_utils, fibo_generation, tests, demo).
-# Note: codeolas, crypteolas, and crypteolas_demo are loaded as separate
-# workspace members and are NOT included in the tuath wheel.
-packages = [
-    "dlt_sources",
-    "dagster_assets",
-    "cocoindex_flows",
-    "knowledge_graph",
-    "agents",
-    "api",
-    "storage",
-    "asset_generation",
-    "dlt_utils",
-    "fibo_generation",
-    "demo",
-    "tests",
-]
+# Round 11 Phase 11 (tuatha Phase 3): declare the project root (`.`)
+# so hatch auto-detects sub-packages that have an `__init__.py`.
+# Previously this was an explicit sub-packages list (12 entries).
+# The fix mirrors the croilar packaging fix from commit
+# `e9e0fc7d2` ("fix(croilar): close issue #17 — packaging fix
+# for the dagster code-location"). It makes `tuatha` itself a
+# real Python package (importable as `from tuatha.X import Y`),
+# unblocking `sruth/tuatha/tests/conftest.py:8: from tuatha.api.main import app`.
+# Note: codeolas, crypteolas, and crypteolas_demo are loaded as separate
+# workspace members and are NOT included in the tuath wheel.
+packages = ["."]
```

### 7. CREATE `sruth/tuatha/scripts/fix-pth.sh` (post-install .pth rewriter)

A 64-line bash script that mirrors
`sruth/croilar/scripts/fix-pth.sh` exactly. It rewrites
`/Users/.../.venv/lib/python3.13/site-packages/_editable_impl_tuath.pth`
to contain a single line — `sruth/` (the parent of `tuatha/`).
This makes `import tuatha` succeed in the dev venv.

### 8. FIX 3 wrong import names in test files

| File | Change |
|:--|:--|
| `sruth/tuatha/tests/conftest.py:8` | `from tuath.api.main import app` → `from tuatha.api.main import app` |
| `sruth/tuatha/tests/test_graphiti_integration.py:8` | `from tuath.knowledge_graph.graphiti import ...` → `from tuatha.knowledge_graph.graphiti import ...` |
| `sruth/tuatha/tests/test_hybrid_search.py:8` | `from tuath.knowledge_graph import ...` → `from tuatha.knowledge_graph import ...` |

## What does NOT change

- The 4 spec-mandated thin re-export shims at
  `sruth/tuatha/agents/adk/{celtic_tutor,mythology_narrator,quest_guide,research_assistant}.py`
  — these are inside `agents/` which becomes a real package
  via the new `__init__.py`. Different scope.
- `sruth/tuatha/cocoindex_flows/mythology_embedding.py` (7339 bytes)
  — real cocoindex transform_flow, kept as-is (no functional
  change). Now properly importable as
  `from tuatha.cocoindex_flows.mythology_embedding import ...`.
- The pre-existing
  `sruth/oideachais/agents/adk/research_agent.py:114` Pydantic
  `ValidationError: ThinkingConfig.thinking_budget_tokens`
  — out of scope.
- The docs at `.agents/skills/tuatha-mmo/references/*.md` —
  they use the wrong import name `tuath` (no 'a'). Out of
  scope for this Phase (will fix in a docs cleanup change).
- `sruth/tuatha/summary.txt` — contains `from tuath.db import ...`
  (wrong import name). Out of scope (this is data, not code).

## Out of scope (deferred to other changes)

- The `mise.toml` change to register the post-install
  hook (mirroring the croilar fix's 18-line diff). This would
  automate `bash sruth/tuatha/scripts/fix-pth.sh` after every
  `uv sync`. Deferred to a future Phase.
- The doc fix for the wrong import name `tuath` (no 'a') in
  `.agents/skills/tuatha-mmo/references/*.md` (5 files) +
  `sruth/tuatha/summary.txt` (1 file). Deferred to a docs
  cleanup change.

## Impact

- **Net change**: 5 new `__init__.py` files (5 lines total)
  + 1 new `fix-pth.sh` script (64 lines) + 1 pyproject.toml
  modification (12-line list → 1-line declaration + comment)
  + 3 test file 1-line fixes.
- **Files touched**: 6 new + 4 modified + 1 README.md
  update + 1 spec delta.
- **No spec deletion**: spec is silent on the packaging
  issue; the change adds 1 NEW requirement
  (no-missing-package-init-py-in-tuatha).
- **Build risk**: very low. The new `__init__.py` files
  are empty markers (no side effects). The pyproject
  change matches the croilar fix pattern (already
  battle-tested in production).
- **Behaviour change**: `import tuatha` becomes importable
  for the first time. `import tuatha.cocoindex_flows.transforms.X`
  becomes importable for the first time. `from tuath.X`
  imports in 3 test files now resolve to the correct
  `sruth/tuatha/X/` paths.