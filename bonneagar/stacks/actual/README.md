# Actual Budget — Self-Hosted Personal Finance Manager

## Overview

Actual Budget is an open-source, self-hosted personal finance and budgeting application based on double-entry bookkeeping principles. It provides envelope budgeting, transaction tracking, bank sync (via third-party connectors), and multi-device access. Originally a commercial product, it was acquired and open-sourced in 2021.

## Why This Matters for Kings' College Galway

Managing infrastructure costs across three cloud providers (OCI, Hetzner, Cloudflare) and multiple API subscriptions (DeepSeek, Infisical, Browserbase, Firecrawl, HuggingFace) requires careful budget tracking. Actual provides envelope-based budgeting where each infrastructure cost category gets a monthly allocation, and transactions are categorised automatically. The double-entry system ensures accuracy — every API charge, every cloud compute hour, and every storage gigabyte is tracked and reconciled against the budget. For a student/researcher-run project with a $25/month AI budget, this financial discipline keeps costs predictable and prevents surprise bills.

## Key Features

- **Envelope budgeting** — Allocate funds to categories; track spending against limits
- **Double-entry accounting** — Every transaction is balanced; no lost money
- **Bank sync** — Import transactions via SimpleFIN/GoCardless (optional)
- **Multi-device** — Sync budgets across desktop and mobile
- **Reports** — Spending trends, category breakdowns, net worth tracking

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/actual
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Stores budget data in a local SQLite database within the Docker volume.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `HTTPS` | No | Enable HTTPS | — |
| `ACTUAL_PORT` | No | Web UI port | `3001` |

## Access

- **Web UI**: `https://actual.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: Local password + optional Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/actualbudget/actual>
- **Documentation**: <https://actualbudget.org/docs>
- **Latest**: v24.x (2025) — bank sync improvements, mobile app enhancements, report builder, goal tracking

## Screenshot

Actual Budget's web UI shows a clean budgeting dashboard: a sidebar with budget categories and their balances, a transaction register with search and filter, and a budget view showing allocated vs spent per category with colour-coded progress bars. Reports show spending trends, income vs expenses, and net worth over time.
