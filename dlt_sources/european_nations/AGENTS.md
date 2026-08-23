# `dlt_sources/european_nations/`

> `european_nations/`: the 40 European nations (each follows `_shared/nation_source.py` pattern × 5 verticals: education + government + law + medicine + statistics) — 859 .py files, 407 @dlt.source.

## Quick start

- `_shared/nation_source.py` — the canonical base class
- 40 nations × 5 verticals (education + government + law + medicine + statistics) = ~200 DLT sources

## Status

The 40 nations follow the sprawled-but-converged pattern: each nation is a sub-directory with a standardized 5-vertical structure. The `nation_source.py` base class enforces the canonical contract.
