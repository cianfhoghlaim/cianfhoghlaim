#!/usr/bin/env bash
# sync/tg4_all.sh — chain the TG4 player + Foghlaim DLT ingestions +
# refresh the v1 App. Per the 2026-08-25-tg4-foghlaim-corpus-v1 change.
#
# Usage: mise run sync:tg4-all

set -euo pipefail

echo "==> [sync:tg4-all] running TG4 player catalog DLT ingestion"
mise run sync:tg4-player

echo "==> [sync:tg4-all] running Foghlaim lessons DLT ingestion"
mise run sync:tg4-foghlaim

echo "==> [sync:tg4-all] refreshing Tg4FoghlaimEmbedding v1 App"
mise run cocoindex:update -- cianfhoghlaim.cocoindex_flows.media.tg4_foghlaim_embedding:Tg4FoghlaimEmbedding || true

echo "==> [sync:tg4-all] complete"