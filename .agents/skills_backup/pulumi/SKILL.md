---
name: pulumi
description: Expert assistance for Pulumi Infrastructure as Code. Use when users need cloud resource provisioning, multi-cloud deployments, stack management, or infrastructure automation using TypeScript, Python, Go, or other languages.
---

# Pulumi - Infrastructure as Code

**Version:** 3.x | **Last Updated:** 2025-01

## Overview

Pulumi enables infrastructure as code using general-purpose programming languages:

- **Multi-Language**: TypeScript, Python, Go, .NET, Java, YAML
- **Multi-Cloud**: 120+ providers (AWS, Azure, GCP, Kubernetes, etc.)
- **Type Safety**: Full IDE support and compile-time checks
- **State Management**: Pulumi Cloud or self-hosted backends
- **Testing**: Unit, property, and integration testing

**Documentation**: https://www.pulumi.com/docs/

## When to Use This Skill

Activate when users need:

- "Provision cloud infrastructure with code"
- "Create infrastructure as code with TypeScript"
- "Deploy to AWS/Azure/GCP with Pulumi"
- "Manage Kubernetes resources programmatically"
- "Set up multi-cloud infrastructure"

## Core Concepts

### 1. Basic Resource Definition

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as aws from "@pulumi/aws"

// Create an S3 bucket
const bucket = new aws.s3.Bucket("my-bucket", {
  website: {
    indexDocument: "index.html",
  },
})

// Create an object in the bucket
const index = new aws.s3.BucketObject("index.html", {
  bucket: bucket.id, // Creates automatic dependency
  content: "<h1>Hello, Pulumi!</h1>",
  contentType: "text/html",
})

// Export the bucket URL
export const url = bucket.websiteEndpoint
```

### 2. Outputs and Dependencies

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as aws from "@pulumi/aws"

const bucket = new aws.s3.Bucket("my-bucket")

// Outputs are asynchronous - use apply() to transform
const bucketUrl = bucket.websiteEndpoint.apply(
  endpoint => `https://${endpoint}`
)

// Use pulumi.interpolate for string interpolation
const fullUrl = pulumi.interpolate`https://${bucket.websiteEndpoint}/index.html`

// Combine multiple outputs
const combined = pulumi.all([bucket.id, bucket.arn]).apply(
  ([id, arn]) => ({ id, arn })
)

export { bucketUrl, fullUrl }
```

### 3. Component Resources

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as aws from "@pulumi/aws"

interface WebServiceArgs {
  instanceType: string
  subnetIds: pulumi.Input<string>[]
}

class WebService extends pulumi.ComponentResource {
  public readonly loadBalancer: aws.lb.LoadBalancer
  public readonly url: pulumi.Output<string>

  constructor(name: string, args: WebServiceArgs, opts?: pulumi.ComponentResourceOptions) {
    super("custom:service:WebService", name, args, opts)

    // Create child resources with parent: this
    this.loadBalancer = new aws.lb.LoadBalancer(`${name}-lb`, {
      loadBalancerType: "application",
      subnets: args.subnetIds,
    }, { parent: this })

    const targetGroup = new aws.lb.TargetGroup(`${name}-tg`, {
      port: 80,
      protocol: "HTTP",
      vpcId: args.vpcId,
      healthCheck: {
        path: "/health",
        interval: 30,
      },
    }, { parent: this })

    this.url = this.loadBalancer.dnsName

    // Register outputs for stack exports
    this.registerOutputs({
      url: this.url,
    })
  }
}

// Usage
const webService = new WebService("my-app", {
  instanceType: "t3.micro",
  subnetIds: vpc.publicSubnetIds,
})
```

### 4. Configuration and Secrets

```typescript
import * as pulumi from "@pulumi/pulumi"

const config = new pulumi.Config()

// Required configuration
const region = config.require("region")
const instanceCount = config.requireNumber("instanceCount")

// Optional with defaults
const environment = config.get("environment") || "development"

// Secrets (encrypted in state)
const dbPassword = config.requireSecret("dbPassword")
const apiKey = config.getSecret("apiKey")

// Typed configuration object
interface AppConfig {
  port: number
  debug: boolean
}
const appConfig = config.requireObject<AppConfig>("app")
```

### 5. Stack References

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as aws from "@pulumi/aws"

// Reference outputs from another stack
const infraStack = new pulumi.StackReference("org/infrastructure/prod")

// Get typed outputs
const vpcId = infraStack.getOutput("vpcId")
const subnetIds = infraStack.getOutput("privateSubnetIds")

// Use in current stack
const instance = new aws.ec2.Instance("app", {
  ami: "ami-12345678",
  instanceType: "t3.micro",
  subnetId: subnetIds.apply(ids => ids[0]),
  vpcSecurityGroupIds: [securityGroup.id],
})
```

### 6. Resource Options

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as aws from "@pulumi/aws"

// Protect critical resources from deletion
const database = new aws.rds.Instance("prod-db", {
  // ... config
}, { protect: true })

// Explicit dependencies
const app = new aws.ec2.Instance("app", {
  // ... config
}, { dependsOn: [database] })

// Ignore changes to specific properties
const container = new aws.ecs.Service("api", {
  // ... config
}, { ignoreChanges: ["desiredCount"] })

// Delete before replace (for unique constraints)
const bucket = new aws.s3.Bucket("unique-name", {
  // ... config
}, { deleteBeforeReplace: true })

// Custom provider
const usWest = new aws.Provider("us-west", { region: "us-west-2" })
const westBucket = new aws.s3.Bucket("west-bucket", {}, { provider: usWest })
```

### 7. Testing

```typescript
import * as pulumi from "@pulumi/pulumi"
import { describe, it } from "mocha"
import * as assert from "assert"

// Mock Pulumi runtime
pulumi.runtime.setMocks({
  newResource: (args) => ({
    id: `${args.name}-id`,
    state: args.inputs,
  }),
  call: (args) => args.inputs,
})

describe("Infrastructure", () => {
  it("bucket should have versioning enabled", async () => {
    const infra = await import("./index")

    const versioning = await new Promise<boolean>((resolve) => {
      infra.bucket.versioning.apply((v) => {
        resolve(v?.enabled ?? false)
      })
    })

    assert.strictEqual(versioning, true)
  })

  it("should have correct tags", async () => {
    const infra = await import("./index")

    const tags = await new Promise((resolve) => {
      infra.bucket.tags.apply(resolve)
    })

    assert.strictEqual(tags?.Environment, "production")
  })
})
```

### 8. Cloudflare + Pulumi Example

```typescript
import * as pulumi from "@pulumi/pulumi"
import * as cloudflare from "@pulumi/cloudflare"

const config = new pulumi.Config()
const accountId = config.require("cloudflareAccountId")

// D1 Database
const database = new cloudflare.D1Database("my-db", {
  accountId: accountId,
  name: "production-db",
})

// R2 Bucket
const bucket = new cloudflare.R2Bucket("assets", {
  accountId: accountId,
  name: "my-app-assets",
})

// KV Namespace
const kvNamespace = new cloudflare.WorkersKvNamespace("cache", {
  accountId: accountId,
  title: "app-cache",
})

// Worker Script
const worker = new cloudflare.WorkerScript("api", {
  accountId: accountId,
  name: "my-api",
  content: pulumi.interpolate`
    export default {
      async fetch(request, env) {
        return new Response("Hello!");
      }
    }
  `,
  module: true,
  d1DatabaseBindings: [{
    name: "DB",
    databaseId: database.id,
  }],
  r2BucketBindings: [{
    name: "BUCKET",
    bucketName: bucket.name,
  }],
  kvNamespaceBindings: [{
    name: "CACHE",
    namespaceId: kvNamespace.id,
  }],
})

export const workerUrl = pulumi.interpolate`https://${worker.name}.workers.dev`
```

## CLI Commands

```bash
# Project setup
pulumi new typescript       # Create new TypeScript project
pulumi new aws-typescript   # With AWS template

# Stack management
pulumi stack init dev       # Create new stack
pulumi stack select prod    # Switch stacks
pulumi stack ls             # List stacks

# Configuration
pulumi config set region us-west-2
pulumi config set --secret dbPassword mySecret123
pulumi config get region

# Deployment
pulumi preview              # Preview changes
pulumi up                   # Apply changes
pulumi up --yes             # Skip confirmation
pulumi refresh              # Sync state with cloud
pulumi destroy              # Delete all resources

# State management
pulumi stack export --file state.json
pulumi stack import --file state.json

# Debugging
pulumi logs                 # View logs
pulumi stack graph          # Visualize dependencies
```

## Project Structure

```
my-pulumi-project/
├── Pulumi.yaml             # Project definition
├── Pulumi.dev.yaml         # Dev stack config
├── Pulumi.prod.yaml        # Prod stack config
├── index.ts                # Main program
├── components/
│   ├── vpc.ts              # VPC component
│   └── webService.ts       # Web service component
├── tests/
│   └── index.test.ts       # Unit tests
├── package.json
└── tsconfig.json
```

## Best Practices

1. **Use Component Resources**: Encapsulate related resources
2. **Type Everything**: Leverage TypeScript for safety
3. **Stack References**: Separate concerns across stacks
4. **Secret Management**: Use `--secret` for sensitive config
5. **Protect Production**: Use `protect: true` for critical resources
6. **Test Infrastructure**: Write unit and integration tests
7. **Version Control**: Commit Pulumi.*.yaml (not state)

## Common Anti-Patterns

```typescript
// BAD: Synchronous access to outputs
const url = bucket.websiteEndpoint + "/index.html" // Won't work!

// GOOD: Use interpolate or apply
const url = pulumi.interpolate`${bucket.websiteEndpoint}/index.html`

// BAD: Hardcoded values
const bucket = new aws.s3.Bucket("bucket", {
  tags: { Environment: "production" }, // Should use config
})

// GOOD: Use configuration
const config = new pulumi.Config()
const env = config.require("environment")
```

## Troubleshooting

### Output Type Errors
- Use `pulumi.interpolate` for string concatenation
- Use `.apply()` to transform output values
- Use `pulumi.all()` to combine multiple outputs

### State Conflicts
```bash
pulumi refresh              # Sync state with actual resources
pulumi stack export         # Backup state
pulumi state delete <urn>   # Remove orphaned resources
```

### Provider Issues
```bash
pulumi plugin ls            # List installed plugins
pulumi plugin install resource aws v6.0.0
```

## Resources

- **Documentation**: https://www.pulumi.com/docs/
- **Registry**: https://www.pulumi.com/registry/
- **Examples**: https://github.com/pulumi/examples
- **Community**: https://slack.pulumi.com
