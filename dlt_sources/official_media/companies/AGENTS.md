# `dlt_sources/official_media/companies/` — Companies House + CRO feeds

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1).

This sub-tree holds the UK + Ireland companies registry feeds:

| Sub-dir | Registry |
|:--|:--|
| `companies_house/` | UK Companies House + Crown Dependencies company registry |

The British Crown jurisdictional feeds (`sct/`, `wls/`) live under
[`../british_crown/`](../british_crown/AGENTS.md) instead.

The Channel Islands feeds (`ggy/`, `iom/`, `jsy/`) live under
[`../channel_islands/`](../channel_islands/AGENTS.md) instead.

The fediverse / Mastodon / Bluesky feeds live under
[`../fediverse/`](../fediverse/AGENTS.md) instead.

## Public surface

```python
from dlt_sources.official_media.companies.companies_house import companies_house_source
```

The `crown_filter.py` helper inside `companies_house/` filters
out the Channel Islands + Isle of Man companies from the main UK
Companies House feed, since those are tracked separately under
`../channel_islands/`.

## Backwards-compat shims

The original `dlt_sources/official_media/companies_house/` flat path
continues to work via a re-export shim at the legacy location.
