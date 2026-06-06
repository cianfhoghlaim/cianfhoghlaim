---
title: "Kubernetes Deployment — K8s, IaC & Server Provisioning"
domain: architecture
status: stable
description: "Kubernetes deployment patterns including Talos on Hetzner, Pulumi/OpenTofu IaC, Ansible server provisioning, and Komodo Periphery bootstrap"
supersedes:
  - docs/bonneagar/High-Availability Kubernetes on Hetzner with Talos 1.11.md
  - docs/bonneagar/pulumi.md
  - docs/bonneagar/pulumi-infrastructure-as-code.md
  - docs/bonneagar/pulumi_1.md
  - docs/bonneagar/pulumi-typescript-guide-provisioning-cloudflare-d1-r2-1password-integration.md
  - docs/bonneagar/Provision Resources on Hetzner Cloud with Pulumi.md
  - docs/bonneagar/Register a Hetzner Server.md
  - docs/bonneagar/Register a GCP Instance.md
  - docs/bonneagar/Deploying Dagster to Google Cloud Platform _ Dagster Docs.md
  - docs/bonneagar/apple-silicon-deployment.md
  - docs/bonneagar/apple-silicon-deployment_1.md
  - docs/bonneagar/Building preconfigured OS images with HashiCorp Packer.md
entities:
  - Kubernetes
  - TalosLinux
  - Pulumi
  - Ansible
  - HetznerCloud
related_skills:
  - .agents/skills/pulumi/SKILL.md
  - .agents/skills/dagger/SKILL.md
  - .agents/skills/komodo/SKILL.md
ccc_query_hints:
  - "kubernetes deployment on hetzner"
  - "talos linux cluster setup"
  - "pulumi infrastructure as code"
  - "ansible server provisioning"
  - "opentofu infrastructure"
last_reviewed: 2026-06-06
---

# Kubernetes Deployment & Infrastructure as Code

The Cianfhoghlaim platform uses **Komodo + Docker Compose** for day-to-day operations. For scenarios requiring Kubernetes (multi-tenant isolation, auto-scaling, enterprise compliance), the following patterns are documented.

## High-Availability Kubernetes on Hetzner with Talos 1.11

### Option 1: "Business Powerhouse" (3x CX53 Converged)

Best for production apps, Mastodon instances, Odoo ERP, high-traffic WordPress networks.

| Resource | Spec |
|----------|------|
| **Nodes** | 3x CX53 (16 vCPU, 32GB RAM, 320GB NVMe) |
| **Networking** | 1x Load Balancer (LB11) + 1x Failover IP |
| **Storage** | Hetzner Object Storage (S3 Compatible) |

**Monthly Cost:** ~€66.46 (48 vCPUs, 96GB RAM)

### Option 2: "Indie Hacker" (1 CP + 3 Workers)

Best for SPAs, static sites, dev environments, low-traffic APIs.

| Resource | Spec |
|----------|------|
| **Control Plane** | 1x CX23 (2 vCPU, 4GB RAM) |
| **Workers** | 3x CX23 (2 vCPU, 4GB RAM) |

**Monthly Cost:** ~€17.56

### Option 3: "Nuclear Option" (3x Dedicated AX41-NVMe)

Best for video encoding, big data, ML, heavy database loads.

| Resource | Spec |
|----------|------|
| **CPU** | AMD Ryzen 5 3600 (Hexa-Core) |
| **RAM** | 64 GB DDR4 |
| **Disk** | 2x 512 GB NVMe (RAID 1) |

**Monthly Cost:** ~€37.30/node

**Challenge:** Talos doesn't support software RAID booting. Workaround: Flatcar Container Linux or Proxmox VE → Talos VMs.

## Infrastructure as Code

### OpenTofu for Talos Bootstrap

```hcl
# main.tf — Converged CX53
terraform {
  required_providers {
    hcloud = { source = "hetznercloud/hcloud", version = "~> 1.45" }
  }
}

resource "hcloud_network" "talos_net" {
  name     = "talos-net"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_server" "node" {
  count       = 3
  name        = "talos-cx53-${count.index + 1}"
  server_type = "cx53"
  image       = "debian-12"  # Bootstrapping OS
  location    = "nbg1"

  user_data = <<-EOF
    #cloud-config
    runcmd:
      - apt-get update && apt-get install -y zstd
      - wget -O /tmp/talos.raw.zst https://github.com/siderolabs/talos/releases/download/v1.11.5/metal-amd64.raw.zst
      - zstd -d -c /tmp/talos.raw.zst | dd of=/dev/sda && sync
      - reboot
  EOF
}
```

### Cilium + Gateway API

```bash
helm install cilium cilium/cilium --version 1.18.4 \
  --namespace kube-system \
  --set gatewayAPI.enabled=true \
  --set kubeProxyReplacement=true \
  --set hcloud.enabled=true
```

### Storage Strategy

| Type | Technology | Use Case |
|------|-----------|----------|
| **Block Storage** | Hetzner CSI Driver + Cloud Volumes | PostgreSQL, MySQL, PVCs (auto-reattach on node failure) |
| **Object Storage** | Hetzner Object Storage (S3) | Media files, backups, unstructured data (~€5/TB) |

### Disaster Recovery

In a 3-node setup, quorum is maintained (2/3 votes). The Hetzner Load Balancer detects dead nodes and stops sending API traffic. Apps reschedule to surviving nodes automatically.

**Repair via GitOps:**

```bash
# Mark broken server for recreation
tofu taint "hcloud_server.node[1]"

# Apply changes
tofu apply
```

## Pulumi Infrastructure as Code

Pulumi manages infrastructure across three providers:

### OCI (Oracle Cloud)

```typescript
import * as oci from "@pulumi/oci";

export const webServer = new oci.core.Instance("web-server", {
  compartmentId: config.compartmentId,
  shape: "VM.Standard.E2.1.Micro",
  sourceDetails: {
    sourceType: "image",
    sourceId: ubuntuImage.id,
  },
  createVnicDetails: {
    subnetId: subnet.id,
    assignPublicIp: "true",
  },
});

export const bucket = new oci.objectstorage.Bucket("documents", {
  compartmentId: config.compartmentId,
  namespace: namespace.namespace,
  name: "cianfhoghlaim-documents",
  accessType: "NoPublicAccess",
});
```

### Hetzner

```typescript
import * as hcloud from "@pulumi/hcloud";

export const server = new hcloud.Server("main", {
  serverType: "cx21",
  image: "ubuntu-22.04",
  location: "fsn1",
  sshKeys: [sshKey.id],
});
```

### Cloudflare

```typescript
import * as cloudflare from "@pulumi/cloudflare";

const bucket = new cloudflare.R2Bucket("data-bucket", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "my-data-bucket",
});

const database = new cloudflare.D1Database("app-db", {
  accountId: process.env.CLOUDFLARE_ACCOUNT_ID,
  name: "app-database",
});
```

### Pulumi Stacks

| Stack | Provider | Resources |
|-------|----------|-----------|
| `oci-production` | OCI | Compute, VCN, Object Storage |
| `hetzner-production` | Hetzner | Servers, Volumes, Networks |
| `cloudflare-production` | Cloudflare | DNS, Pages, Workers, R2, D1 |

### Secrets in Pulumi

```bash
pulumi config set --secret database_password "..."
```

```typescript
const dbPassword = config.requireSecret("database_password");
```

### Dagger Integration for Pulumi

```typescript
export async function deployPulumi(
  client: Client,
  source: Directory,
  stack: string
): Promise<string> {
  return client
    .container()
    .from("pulumi/pulumi-nodejs:latest")
    .withDirectory("/src", source)
    .withWorkdir(`/src/bonneagar/pulumi/${stack.split("-")[0]}`)
    .withExec(["pulumi", "up", "-s", stack, "--yes"])
    .stdout();
}
```

## Ansible Server Provisioning

### Architecture Role

Ansible acts as the **bridge** between the infrastructure definition (Pulumi) and the application runtime (Komodo):

```
Pulumi (provisions raw VMs)
    ↓
Ansible (configures OS, installs Periphery + Newt)
    ↓
Komodo (deploys Docker Compose stacks)
```

### Komodo Periphery Bootstrap Playbook

```yaml
# playbooks/setup-server.yml
- name: Setup production server
  hosts: production
  become: yes
  tasks:
    - name: Install Docker
      ansible.builtin.apt:
        name: docker.io
        state: present

    - name: Install Komodo Periphery
      community.docker.docker_container:
        name: komodo-periphery
        image: ghcr.io/mbecker20/periphery:latest
        restart_policy: always
        env:
          KOMODO_HOST: "https://komodo.example.com"
          PERIPHERY_PASSKEY: "{{ lookup('community.general.onepassword', 'periphery-key') }}"
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
          - /etc/komodo:/etc/komodo

    - name: Install Pangolin Newt
      community.docker.docker_container:
        name: pangolin-newt
        image: ghcr.io/pangolin/newt:latest
        restart_policy: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
        env:
          PANGOLIN_ENDPOINT: "wss://gerbil.example.com"
          PANGOLIN_ID: "{{ inventory_hostname }}"
```

### Ansible Role (bpbradley.komodo)

```bash
ansible-galaxy role install bpbradley.komodo
```

```yaml
# inventory.yaml
all:
  children:
    komodo_nodes:
      hosts:
        server-a:
          ansible_host: 192.168.1.10
          komodo_server_name: "Production-A"
```

```yaml
# deploy_periphery.yaml
- name: Deploy Komodo Periphery Agents
  hosts: komodo_nodes
  become: true
  roles:
    - role: bpbradley.komodo
      vars:
        komodo_action: "install"
        komodo_version: "2-dev"
```

### Ansible Execution Environment (uv-based)

Instead of slow `pip install`, use `uv` for fast, hermetic Ansible environments:

```bash
uv venv
uv pip install ansible-core requests netaddr
```

### Semaphore UI (Alternative to AWX)

| Feature | Semaphore UI | AWX |
|---------|-------------|-----|
| **Language** | Go (single binary) | Python/Django (microservices) |
| **Minimum RAM** | ~512 MB | ~4 GB |
| **Database** | MySQL, Postgres, BoltDB | Postgres + Redis |
| **GitOps** | Native (webhook/polling) | Native (project sync) |
| **Secret Store** | AES-256 (internal) | Vault integration |

## Separation of Concerns

| Tool | Role | Scope |
|------|------|-------|
| **Pulumi** | Cloud resource creation | VMs, VPCs, Load Balancers, Managed DBs |
| **Ansible** | OS-level bootstrap | Docker install, Periphery agent, SSH hardening |
| **Komodo** | Application deployment | Docker Compose stacks, GitOps, container lifecycle |
| **Pangolin** | Service exposure | WireGuard tunnels, TLS termination, OIDC auth |
