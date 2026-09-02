# `dlt_sources/official_media/british_crown/` — British Crown feeds

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1).

This sub-tree holds the British Crown jurisdiction feeds (the
non-devolved UK nations + crown dependencies):

| Sub-dir | Jurisdiction |
|:--|:--|
| `sct/` | Scotland — Scottish Government open data |
| `wls/` | Wales — Welsh Government open data |

The Channel Islands feeds (`ggy/`, `iom/`, `jsy/`) live under
[`../channel_islands/`](../channel_islands/AGENTS.md) instead.

The British Crown companies feeds (`companies_house/`) live under
[`../companies/`](../companies/AGENTS.md) instead.

The fediverse / Mastodon / Bluesky feeds live under
[`../fediverse/`](../fediverse/AGENTS.md) instead.

## Public surface

```python
from dlt_sources.official_media.british_crown.sct import scotland_open_data_source
from dlt_sources.official_media.british_crown.wls import wales_open_data_source
```

## Backwards-compat shims

The original `dlt_sources/official_media/sct/` + `wls/` flat paths
continue to work via re-export shims at the legacy locations.
