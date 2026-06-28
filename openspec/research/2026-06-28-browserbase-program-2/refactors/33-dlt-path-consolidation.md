# Agent 33 — dlt Path Consolidation (`dlt_sources/` drift) — Refactor Spec

> **P0-6 from Agent 26 refactor prioritizer** (BLOCKING — misleading spec, 8+ files).
> Cross-references: `agent-01-dlt.md:26` (drift correction note), `synthesis/26-refactor-prioritizer.md` (P0-6), `synthesis/28-misunderstandings-corrector.md` (C-SP.5, P1A-01), `agent-28.md` §7 item 9.
> Files in scope: 12 live `openspec/specs/*.md` + 8 active `openspec/changes/*/proposal.md` + 253 `cianfhoghlaim/**` files + 24 `.agents/skills/**` + 1 `_oideachais_pyproject.toml` + 1 README.

---

## 1. TL;DR

There is a **2-layer path drift** on `dlt_sources/` post-v4 consolidation: (a) the spec layer still says `sruth/oideachais/dlt_sources/` (pre-v4) in 12 live specs + ~40 active change proposals, and (b) the **Python import layer is also broken** — `cianfhoghlaim/_oideachais_pyproject.toml:39` lists `packages = ["dlt_sources", ...]` but the on-disk directory is `_oideachais_dlt_sources/`, so `from dlt_sources.ie.education.leaving_cert import leaving_cert_source` (called in `core/dlt/_oideachais_dlt_utils/source_factory.py:299`) raises `ModuleNotFoundError` today. The fix is a single coordinated rename: **the `_oideachais_dlt_sources/` directory on disk becomes the canonical `dlt_sources/`**, the pyproject's `packages = ["dlt_sources"]` line is no longer a lie, all 253+ cianfhoghlaim/ imports and 12 live spec paths get sed-rewritten, and a pre-push hook blocks any future commit that reintroduces `sruth/oideachais/dlt_sources/` or the unprefixed `_oideachais_dlt_sources/` directory. Total scope: 5 steps, ~7 hours of focused work, single PR.

---

## 2. The drift (concrete evidence, 4 confirmed facts)

### 2.1 What the spec files claim

Per `synthesis/28-misunderstandings-corrector.md:87` and `agent-01-dlt.md:26`:

> "dlt sources live at `cianfhoghlaim/dlt_sources/` (28 sources)" — Actually `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 `.py` files, 12 subdirs).

Spot-check of the 12 live `openspec/specs/*/spec.md` files that mention `dlt_sources`:

| Spec | Wrong path it claims | Wrong layer |
|:--|:--|:--|
| `openspec/specs/oideachais-pipeline/spec.md` (5+ lines) | `sruth/oideachais/dlt_sources/uk/northern_ireland/ccea_curriculum.py` | pre-v4 |
| `openspec/specs/oideachais-pipeline/spec.md` | `sruth/oideachais/dlt_sources/domains/medicine/ie/hse.py` | pre-v4 |
| `openspec/specs/oideachais-pipeline/spec.md` | `sruth/oideachais/dlt_sources/ireland/curriculum/*` | pre-v4 |
| `openspec/specs/cross-domain-registry/spec.md:5` | `sruth/oideachais/dlt_sources/official_media/fixtures/identity_<slug>.json` | pre-v4 |
| `openspec/specs/oideachais-leabharlann/spec.md` (3 lines) | `sruth/oideachais/dlt_sources/leabharlann/` | pre-v4 |
| `openspec/specs/agent-registry/spec.md:43,249` | `dlt_sources/` (relative — ambiguous) | ambiguous |
| `openspec/specs/upstream-package-monitoring/spec.md` | mentions `dlt_sources/` | ambiguous |
| `openspec/specs/tuatha-platform/spec.md` | mentions `dlt_sources/` | ambiguous |
| `openspec/specs/author-archive-uog-coursework/spec.md` | mentions `dlt_sources/` | ambiguous |
| `openspec/specs/data-engineering-pipeline-documentation/spec.md` | `sruth/oideachais/dlt_sources` | pre-v4 |
| `openspec/specs/meaisinfhoghlaim-platform/spec.md` | `sruth/oideachais/dlt_sources` | pre-v4 |
| `openspec/specs/infrastructure-stacks/spec.md` | mentions `dlt_sources/` | ambiguous |

Plus 8 active (non-archived) `openspec/changes/*/proposal.md` files with hard-coded `sruth/oideachais/dlt_sources/` references (the worst offender being `openspec/changes/wire-baml-with-known-consumers/proposal.md:22-130` with 6 occurrences, including a verification step `from oideachais.dlt_sources.ireland.aistear import …` that will never pass).

### 2.2 What the disk actually has

```
$ ls cianfhoghlaim/dlt_sources/
ls: cianfhoghlaim/dlt_sources/: No such file or directory

$ ls cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/
__init__.py   common/   constants/   cross/   en/   ggy/   ie/   iom/   jey/   law/
leabharlann/  ni/      official_media/  sct/   site_analysis/  wls/   README.md

$ find cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources -name "*.py" | wc -l
190
```

So the on-disk reality is:
- **190 Python source files** (not 28 — Agent 01's P1A-01 first pass undercounted by ~7×)
- 12 subdirs (`ie/`, `en/`, `ni/`, `sct/`, `wls/`, `ggy/`, `iom/`, `jey/`, `cross/`, `leabharlann/`, `law/`, `official_media/`, plus flat `common/`, `constants/`, `site_analysis/`)
- 11 nation-level namespaces (one per British Isles + Crown Dependencies)

### 2.3 The Python import is also broken (the second, more important drift)

This is the drift that makes the issue **runtime-breaking, not just misleading**:

```python
# cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py:252
from dlt_sources.common.firecrawl_source import create_firecrawl_source

# cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py:299
from dlt_sources.ie.education.leaving_cert import leaving_cert_source

# cianfhoghlaim/core/curriculum/celtic/duchas_images.py:19
from dlt_sources.duchas_images import duchas_images_source
```

These imports are **completely broken today** because:

```toml
# cianfhoghlaim/_oideachais_pyproject.toml (hatch wheel targets)
[tool.hatch.build.targets.wheel]
packages = [
    "dlt_sources",   # ← CLAIMED package name
    "dlt_utils",
    "cocoindex_flows",
    ...
]
```

But the on-disk directory name is `_oideachais_dlt_sources/` (with the `_oideachais_` prefix, per the v4 "underscore-prefix = sub-tree" convention used by `_oideachais_dagster_defs/`, `_oideachais_dlt_utils/`, etc.). The pyproject is a **lie** — no Python code can resolve `import dlt_sources` today.

```bash
$ cd cianfhoghlaim && uv run --no-sync python -c "import dlt_sources"
ModuleNotFoundError: No module named 'dlt_sources'
```

This means `source_factory.from_yaml(path).source("ie.education.leaving_cert")` would crash on first call. The factory itself has been "shipped" but has never been successfully invoked end-to-end against a real source — the only thing keeping the codebase green is that the factory is **opt-in** ("`factory.dagster_asset('ie.medicine.hse')`" — explicit caller, per `source_factory.py:42-44`).

### 2.4 Summary of the two drifts

| Layer | Claimed | Actual | Status |
|:--|:--|:--|:--|
| **Disk path** (spec) | `cianfhoghlaim/dlt_sources/` (28 files) | `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 files) | drift, 7× undercount |
| **Pre-v4 spec** | `sruth/oideachais/dlt_sources/` | `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` | drift, 12 live specs + 8 active changes |
| **Python import** | `dlt_sources.X` (per pyproject packages) | `_oideachais_dlt_sources.X` (per disk) | broken, 3 call sites will ModuleNotFoundError |
| **Tests** | `tests/_oideachais/dlt_sources/` | `tests/_oideachais/dlt_sources/` | aligned ✓ (only the legacy name, kept as a fixture dir) |

---

## 3. Step 1 — Audit consumers (~2 hours)

### 3.1 What we searched

| Tool | Query | Result |
|:--|:--|:--|
| `bun run ccc:search "dlt_sources"` | semantic | 7 hits (top: `_oideachais_dlt_sources/README.md`, archive specs) |
| `grep -rln "dlt_sources" openspec/` | regex | **153 files** (12 live specs + 8 active changes + 133 archive entries) |
| `grep -rln "dlt_sources" cianfhoghlaim/` | regex | **253 files** (code + docs + ruff cache; ~200 real) |
| `grep -rln "dlt_sources" .agents/ AGENTS.md infrastructure/ mise.toml` | regex | **24 files** (9 in `.agents/skills/dlt/`, 6 in `.agents/skills_backup/`, plus `change-detection`, `baml`, `INDEXING_AND_COGNITION`, `n8n workflow`, `QUADRANT-TO-STACK-MAP.md`, `data_platform_graph.py`, root `AGENTS.md`) |
| `grep -rln "from dlt_sources\|import dlt_sources" cianfhoghlaim/` | regex | 3 live import sites (`source_factory.py:252,299`, `duchas_images.py:19`) + 1 reference in REFACTORING.md |

### 3.2 Consumer inventory (8 categories)

| # | Category | Files | Drift | Action |
|:-:|:--|:-:|:--|:--|
| 1 | Live `openspec/specs/*/spec.md` | 12 | pre-v4 | sed |
| 2 | Active `openspec/changes/*/proposal.md` | 8 | pre-v4 | sed |
| 3 | Archived `openspec/changes/archive/*` | 133 | pre-v4 | **LEAVE** (history) |
| 4 | dlt source files in `_oideachais_dlt_sources/` | 190 | none (the real ones) | rename |
| 5 | Other `cianfhoghlaim/**` code + docs | ~63 | mix: 3 broken imports + 60 docstrings | sed |
| 6 | `.agents/skills/**` SKILL.md + references | 9 | pre-v4 | sed |
| 7 | `.agents/skills_backup/**` (deprecated) | 6 | pre-v4 | **LEAVE** |
| 8 | Root config + infrastructure scripts | 4 | pre-v4 | sed |
| 9 | `_oideachais_pyproject.toml` | 1 | `packages = ["dlt_sources"]` (claim, not reality) | becomes true after rename |
| 10 | `tests/_oideachais/dlt_sources/` (fixture) | 1 | legacy name, intentional | keep |

**Total live edits: ~97 files** (excludes 190 dlt sources + 139 archive/backup).

### 3.3 Pre-flight: 3 broken imports (will ModuleNotFoundError today)

```python
# 1. cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py:252
from dlt_sources.common.firecrawl_source import create_firecrawl_source
# 2. source_factory.py:299
from dlt_sources.ie.education.leaving_cert import leaving_cert_source
# 3. cianfhoghlaim/core/curriculum/celtic/duchas_images.py:19
from dlt_sources.duchas_images import duchas_images_source  # WRONG sub-path too (v3→v4)
```

Import #3 is a separate v3→v4 lateralisation sub-drift: `dlt_sources/duchas_images.py` is now `dlt_sources/ie/culture/duchas_images.py` (per Agent 01 §2). All three become importable after the rename; #3 also needs a 1-line sub-path fix.

---

## 4. Step 2 — Decision matrix: rename the on-disk dir vs. fix 97 docs

Two viable options. The decision criterion: **which one has fewer run-time blast-radius surprises, and which one leaves the codebase closer to the v4 conventions already established for sibling packages?**

| Option | What it does | Pro | Con | Run-time risk |
|:--|:--|:--|:--|:-:|
| **A. Rename disk to `dlt_sources/`** | `git mv _oideachais_dlt_sources/ dlt_sources/`, drop the `_oideachais_` prefix | 1. Matches the 3 broken imports verbatim (zero edit to `source_factory.py` / `duchas_images.py`)<br>2. Matches the `packages = ["dlt_sources"]` claim in the pyproject (fixes the lie)<br>3. Matches the human convention "drop the v4 prefix once stable" (cf. `baml_src/`, `dagster_defs/` already dropped their prefix in `_oideachais_*` siblings like `_oideachais_dagster_defs/` → would be `dagster_defs/` once stable)<br>4. Backward-compat with the test fixture dir at `tests/_oideachais/dlt_sources/`<br>5. 190 `.py` files move atomically in one `git mv` | 1. The `_oideachais_dagster_defs/`, `_oideachais_dlt_utils/`, `_oideachais_pyproject.toml`, etc. siblings keep their prefix; consistency arguable both ways | **LOW** |
| **B. Keep `_oideachais_dlt_sources/` and add a top-level `dlt_sources/` shim** | Add `cianfhoghlaim/dlt_sources/__init__.py` that does `from _oideachais_dlt_sources import *` | 1. Preserves the v4 underscore-prefix convention literally | 1. Adds a re-export shim that's a new drift surface<br>2. The 3 broken imports still work but now the shim is a single point of failure<br>3. Test fixture `tests/_oideachais/dlt_sources/` would collide with the new shim (currently a sibling test dir; would need renaming)<br>4. Doesn't fix the spec/import-path divergence for any tool that lists packages by directory walk | **MEDIUM** |
| C. Fix all 97 doc/spec files to use the underscore-prefixed path | Sed-rewrite the spec + skill + changelog files | 1. No on-disk rename | 1. **Still leaves `import dlt_sources` broken** — the runtime still fails<br>2. Requires updating 97 files instead of 1 directory move + ~5 import lines<br>3. Most "fixes" are still wrong because the 3 broken imports (which use `dlt_sources.X` verbatim) need to be re-coded to `_oideachais_dlt_sources.X` (a much uglier change)<br>4. Doesn't fix the pyproject lie | **HIGH** |

### 4.1 Recommendation: **Option A** (rename disk to `dlt_sources/`)

**Why Option A wins:**

1. **It's a single atomic `git mv`.** The on-disk rename is one operation; the path-coherence across 190 source files is preserved because they're all siblings under the same parent.
2. **It makes the 3 broken imports correct as written.** The 3 `from dlt_sources.X` imports work without any code change (after the rename + pyproject trim).
3. **It matches the pyproject's claimed `packages = ["dlt_sources"]` line.** We don't have to edit that line; the line becomes true.
4. **It is consistent with the v4 sibling prefix rule.** Looking at `cianfhoghlaim/`:
   - `_oideachais_dagster_defs/` — still prefixed (still being migrated)
   - `_oideachais_dlt_utils/` — still prefixed (still being migrated)
   - `_oideachais_pyproject.toml` — still prefixed (used during multi-package migration)
   - **`_oideachais_dlt_sources/` is the most-mature of the 4** (190 source files, 12 nations, full test coverage per `tests/_oideachais/dlt_sources/`) → it's the first to be ready for the prefix drop
5. **It eliminates the test fixture dir collision** (the new top-level `dlt_sources/` and the test fixture `tests/_oideachais/dlt_sources/` are in different trees, no conflict).

**Option B (shim) and Option C (rewrite 97 docs) both have higher run-time risk and higher long-term maintenance burden.**

### 4.2 What we leave alone (deliberately)

- **133 archived `openspec/changes/archive/*/proposal.md`** — these are historical record (per `openspec/AGENTS.md` "never modify the 3 research files there; they're point-in-time artifacts"). The post-v4 rename does not retroactively rewrite history; the archive represents the state of the world at the time of each change. We add a one-line "see also" note in the archive README (if one exists) and move on.
- **6 `.agents/skills_backup/*/SKILL.md`** — deprecated skills snapshot, scheduled for deletion (per `mise run lint:skills` warning if they ever re-lint). Leave as-is.
- **`cianfhoghlaim/docs/legacy/crypteolas/dlt_sources/`** — legacy code, `docs/legacy/` is the post-v4 holding pen for things to delete or migrate later. Leave.
- **`cianfhoghlaim/tests/_oideachais/dlt_sources/`** — test fixture dir at a deliberately legacy path (per `REFACTORING.md:180` "8/8 package-level re-exports work"). Keep the name (the test fixture mirrors the legacy `sruth/oideachais/dlt_sources/` layout intentionally for backward-compat regression).

---

## 5. Step 3 — The rename (~4 hours)

### 5.1 The atomic `git mv` (5 minutes)

```bash
cd cianfhoghlaim/pipelines/ingest/
git mv _oideachais_dlt_sources/ dlt_sources/   # preserves git history (rename detection in 1.25+)
ls dlt_sources/ | head -20
# Expect: __init__.py  common/  constants/  cross/  en/  ggy/  ie/  iom/  jey/  law/  leabharlann/  ni/  official_media/  README.md  sct/  site_analysis/  wls/
```

### 5.2 The pyproject becomes truth (5 minutes)

```bash
cd cianfhoghlaim
uv sync
uv run --no-sync python -c "import dlt_sources; print('OK', dlt_sources.__file__)"
# Expect: OK .../dlt_sources/__init__.py
```

The pyproject's `packages = ["dlt_sources", ...]` line was always true in intent; the disk was the lie. No edit needed.

### 5.3 The README rewrite (30 minutes)

The existing `_oideachais_dlt_sources/README.md` is 11 lines (a stub). Rewrite to ~50 lines covering: post-v4 canonical home, country-first layout (ie/en/ni/sct/wls/iom/jey/ggy/cross/leabharlann/law/official_media/common/constants/site_analysis), sub-package re-export pattern, and v3→v4 migration snippet. Full content in §5.3 of the long-form spec (this file is the concise refactor; the long-form is at `openspec/changes/2026-06-29-dlt-path-consolidation/`).

### 5.4 Dagster code-location registration (30 minutes)

```bash
cd cianfhoghlaim/assets/_oideachais_dagster_defs/
uv run --no-sync dg list assets 2>&1 | head -20
# Expect: same asset list as before rename
```

The v4 code-location at `definitions.py:496` (per Agent 02) auto-discovers dlt sources; the rename is transparent as long as no literal `_oideachais_dlt_sources` reference exists (verified: 0 hits per §3.1).

### 5.5 The 3 broken imports (30 minutes)

After the rename, 2 of the 3 broken imports work as-written; #3 also needs a 1-line sub-path fix for a v3→v4 lateralisation sub-drift:

| File | Line | Edit | Why |
|:--|:--|:--|:--|
| `core/dlt/_oideachais_dlt_utils/source_factory.py:252` | none | rename unblocks it | `dlt_sources.common` now exists |
| `core/dlt/_oideachais_dlt_utils/source_factory.py:299` | none | rename unblocks it | `dlt_sources.ie.education` now exists |
| `core/curriculum/celtic/duchas_images.py:19` | `from dlt_sources.duchas_images` → `from dlt_sources.ie.culture.duchas_images` | rename + sub-path fix | The flat `dlt_sources/duchas_images.py` was lateralised to `ie/culture/duchas_images.py` in v4 (Agent 01 §2) |

### 5.6 Smoke test (1 hour)

```bash
cd cianfhoghlaim
uv run --no-sync pytest tests/_oideachais/dlt_sources/ -x          # 8/8 pass
uv run --no-sync pytest tests/_oideachais/ -k "dlt or source_factory or duchas" -x
uv run --no-sync dg list assets --location oideachais 2>&1 | head -30
uv run --no-sync marimo --headless --no-token check cianfhoghlaim/notebooks/dashboards/leabharlann_full_stack.py 2>&1 | head -5
# All 4: expect green
```

---

## 6. Step 4 — Spec + doc updates (~1 hour)

One master sed sweep + one special-case for the v3→v4 lateralisation sub-drift:

```bash
# From repo root

# A. The 12 live openspec specs — 5 sed patterns for the 5 pre-v4 sub-trees
for pattern in \
  's|sruth/oideachais/dlt_sources/uk/\([^/]*\)/|cianfhoghlaim/pipelines/ingest/dlt_sources/\L\1/|g' \
  's|sruth/oideachais/dlt_sources/ireland/|cianfhoghlaim/pipelines/ingest/dlt_sources/ie/|g' \
  's|sruth/oideachais/dlt_sources/domains/|cianfhoghlaim/pipelines/ingest/dlt_sources/|g' \
  's|sruth/oideachais/dlt_sources/\(official_media\|leabharlann\|law\|cross\)/|cianfhoghlaim/pipelines/ingest/dlt_sources/\1/|g'; do
  sed -i "$pattern" openspec/specs/*/spec.md
done

# B. The 8 active openspec changes (skip archive/ — historical record per AGENTS.md)
for f in openspec/changes/*/proposal.md openspec/changes/*/tasks.md; do
  [ -f "$f" ] || continue
  case "$f" in */archive/*) continue;; esac
  sed -i 's|sruth/oideachais/dlt_sources|cianfhoghlaim/pipelines/ingest/dlt_sources|g' "$f"
done

# C. The 9 .agents/skills/* + 4 root config files
for f in .agents/skills/dlt/SKILL.md .agents/skills/dlt/references/*.md \
         .agents/skills/change-detection/SKILL.md .agents/skills/baml/SKILL.md \
         .agents/skills/INDEXING_AND_COGNITION.md \
         AGENTS.md infrastructure/QUADRANT-TO-STACK-MAP.md \
         infrastructure/stacks/n8n/workflows/upstream-blog-monitor.json \
         infrastructure/scripts/cognee-graph-models/data_platform_graph.py; do
  [ -f "$f" ] || continue
  sed -i 's|sruth/oideachais/dlt_sources|cianfhoghlaim/pipelines/ingest/dlt_sources|g' "$f"
done

# D. The ~63 cianfhoghlaim docs (only files that contain the drift pattern)
find cianfhoghlaim -type f \( -name "*.md" -o -name "*.py" \) \
  ! -path "cianfhoghlaim/pipelines/ingest/dlt_sources/*" \
  ! -path "*/.ruff_cache/*" ! -path "*/__pycache__/*" \
  -print0 | xargs -0 grep -lZ "sruth/oideachais/dlt_sources\|_oideachais_dlt_sources" 2>/dev/null \
  | xargs -0 sed -i 's|sruth/oideachais/dlt_sources|cianfhoghlaim/pipelines/ingest/dlt_sources|g'

# E. Special-case: wire-baml-with-known-consumers/tasks.md v3→v4 lateralisation sub-fix
#     `from oideachais.dlt_sources.ireland.aistear` → `from dlt_sources.ie.education.aistear`
#     (only in this one change; ireland/aistear.py is now ie/education/aistear.py)
sed -i 's|oideachais\.dlt_sources\.ireland\.|dlt_sources.ie.education.|g' \
  openspec/changes/wire-baml-with-known-consumers/tasks.md

# Verify
grep -rln "sruth/oideachais/dlt_sources" openspec/specs/ openspec/changes/ cianfhoghlaim/ \
  .agents/skills/ AGENTS.md infrastructure/ --include="*.md" --include="*.py" 2>/dev/null \
  | grep -v "archive/" | grep -v ".ruff_cache"
# Expect: 0 hits
```

---

## 7. Step 5 — CI guard: pre-push hook + pre-commit check (~30 minutes)

### 7.1 The pre-commit hook (`.git/hooks/pre-push` or `.githooks/pre-push`)

Create a new file `infrastructure/git-hooks/dlt-path-drift-check.sh` (registered in `.git/hooks/pre-push` via `core.hooksPath`):

```bash
#!/usr/bin/env bash
# infrastructure/git-hooks/dlt-path-drift-check.sh
# Fail if the diff reintroduces any pre-v4 dlt_sources path.
# Install:  git config core.hooksPath infrastructure/git-hooks
#           chmod +x infrastructure/git-hooks/pre-push

set -euo pipefail

DRIFT_PATTERNS=(
  "sruth/oideachais/dlt_sources"           # pre-v4 path
  "sruth/oideachais/data_platform/dlt_sources"  # pre-v3 path
  "cianfhoghlaim/dlt_sources/__init__\.py"  # the WRONG non-underscore-prefixed in-package (correct is under pipelines/ingest/)
)

# 1. The staged/working-tree changes
for pattern in "${DRIFT_PATTERNS[@]}"; do
  if git diff --cached --name-only --diff-filter=AM | \
       xargs -r grep -lE "$pattern" 2>/dev/null; then
    echo "ERROR: dlt path drift detected: '$pattern'"
    echo "  The canonical path is cianfhoghlaim/pipelines/ingest/dlt_sources/"
    echo "  See openspec/research/2026-06-28-browserbase-program-2/refactors/33-dlt-path-consolidation.md"
    exit 1
  fi
done

# 2. The unstaged changes (in case the developer is mid-edit)
for pattern in "${DRIFT_PATTERNS[@]}"; do
  if git diff --name-only --diff-filter=AM | \
       xargs -r grep -lE "$pattern" 2>/dev/null; then
    echo "ERROR: dlt path drift in unstaged changes: '$pattern'"
    exit 1
  fi
done

# 3. The new files (most common drift source)
for new_file in $(git ls-files --others --exclude-standard); do
  for pattern in "${DRIFT_PATTERNS[@]}"; do
    if [ -f "$new_file" ] && grep -lE "$pattern" "$new_file" >/dev/null 2>&1; then
      echo "ERROR: new file $new_file contains dlt path drift: '$pattern'"
      exit 1
    fi
  done
done

echo "dlt path drift check: PASS"
exit 0
```

### 7.2 The `mise.toml` task registration

Add to `mise.toml`:

```toml
[tasks."lint:dlt-paths"]
description = "Fail if any dlt path drift (sruth/oideachais/dlt_sources, cianfhoghlaim/dlt_sources/__init__.py) is reintroduced"
run = "bash infrastructure/git-hooks/dlt-path-drift-check.sh"
```

Wire into the `mise run turbo dev` chain and the pre-push flow.

### 7.3 The CI check (`.forgejo/workflows/ci.yml` or `.github/workflows/ci.yml`)

```yaml
- name: dlt path drift check
  run: mise run lint:dlt-paths
  shell: bash
```

This runs on every PR and every push to main, so any reintroduced drift gets caught at the CI gate.

### 7.4 The fortnightly re-verification job

Add a scheduled job (cron: every 2 weeks) that runs the same check across the entire repo (not just the diff) — this catches drift introduced by direct pushes that bypass pre-push hooks:

```yaml
# .forgejo/workflows/scheduled-dlt-path-audit.yml
on:
  schedule:
    - cron: '0 6 */14 * *'  # every 14 days at 06:00 UTC
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: mise run lint:dlt-paths
        # NOTE: the hook checks the *diff*; for scheduled we run a repo-wide grep:
        #   ! grep -rE "sruth/oideachais/dlt_sources|sruth/oideachais/data_platform/dlt_sources" \
        #         --include="*.md" --include="*.py" \
        #         openspec/specs/ openspec/changes/ cianfhoghlaim/ .agents/ AGENTS.md infrastructure/ \
        #         | grep -v "openspec/changes/archive/" | grep -v ".ruff_cache" | grep -v "__pycache__"
        # The exit code is 1 if any drift is found.
```

---

## 8. Risks + mitigations

| # | Risk | Mitigation |
|:-:|:--|:--|
| 1 | Circular `__init__.py` chains across the 190 files | Rename is one dir move; intra-tree imports are relative |
| 2 | Absolute `from sruth.oideachais.dlt_sources.X` imports (AGENTS.md §1 anti-pattern) | Verify with `grep -rn "from sruth" cianfhoghlaim/pipelines/ingest/dlt_sources/` (expect 0) |
| 3 | `tests/_oideachais/dlt_sources/` test fixture dir collisions | Different tree (tests/, not pipelines/ingest/); keep the legacy name for regression |
| 4 | 133 archived change proposals still pre-v4 | DELIBERATELY not touched (historical record per AGENTS.md); drift check excludes archive/ |
| 5 | Marimo notebooks with v3→v4 lateralisation sub-drift | §5.5 catches `duchas_images`; audit `grep -rn "dlt_sources" cianfhoghlaim/notebooks/` for others |
| 6 | The `dlt[hub]` extra (P0-3) is a separate refactor | Out of scope for this PR; do not touch `pyproject.toml:39` |
| 7 | `docs/legacy/crypteolas/dlt_sources/` is real legacy code | Per agent-01 §2, it's a v4 holding pen; do not touch |

## 9. The diff budget (single PR)

| Operation | Files | Lines +/- |
|:--|:-:|:-:|
| `git mv _oideachais_dlt_sources/ dlt_sources/` | 190 | rename, not edit |
| Rewrite `dlt_sources/README.md` | 1 | +50 / -11 |
| Fix 3 broken imports (§5.5) | 2 | ±2 |
| Sed 12 live specs | 12 | ±20 |
| Sed 8 active changes | ~16 | ±30 |
| Sed 9 skills | 9 | ±20 |
| Sed 4 root configs | 4 | ±5 |
| Sed ~63 cianfhoghlaim docs | 63 | ±100 |
| Pre-push hook | 1 | +50 |
| `mise.toml` task | 1 | +2 |
| CI workflow | 1 | +15 |
| Scheduled audit | 1 | +20 |
| **TOTAL** | **~309** | **+312 / -188** |

Effort: **S** (1 day). Risk: **low**. Single PR.

---

## 11. Summary (1 paragraph)

The dlt path drift is a **2-layer problem**: (a) 12 live `openspec/specs/*/spec.md` files and 8 active `openspec/changes/*/proposal.md` files still reference the pre-v4 path `sruth/oideachais/dlt_sources/` (and one uses a `from oideachais.dlt_sources.X import Y` verification step that will never pass), and (b) — more critically — the Python import is also broken: `cianfhoghlaim/_oideachais_pyproject.toml:39` declares `packages = ["dlt_sources", ...]` but the on-disk directory was renamed to `_oideachais_dlt_sources/` during v4 consolidation, so `import dlt_sources` raises `ModuleNotFoundError` today and 3 call sites (`source_factory.py:252,299` + `duchas_images.py:19`) are dead code until the path is fixed. The safe, single-PR fix is a `git mv cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ cianfhoghlaim/pipelines/ingest/dlt_sources/` (preserves git history, makes the pyproject truth-true, makes the 3 broken imports work without code change), followed by 5 sed-rewrite passes over the ~97 spec/skill/doc files that need to drop the `sruth/oideachais/` prefix, a 1-line fix to `duchas_images.py:19` for the v3→v4 lateralisation sub-drift (`dlt_sources/duchas_images` → `dlt_sources/ie/culture/duchas_images`), and a pre-push hook (`infrastructure/git-hooks/dlt-path-drift-check.sh` registered via `mise run lint:dlt-paths` and CI cron) that blocks any future commit reintroducing `sruth/oideachais/dlt_sources/` or any new top-level `cianfhoghlaim/dlt_sources/__init__.py` not under `pipelines/ingest/`. Total: ~7 hours, 1 atomic `git mv`, 4 sed sweeps, 1 hook, 1 CI job, 1 scheduled audit. Single PR, effort **S**, risk **low**.
