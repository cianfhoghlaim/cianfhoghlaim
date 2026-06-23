# Hosting LanceDB on Cloudflare R2 (Docker Compose)

The KCG production target for LanceDB is **Cloudflare R2** (S3-compatible
object storage). The recommended pattern is an **rclone sidecar
container** that mounts R2 as a FUSE filesystem, with the
LanceDB-using service sharing the mount.

## Why rclone (not native S3)?

- **Zero egress** — R2 doesn't charge for egress, but native S3
  mounting (s3fs, goofys) has performance issues
- **Atomic writes** — rclone's `vfs-cache-mode full` provides
  local-cache atomic writes, which LanceDB needs for MVCC
- **Cross-cloud portability** — same Compose file works for R2,
  GCS, S3, Azure Blob, Backblaze B2

## Docker Compose

```yaml
version: "3.9"
services:
  r2-sidecar:
    image: rclone/rclone:latest
    restart: unless-stopped
    command: |
      rclone mount r2:lance /data/lance
        --vfs-cache-mode full
        --vfs-cache-max-age 168h
        --vfs-cache-poll-interval 60s
        --vfs-write-back 5s
        --allow-other
        --dir-cache-time 5m
        --poll-interval 10s
        --umask 000
        --config /config/rclone.conf
    volumes:
      - ./rclone.conf:/config/rclone.conf:ro
      - lance-data:/data/lance:shared
    devices:
      - /dev/fuse
    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined

  lancedb-app:
    image: your-app:latest
    restart: unless-stopped
    depends_on:
      - r2-sidecar
    volumes:
      - lance-data:/data/lance:shared
    environment:
      LANCEDB_URI: /data/lance
      RUST_LOG: info

volumes:
  lance-data:
    driver: local
```

## rclone.conf (template)

```ini
[r2]
type = s3
provider = Cloudflare
access_key_id = ${R2_ACCESS_KEY_ID}
secret_access_key = ${R2_SECRET_ACCESS_KEY}
endpoint = https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com
no_check_bucket = true
```

## Performance tuning

- **`vfs-cache-mode full`** — required for atomic writes
- **`vfs-write-back 5s`** — batches writes for 5s before flushing to R2
- **`dir-cache-time 5m`** — caches directory listings for 5 minutes
- **`poll-interval 10s`** — polls R2 for changes every 10s

## When NOT to use rclone

- **Read-only workloads** — use the native `s3://` URI directly
- **High-throughput, low-latency writes** — rclone's FUSE layer adds
  ~2-5ms latency per write. For write-heavy workloads, use LanceDB
  Cloud directly.
- **Multi-region** — rclone mounts a single bucket. For multi-region,
  use LanceDB Cloud.

## KCG production usage

The KCG stack uses this pattern in
`infrastructure/stacks/lancedb-r2/` (a 6-file
GOLD_STANDARD stack). The full Compose file is there; the snippet
above is a minimal version for reference.

## Reference

- The full `docs/lance/lancedb.compose.yaml` (73 lines, with the
  rclone sidecar + healthchecks + named network + secrets) was in
  the docs subdirectory (deleted with the `sync-skills-from-docs`
  change).
- rclone docs: <https://rclone.org/s3/#cloudflare-workers-kv>
- Cloudflare R2 docs: <https://developers.cloudflare.com/r2/>
