# `bonneagar/docs/`

Architecture and reproduction guides for the self-hosted platform. These are
the "how does this actually work / how would someone else build it" documents;
operational runbooks live in [`../deploy-runbooks/`](../deploy-runbooks/).

| Document | Read it when |
|---|---|
| [private-resources-architecture.md](private-resources-architecture.md) | You want to understand how a service on a laptop is reachable at a public hostname, over TLS, with no inbound ports — and why the "connect via the client" page is correct behaviour rather than a bug. |
| [deploy-private-resource-from-scratch.md](deploy-private-resource-from-scratch.md) | You are building one, on your own VPS / hardware / domain. Includes the verification ladder and a troubleshooting table. |
| [ai-provider-tiers.md](ai-provider-tiers.md) | You are wiring up model serving and need to know what is worth running on your hardware, and how the fallback chain degrades. |

Related, elsewhere in `bonneagar/`:

- [`../PANGOLIN-SETUP.md`](../PANGOLIN-SETUP.md) — control-plane bring-up and manual steps
- [`../SECRETS-MANAGEMENT.md`](../SECRETS-MANAGEMENT.md) — secret hydration, incl. Infisical / 1Password / plain `.env` parity
- [`../DEPLOYMENT-STRATEGY.md`](../DEPLOYMENT-STRATEGY.md) — host topology and the four deploy surfaces
- [`../pangolin/private-resources.blueprint.yaml`](../pangolin/private-resources.blueprint.yaml) — the declarative source of truth for private resources

## A note on trusting these documents

Everything in the private-resource guides was verified against the live
deployment on 2026-08-23, including applying the blueprint and driving a real
Olm client through the tunnel end to end.

Where a claim could not be verified it says so. Where a previously documented
claim turned out to be false — the Postgres/SQLite mismatch, the site naming,
the mock image digest — the document says that too, rather than quietly
correcting it, because the failure modes are instructive and someone
reproducing this will hit the same ones.
