# DEPRECATED — Migrated to `notebooks/speedrun_mmo.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 8 speedrun MMO sub-notebooks + the shared file
have been consolidated into the single grouped marimo dashboard
[`notebooks/speedrun_mmo.py`](../../speedrun_mmo.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `16_speedrun_mmo_00_celtic_nft.py` | Celtic NFT |
| `16_speedrun_mmo_01_language_staking.py` | Language Staking |
| `16_speedrun_mmo_01_mission_control.py` | Mission Control |
| `16_speedrun_mmo_02_cianfhoghlaim_mmo_progress.py` | MMO Progress |
| `16_speedrun_mmo_02_token_shop.py` | Token Shop |
| `16_speedrun_mmo_03_quest_randomness.py` | Quest Randomness |
| `16_speedrun_mmo_04_item_exchange.py` | Item Exchange |
| `16_speedrun_mmo_05..08_*.py` | (additional Tabs) |
| `16_speedrun_mmo__shared.py` | (shared helpers — now in `_shared/`) |

## How to run

```bash
marimo edit notebooks/speedrun_mmo.py
python notebooks/speedrun_mmo.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.