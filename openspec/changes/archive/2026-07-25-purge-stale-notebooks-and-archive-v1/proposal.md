# 2026-07-25-purge-stale-notebooks-and-archive-v1

## Why

After Change 4 flattened + merged the LC notebook surface, two stale
subtrees are now redundant:

- **23-file `notebooks/leaving_cert/03_leaving_cert/` subtree** (3,749 LOC):
  files 01–11 are the original 2026-era analysis notebooks superseded by
  the 6 per-subject files (now merged into `40_leaving_cert_subject_panel.py`);
  files 12–17 are PDF tooling now folded into `10_biep_pipeline_lakehouse.py`;
  files 18–23 are 2026-07-13 BIEP v1 stubs now subsumed by the new
  grouped panel.

- **26-file `notebooks/legacy/corpora/` subtree** (~3,800 LOC):
  medicine/law/culture/medical/other/politics/technology/author_archive
  corpora — all folded into `marimo_dashboards/01_leabharlann_corpus_overview.py`
  (now `12_corpus_overview.py` after Change 4 flatten).

This change is the **final cleanup** + archives all 5 openspec changes
from this refactor batch (per the canonical `openspec/AGENTS.md` workflow:
"Archive after deployment").

## What changes

### 1. Delete the 23-file stale LC subtree

DELETE the entire `notebooks/leaving_cert/03_leaving_cert/` directory:
- 01_chemistry_analysis.py … 11_*.py (11 analysis notebooks, ~2,055 LOC)
- 12_*.py … 17_*.py (6 PDF processing stubs, ~990 LOC)
- 18_chemistry_biep_v1.py … 23_mathematics_biep_v1.py (6 BIEP v1 stubs, ~704 LOC)
- (Total: 23 files, ~3,749 LOC)

### 2. Delete the 26-file `legacy/corpora/` subtree

DELETE the entire `notebooks/legacy/` directory:
- `corpora/medicine/` (3 files)
- `corpora/law/` (5 files)
- `corpora/culture/` (1 file)
- `corpora/medical/` (1 file)
- `corpora/other/` (1 file)
- `corpora/politics/` (1 file)
- `corpora/technology/` (1 file)
- `corpora/author_archive/` (1 file)
- `corpora/site_analysis_dashboard.py` (1 file)
- `corpora/subject_full_pipeline_runner.py` (1 file)
- `leaving_cert_teacher_view/` (6 files)
- (Total: ~26 files, ~3,800 LOC)

### 3. Reduce `notebooks/legacy/` to a single README

CREATE `notebooks/legacy/README.md` (single page) with:
- A redirect to `notebooks/12_corpus_overview.py` (post-Change 4 name)
- A git history note for the deleted corpora

### 4. Archive all 5 openspec changes

```bash
openspec archive 2026-07-25-nb-utils-ibis-first-v1 --yes
openspec archive 2026-07-25-cocoindex-per-subject-dedup-v1 --yes
openspec archive 2026-07-25-baml-archive-orphaned-and-superseded-v1 --yes
openspec archive 2026-07-25-flatten-notebooks-v1 --yes
openspec archive 2026-07-25-purge-stale-notebooks-and-archive-v1 --yes
```

### 5. Spec delta

`openspec/specs/oideachais-marimo-dashboards/spec.md` — add 2 `## REMOVED Requirements`
entries (23-file LC subtree + 26-file legacy corpus subtree).

## Dependencies

```yaml
Blocked by: 2026-07-25-nb-utils-ibis-first-v1
            2026-07-25-cocoindex-per-subject-dedup-v1
            2026-07-25-baml-archive-orphaned-and-superseded-v1
            2026-07-25-flatten-notebooks-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-25-purge-stale-notebooks-and-archive-v1 --strict` passes
- 23-file `03_leaving_cert/` subtree deleted
- 26-file `legacy/` subtree deleted
- `notebooks/legacy/README.md` (single page redirect) created
- 5 openspec changes archived
- The BIEP v2 stack from `openspec/biep-v2-stack` is still merged
- The full BIEP v1 + JC + England pipeline still passes regression
- `mise run lint:skills` — must remain 53/53
- Push target: `origin/main`

## Cross-references

- [`oideachais-marimo-dashboards`](../../specs/oideachais-marimo-dashboards/spec.md) —
  the parent marimo dashboard spec that gets 2 new `## REMOVED Requirements`
- `openspec/changes/2026-07-25-flatten-notebooks-v1/` — the prerequisite
  (the 23 stale files must be flat-renamed before they can be deleted)
- `.agents/skills/marimo/SKILL.md` — the marimo conventions