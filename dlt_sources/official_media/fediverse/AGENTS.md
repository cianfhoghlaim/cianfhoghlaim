# `dlt_sources/official_media/fediverse/` — Mastodon + Bluesky feeds

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1).

This sub-tree holds the fediverse / open social web feeds:

| Module | Protocol |
|:--|:--|
| `__init__.py` (was `fediverse.py`) | Mastodon + Bluesky resolver library |

The British Crown jurisdictional feeds (`sct/`, `wls/`) live under
[`../british_crown/`](../british_crown/AGENTS.md) instead.

The Channel Islands feeds (`ggy/`, `iom/`, `jsy/`) live under
[`../channel_islands/`](../channel_islands/AGENTS.md) instead.

The British Crown companies feeds (`companies_house/`) live under
[`../companies/`](../companies/AGENTS.md) instead.

## Public surface

```python
from dlt_sources.official_media.fediverse import resolve_mastodon, resolve_bluesky

profile = resolve_mastodon(username="cianfhoghlaim", host="mastodon.social")
```

## Backwards-compat shims

The original `dlt_sources/official_media/fediverse.py` flat file
continues to work via a re-export shim at the legacy location.
