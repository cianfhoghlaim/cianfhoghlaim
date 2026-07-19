"""Bootstrap: ensure the real dlt package (not the local dlt/ directory) wins.

Per the v7 flattened layout, the repo root is added to sys.path by the
editable install (`_editable_impl_cianchoghlaim.pth`). This makes
`import dlt` resolve to the LOCAL `dlt/__init__.py` (which has version
0.4.0 and exposes only `british_isles` + `common` — no `@dlt.source`).

To run the BIEP v3 jurisdiction pipelines (which need dlt >= 1.x), we
must remove the repo root from sys.path BEFORE any `import dlt`, then
import the local submodules (`dlt.british_isles`, `dlt.common`) via
load_source_module directly.

Usage (must be FIRST import in your script):
    import scripts.bootstrap_dlt  # noqa: F401
    import dlt  # now resolves to the real dlt 1.29.0

After bootstrap:
    - `import dlt` → real dlt 1.29.0
    - `from dlt.british_isles.ireland.education.ireland_jurisdiction_pipeline import ...`
      → loads the local dlt/british_isles/* via importlib
"""
from __future__ import annotations

import importlib.util
import os
import sys
import types

# 1. Compute the paths
_VENV_SITE_PACKAGES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".venv",
    "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Remove the repo root from sys.path if present (so local dlt/ doesn't shadow)
sys.path = [p for p in sys.path if os.path.realpath(p) != os.path.realpath(_REPO_ROOT)]

# 3. Insert venv site-packages at position 0 (if present)
if os.path.isdir(_VENV_SITE_PACKAGES) and _VENV_SITE_PACKAGES not in sys.path:
    sys.path.insert(0, _VENV_SITE_PACKAGES)

# 4. Pre-import the real dlt so it's in sys.modules
_real_dlt = importlib.import_module("dlt")

# 5. Now register the local `dlt.british_isles` and `dlt.common` as
# synthetic submodules of the real `dlt` package. We do this by
# manually loading the local packages and registering them under the
# real `dlt` name.
def _load_local_as_submodule(local_pkg_name: str) -> None:
    """Load a local package (from repo root) as `dlt.<local_pkg_name>`."""
    real_name = f"dlt.{local_pkg_name}"
    if real_name in sys.modules:
        return  # already registered
    spec = importlib.util.spec_from_file_location(
        real_name,
        os.path.join(_REPO_ROOT, "dlt", local_pkg_name, "__init__.py"),
        submodule_search_locations=[
            os.path.join(_REPO_ROOT, "dlt", local_pkg_name),
        ],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"bootstrap_dlt: cannot load {real_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[real_name] = module
    spec.loader.exec_module(module)

# Register local dlt.british_isles + dlt.common
for local_pkg in ("common", "british_isles"):
    _load_local_as_submodule(local_pkg)

# 6. Sanity check
assert hasattr(_real_dlt, "source"), (
    f"bootstrap_dlt: real dlt should have 'source' attribute; "
    f"got dlt={_real_dlt.__file__} v{_real_dlt.__version__}"
)
assert "dlt.british_isles" in sys.modules, (
    "bootstrap_dlt: dlt.british_isles should be in sys.modules"
)