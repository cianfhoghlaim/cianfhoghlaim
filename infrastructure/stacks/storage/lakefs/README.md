# LakeFS — Git-like Version Control for Data Lakes

## Overview

LakeFS provides Git-style branching, committing, and merging for data stored in S3-compatible object storage. It wraps an S3 bucket in a versioning layer, allowing you to create isolated branches of your data, run pipelines against branch snapshots, and merge only validated results back to production.

## Why This Matters for Kings' College Galway

Curriculum data is versioned by nature — exam syllabi change every 3-5 years, and marking schemes are updated annually. LakeFS lets us maintain a `production` branch with the current curriculum, a `2023-reform` branch with the pre-reform data, and per-experiment branches for testing new OCR or extraction pipelines — all against the same underlying Garage S3 storage. When a new pipeline produces better extraction results, we merge the branch atomically. This Git-like workflow brings software engineering rigour to curriculum data management.

## Key Features

- **Branching and merging** — Create isolated data branches, run experiments, merge validated results
- **Atomic commits** — Every data write is a commit; rollback is instant
- **Cross-collection transactions** — Commit changes across multiple tables atomically
- **Hooks and CI/CD** — Run validation checks on branch merge via webhooks
- **ACL and RBAC** — Fine-grained access control per repository and branch

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/storage/lakefs
docker compose up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci. Uses co-located MinIO (dev) or Garage S3 (prod) as the backing store. Locket resolves `LAKEFS_DB_PASSWORD` and S3 credentials from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LAKEFS_DB_USERNAME` | No | PostgreSQL user | `lakefs` |
| `LAKEFS_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `LAKEFS_AUTH_ENCRYPT_SECRET_KEY` | Yes | Encryption key for auth tokens (32-char) | — |
| `MINIO_ROOT_USER` | No | MinIO access key (dev) | `minio` |
| `MINIO_ROOT_PASSWORD` | No | MinIO secret key (dev) | `devpassword` |
| `MINIO_API_PORT` | No | MinIO S3 API port | `9000` |
| `MINIO_CONSOLE_PORT` | No | MinIO web console port | `9001` |
| `LAKEFS_PORT` | No | LakeFS API and UI port | `8000` |

## Access

- **Web UI**: `http://localhost:8000`
- **S3 Gateway**: `http://localhost:8000/s3`
- **Auth**: Email/password admin account (local); Pocket ID SSO (production)

## Upstream

- **Repository**: <https://github.com/treeverse/lakeFS>
- **Documentation**: <https://docs.lakefs.io>
- **Latest**: v1.x series — active development with focus on enterprise RBAC, performance, and S3 gateway improvements

## Screenshot

LakeFS provides a web UI at port 8000 showing repository browser, branch comparison, commit history, and diff views. The UI resembles a Git hosting platform (GitHub/GitLab) but for data: you can browse files on different branches, view commit logs, and create merge requests for data changes.
