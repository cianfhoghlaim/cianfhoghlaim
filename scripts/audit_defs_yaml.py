"""Validate every orchestration/defs/**/defs.yaml against Dagster component resolution.

Read-only. Reports, per file: the declared `type:`, whether that symbol resolves,
whether it is a Component subclass, and whether its `attributes:` block validates
against the model Dagster derives for it.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFS = ROOT / "orchestration" / "defs"
sys.path.insert(0, str(ROOT))

import dagster as dg  # noqa: E402

results: list[dict] = []

for path in sorted(DEFS.rglob("defs.yaml")):
    rel = str(path.relative_to(ROOT))
    row: dict = {"file": rel, "type": None, "status": None, "detail": ""}
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception as e:
        row.update(status="YAML_PARSE_ERROR", detail=f"{type(e).__name__}: {e}")
        results.append(row)
        continue

    if not isinstance(doc, dict):
        row.update(status="NOT_A_MAPPING", detail=type(doc).__name__)
        results.append(row)
        continue

    tname = doc.get("type")
    row["type"] = tname
    if tname is None:
        row.update(status="NO_TYPE_FIELD", detail=f"top-level keys: {sorted(doc)}")
        results.append(row)
        continue

    mod_path, _, sym = str(tname).rpartition(".")
    try:
        mod = importlib.import_module(mod_path)
    except Exception as e:
        row.update(status="MODULE_IMPORT_FAILED", detail=f"{type(e).__name__}: {e}")
        results.append(row)
        continue

    obj = getattr(mod, sym, None)
    if obj is None:
        row.update(status="MISSING_CLASS", detail=f"{mod_path} has no attribute {sym!r}")
        results.append(row)
        continue

    if not (isinstance(obj, type) and issubclass(obj, dg.Component)):
        row.update(status="NOT_A_COMPONENT", detail=f"resolved to {type(obj).__name__}")
        results.append(row)
        continue

    try:
        model_cls = obj.get_model_cls()
    except Exception as e:
        row.update(status="NO_MODEL_CLS", detail=f"{type(e).__name__}: {e}")
        results.append(row)
        continue

    if model_cls is None:
        row.update(status="MODEL_CLS_NONE", detail="component derives no attributes model")
        results.append(row)
        continue

    attrs = doc.get("attributes", {}) or {}
    try:
        model_cls(**attrs) if not hasattr(model_cls, "model_validate") else model_cls.model_validate(attrs)
        row.update(status="OK", detail=model_cls.__name__)
    except Exception as e:
        msg = str(e).replace("\n", " ")[:220]
        row.update(status="SCHEMA_FAIL", detail=f"{model_cls.__name__}: {msg}")

    results.append(row)

counts = Counter(r["status"] for r in results)
print(f"defs.yaml files checked: {len(results)}\n")
for status, n in counts.most_common():
    print(f"  {n:>4}  {status}")

print("\n--- non-OK, grouped by (status, type) ---")
grouped: Counter = Counter(
    (r["status"], r["type"]) for r in results if r["status"] != "OK"
)
for (status, tname), n in grouped.most_common():
    print(f"  {n:>4}  {status:<22} {tname}")

print("\n--- first example per (status, type) ---")
seen = set()
for r in results:
    k = (r["status"], r["type"])
    if r["status"] == "OK" or k in seen:
        continue
    seen.add(k)
    print(f"\n{r['status']}  [{r['type']}]\n  {r['file']}\n  {r['detail']}")

if "--json-out" in sys.argv:
    out = pathlib.Path(sys.argv[sys.argv.index("--json-out") + 1])
    out.write_text(json.dumps(results, indent=2))
    print(f"\nfull results -> {out}")

# Exit non-zero when anything fails, so this can gate CI. `dg.load_defs()`
# aborts on the FIRST bad file, so a single failure here means the whole
# code location silently falls back to `_defs_walker` — which ignores all
# YAML and loads zero Components.
sys.exit(0 if counts.get("OK", 0) == len(results) else 1)
