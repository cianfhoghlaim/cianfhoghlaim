---
name: kubernetes
description: Kubernetes deployment for the Cianfhoghlaim platform — Talos OS on Hetzner + OCI, Pulumi + OpenTofu IaC, Ansible Periphery bootstrap, bpbradley.komodo role. KCG is Komodo-first; this skill is for scaling beyond Compose. Use when adding a new K8s node, deploying to OCI/Hetzner, or wiring Pulumi stacks.
---

# Kubernetes — KCG Reference

## When to use this skill

Use when you need to:

- "Add a new K8s node to the Hetzner cluster"
- "Deploy a service to OCI via Pulumi"
- "Bootstrap a new Periphery node via Ansible"
- "Wire a bpbradley.komodo role to a new K8s stack"
- "Migrate a Compose stack to K8s (scale-out trigger)"

## Overview

KCG is **Komodo-first**. Most services run on Docker Compose
via Komodo. Kubernetes is the **scale-out trigger** — when a
service outgrows Compose (multi-region, multi-master, > 50
pods, etc.), it migrates to K8s.

| Aspect | Compose (default) | K8s (scale-out) |
|:--|:--|:--|
| Use case | Single-host, dev, small prod | Multi-host, multi-region, large prod |
| IaC | Komodo + Compose | Pulumi + OpenTofu |
| Bootstrap | `mise run stack:up` | `ansible-playbook setup-server.yml` |
| Service discovery | Traefik (via Pangolin) | Cilium (via Pangolin) |
| Stateful | Local volumes | Rook-Ceph / Longhorn |
| Production use | KCG engineering Dagster, leabharlann | Cognee, FalkorDB cluster |

## 3 Talos node options

| Option | Node count | Use case | Cost (EUR/mo) |
|:--|--:|:--|--:|
| **Business** | 3 control plane + 3 worker | Production Cognee cluster | ~200 |
| **Indie** | 1 control plane + 2 worker | Dev / staging | ~80 |
| **Nuclear** | 1 single-node | Local-only CI | ~30 |

## OpenTofu + Hetzner pattern

```hcl
# infrastructure/k8s/hetzner/main.tf
resource "hcloud_server" "control_plane" {
  count       = 3
  name        = "kcg-cp-${count.index}"
  image       = "talos-v1.7.0"
  server_type = "cx31"
  location    = "fsn1"
}
```

```bash
# Bootstrap
tofu init && tofu apply
talosctl apply-config --file control-plane.yaml --nodes 10.0.1.1,10.0.1.2,10.0.1.3
talosctl bootstrap --nodes 10.0.1.1
```

## Pulumi multi-cloud (OCI + Hetzner + Cloudflare)

```python
# infrastructure/k8s/oci/__main__.py
import pulumi
import pulumi_oci as oci

cluster = oci.containerengine.Cluster(
    "kcg-cognee",
    name="kcg-cognee",
    type="ENHANCED_CLUSTER",
    kubernetes_version="v1.31",
    vcn_id=vcn.id,
)
pulumi.export("kubeconfig", cluster.kubeconfig)
```

## Ansible Periphery bootstrap

```yaml
# infrastructure/ansible/playbooks/setup-server.yml
- name: Bootstrap KCG Periphery
  hosts: all
  become: true
  tasks:
    - name: Install Talos
      ansible.builtin.shell: |
        curl -sL https://talos.dev/install | sh
    - name: Install Komodo
      ansible.builtin.shell: |
        curl -sL https://komo.do/install | sh
    - name: Install Infisical agent
      ansible.builtin.shell: |
        curl -sL https://infisical.com/install | sh
    - name: Wire Pangolin tunnel
      ansible.builtin.shell: |
        pangolin-cli tunnel-up
```

## bpbradley.komodo role

The KCG Komodo deployment uses a custom role
(`bpbradley.komodo`) that adds KCG-specific actions:

- `stack:up <name>` — bring up a Compose stack
- `stack:down <name>` — bring down a Compose stack
- `stack:rebuild <name>` — rebuild and restart
- `stack:logs <name> [service]` — tail logs
- `stack:exec <name> <service> <cmd>` — exec into a service
- `mise:install` — hydrate the polyglot toolchain
- `infisical:export <name>` — export secrets to env

## Separation of concerns

| Tool | Owns |
|:--|:--|
| Pulumi / OpenTofu | Cloud resources (VMs, networks, storage) |
| Ansible | Server bootstrap (Talos, Komodo, Infisical) |
| Komodo | Service deployment (Compose stacks, K8s workloads) |
| Pangolin | Networking (TLS, routing, OIDC) |
| Infisical | Secrets |
| Dagster | Orchestration |

**Never mix these.** Pulumi creates the server; Ansible
configures it; Komodo deploys services; Pangolin routes traffic;
Infisical hydrates secrets; Dagster schedules work.

## When NOT to use this skill

- The service fits on a single Compose stack
- The dev loop is faster with Compose
- You don't have a Hetzner / OCI account

Compose is the right default. K8s is the scale-out trigger.

## Related skills

- `.agents/skills/stack-ops/SKILL.md` — the canonical 6-file
  GOLD_STANDARD stack pattern (Compose + Komodo)
- `.agents/skills/komodo/SKILL.md` — Komodo GitOps
- `.agents/skills/pangolin/SKILL.md` — Pangolin networking
- `.agents/skills/monorepo/SKILL.md` — bun + uv + turbo
- `.agents/skills/pulumi/SKILL.md` — Pulumi multi-cloud
- `.agents/skills/agent-observability/SKILL.md` — Logfire +
  Langfuse + MLflow + RAGAS for K8s workloads

## Resources

- Talos OS: <https://www.talos.dev/>
- Pulumi: <https://www.pulumi.com/>
- Hetzner Cloud: <https://www.hetzner.com/cloud>
- Oracle Cloud Infrastructure: <https://www.oracle.com/cloud/>
- Komodo: <https://komo.do/>
