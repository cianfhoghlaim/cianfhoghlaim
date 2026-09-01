# `dlt_sources/official_media/channel_islands/` — Channel Islands feeds

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1).

This sub-tree holds the Channel Islands jurisdiction feeds (the 3
British Crown Dependencies that are NOT part of the UK):

| Sub-dir | Jurisdiction |
|:--|:--|
| `ggy/` | Guernsey — Government of Guernsey open data |
| `iom/` | Isle of Man — Tynwald / Isle of Man Government open data |
| `jsy/` | Jersey — Government of Jersey open data |

The British Crown feeds (`sct/`, `wls/`) live under
[`../british_crown/`](../british_crown/AGENTS.md) instead.

The British Crown companies feeds (`companies_house/`) live under
[`../companies/`](../companies/AGENTS.md) instead.

The fediverse / Mastodon / Bluesky feeds live under
[`../fediverse/`](../fediverse/AGENTS.md) instead.

## Public surface

```python
from dlt_sources.official_media.channel_islands.ggy import guernsey_open_data_source
from dlt_sources.official_media.channel_islands.iom import isle_of_man_open_data_source
from dlt_sources.official_media.channel_islands.jsy import jersey_open_data_source
```

## Backwards-compat shims

The original `dlt_sources/official_media/{ggy,iom,jsy}/` flat paths
continue to work via re-export shims at the legacy locations.
