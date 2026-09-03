# Pulumi Infrastructure as Code

Multi-cloud infrastructure provisioning with TypeScript.

## Overview

Pulumi manages infrastructure across:

- **OCI (Oracle Cloud)** - Always-free tier VMs
- **Hetzner** - Cost-effective European servers
- **Cloudflare** - DNS, Pages, Workers

## Location

```
bonneagar/pulumi/
├── oci/                 # Oracle Cloud Infrastructure
│   ├── Pulumi.yaml
│   ├── index.ts
│   └── compute.ts
├── hetzner/             # Hetzner Cloud
│   ├── Pulumi.yaml
│   ├── index.ts
│   └── servers.ts
└── cloudflare/          # Cloudflare resources
    ├── Pulumi.yaml
    ├── index.ts
    └── dns.ts
```

## Stacks

| Stack | Provider | Resources |
|-------|----------|-----------|
| `oci-production` | OCI | Compute, VCN, Object Storage |
| `hetzner-production` | Hetzner | Servers, Volumes, Networks |
| `cloudflare-production` | Cloudflare | DNS, Pages, Workers |

## Usage

### Preview Changes

```bash
cd bonneagar/pulumi/oci
pulumi preview -s production
```

### Deploy

```bash
pulumi up -s production
```

### Destroy

```bash
pulumi destroy -s production
```

## OCI Configuration

### Compute Instances

```typescript
// bonneagar/pulumi/oci/compute.ts
import * as oci from "@pulumi/oci";

export const webServer = new oci.core.Instance("web-server", {
  compartmentId: config.compartmentId,
  shape: "VM.Standard.E2.1.Micro",
  availabilityDomain: ad.name,
  sourceDetails: {
    sourceType: "image",
    sourceId: ubuntuImage.id,
  },
  createVnicDetails: {
    subnetId: subnet.id,
    assignPublicIp: "true",
  },
});
```

### Object Storage

```typescript
export const bucket = new oci.objectstorage.Bucket("documents", {
  compartmentId: config.compartmentId,
  namespace: namespace.namespace,
  name: "cianfhoghlaim-documents",
  accessType: "NoPublicAccess",
});
```

## Hetzner Configuration

```typescript
// bonneagar/pulumi/hetzner/servers.ts
import * as hcloud from "@pulumi/hcloud";

export const server = new hcloud.Server("main", {
  serverType: "cx21",
  image: "ubuntu-22.04",
  location: "fsn1",
  sshKeys: [sshKey.id],
});
```

## Cloudflare Configuration

```typescript
// bonneagar/pulumi/cloudflare/dns.ts
import * as cloudflare from "@pulumi/cloudflare";

export const zone = new cloudflare.Zone("main", {
  zone: "cianfhoghlaim.dev",
  plan: "free",
});

export const docsRecord = new cloudflare.Record("docs", {
  zoneId: zone.id,
  name: "docs",
  type: "CNAME",
  value: "cianfhoghlaim-docs.pages.dev",
  proxied: true,
});
```

## Secrets Management

Pulumi secrets are encrypted in state:

```bash
# Set a secret
pulumi config set --secret database_password "..."

# Access in code
const dbPassword = config.requireSecret("database_password");
```

For 1Password integration, see [Locket](./locket).

## Dagger Integration

Deploy via Dagger pipelines:

```typescript
// bonneagar/dagger/src/infrastructure.ts
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

## Related

- [Dagger](./dagger) - CI/CD integration
- [Komodo](./komodo) - Container deployment
- [Infrastructure Overview](./overview)
