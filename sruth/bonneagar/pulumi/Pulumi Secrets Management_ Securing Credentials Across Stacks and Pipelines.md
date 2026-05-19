---
title: "Pulumi Secrets Management: Securing Credentials Across Stacks and Pipelines"
source: "https://infisical.com/blog/pulumi-secrets-management"
author:
  - "[[Ashwin Punj]]"
published: 2026-04-01
created: 2026-05-17
description: "Learn how to secure credentials across Pulumi stacks and pipelines with external secrets management, automated rotation, and centralized access control."
tags:
  - "clippings"
---
![Blog image](https://infisical.com/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Frzezkvk1rm65%2F1CDNYeMrm0xQ5AAEB72jze%2F7fbfe0e53f767f9cff36b33309d0dcf9%2FPulumi_Secrets_Management.png&w=1920&q=75)

Pulumi lets you define cloud infrastructure in general-purpose languages like TypeScript, Python, Go, C#, and Java. That gives engineering teams full programmatic control over resources across AWS, Azure, GCP, and Kubernetes.

But that flexibility comes with a real operational challenge. Your Pulumi stacks need access to sensitive credentials at every layer. Provider authentication requires cloud access keys. Infrastructure configuration depends on database passwords and API tokens. And state files end up storing encrypted versions of all of it. As teams and stacks grow, keeping those secrets secure, rotated, and properly scoped becomes increasingly difficult to manage within Pulumi alone.

This guide breaks down how secrets flow through Pulumi's architecture, where the built-in encryption model falls short for production environments, and how to integrate an external secrets manager to get centralized access control, rotation, and audit capabilities without disrupting your existing Pulumi workflows.

## Understanding Pulumi's Architecture

Pulumi lets you write infrastructure as code in your language of choice. Your code defines a [directed acyclic graph (DAG)](https://www.pulumi.com/docs/iac/concepts/how-pulumi-works/) of resources that describes how your cloud infrastructure is composed.

![Standard Pulumi Architecture](https://images.ctfassets.net/rzezkvk1rm65/1wj2cnjQHk4ZQYPUJ07UkB/7dcd7e68a3516b776a7c61fa933d6b2f/Standard_Pulumi_Architecture.jpg)

When you run `pulumi up`, the engine creates a stack, which is an isolated, configurable instance of your program. Think of stacks as deployment environments: production, staging, development, and so on.

The engine coordinates with cloud providers to create, update, or delete resources until the actual state matches your desired state. Throughout that process, Pulumi maintains state files that track every resource, its metadata, outputs, and relationships. You can store these state files in the Pulumi Cloud service (the default), a self-managed backend like S3, or a local filesystem.

Any secrets your infrastructure references end up in those state files. That makes securing them a hard requirement, not an afterthought.

### Where secrets interact with Pulumi

Pulumi's IaC model touches secrets in three distinct contexts. Each one represents a surface where sensitive data needs to be handled carefully:

1. **Provider authentication.** Cloud access keys for deploying EC2 instances, Azure service principals for managing resource groups, Kubernetes cluster credentials for deploying workloads. Your Pulumi program needs these credentials during `pulumi up` to authenticate with providers and execute changes, but they are typically managed outside of Pulumi itself.
2. **Infrastructure configuration.** Database connection strings, third-party API keys, TLS certificates, and encryption keys all live here. Unlike provider credentials that are only used during deployment, configuration secrets become part of your running infrastructure.
3. **State files.** Pulumi stores encrypted versions of inputs, outputs, and metadata in state. When you create a database, the generated admin password becomes a state secret. These values need protection both at rest and when accessed for stack outputs or subsequent deployments.

To make this concrete: a typical microservices deployment might use AWS credentials to provision RDS databases and ECS services, Stripe API keys and SendGrid credentials in the application configuration, and an RDS-generated admin password stored in state. Each category has different access patterns, different lifecycle requirements, and different security controls.

## Pulumi's Built-in Secrets Handling

Pulumi ships with encryption capabilities that protect secrets at rest and in transit. Encrypted secrets are stored in state files and stack configuration, shielded from casual exposure. Before evaluating whether you need an external secrets manager, it's worth understanding what Pulumi provides out of the box.

### Encrypting secrets in configuration and state

When you mark a value as secret using `pulumi.secret()` or the `--secret` flag, Pulumi encrypts it before storing it in the state file. Each stack gets its own encryption key, and a per-value salt is applied to prevent identical plaintext values from producing identical ciphertext.

By default, encryption is handled by the Pulumi Cloud service. But you can swap in an alternative provider depending on your organization's requirements:

- **AWS KMS** for teams already managing encryption through AWS
- **Azure Key Vault** for Azure-centric infrastructure
- **Google Cloud KMS** for GCP environments
- **HashiCorp Vault** for teams with an existing Vault deployment
- **Passphrase-based encryption** for local or self-managed backends

To initialize a stack with a custom encryption provider, you pass it at creation time:

```js
pulumi stack init my-stack \
  --secrets-provider="awskms://alias/my-key?region=us-east-1"
```

### How secret propagation works

Pulumi tracks secret values through your program's execution. When you retrieve a secret using `config.requireSecret()`, the returned value is wrapped in a secret Output. Any Output derived from that secret is automatically marked as secret too.

This means if you interpolate a database password into a connection string, Pulumi knows the resulting string is also sensitive and encrypts it in state accordingly.

On the CLI side, Pulumi redacts secret values in terminal output, replacing them with `[secret]` placeholders. This prevents secrets from appearing in plain text in logs, CI/CD output, or terminal history.

### Pulumi ESC: centralized environments

Pulumi [ESC](https://www.pulumi.com/docs/esc/) (Environments, Secrets, and Configuration) is Pulumi's dedicated product for managing secrets and configuration at scale across stacks, teams, and tools. Rather than duplicating credentials across stack config files, ESC lets you define composable YAML environments that act as a single source of truth. Those environments can pull secrets dynamically from external stores like AWS Secrets Manager, Azure Key Vault, or Infisical through built-in providers, and can also issue short-lived cloud credentials via OIDC: eliminating the need for long-lived access keys entirely.

ESC includes RBAC, environment versioning with taggable releases, and audit logging. It integrates directly with Pulumi IaC stacks via the `environment` block in your stack config file, but also works independently with any CLI tool or CI/CD pipeline via the `esc run` command.

For teams fully invested in the Pulumi ecosystem, ESC addresses several of the gaps in Pulumi's core secrets model. But it does tie your secrets management to Pulumi's platform, which may not work for organizations that need a secrets layer that spans across IaC tools, CI/CD pipelines, application runtimes, and other internal systems.

### Where Pulumi's native model falls short

Even with ESC in the picture, there are structural limitations that become apparent at scale:

- **Binary stack-level access.** Pulumi provides environment-level RBAC via ESC, but lacks fine-grained, per-secret access controls and ABAC-style policies. You either have access to the entire stack and every secret in it, or you don't. There's no way to scope read-only access to individual secrets, grant temporary access that auto-expires, or implement attribute-based access control (ABAC). For organizations that need to enforce least-privilege access at the secret level, this is a hard constraint.
- **Static secrets by default.** Secrets in Pulumi are stored as static values. They don't expire, rotate automatically, or get generated on demand. Modern security practices recommend dynamic, short-lived credentials that reduce the blast radius if a secret is compromised. Pulumi does not natively generate or manage dynamic secrets, but can consume them from external systems like Infisical.
- **No cross-platform audit trail.** If your secrets are consumed by Pulumi stacks, Kubernetes clusters, CI/CD pipelines, and application runtimes, you need a single audit trail that tracks access across all of those contexts. Pulumi's audit capabilities are scoped to its own platform.
- **Rotation is manual.** There's no built-in mechanism for automated secret rotation. When a credential needs to be cycled, someone has to update the config value, run `pulumi up`, and hope every downstream consumer picks up the change. At scale, this becomes a reliability risk as much as a security one.

## Securing Pulumi with an External Secrets Manager

Most IaC tools treat secrets as a secondary concern, and the gaps in access control, rotation, and auditing tend to follow the same pattern. The standard approach for production environments is to pair your IaC platform with a dedicated secrets manager that handles the full lifecycle: storage, access control, rotation, auditing, and distribution.

For Pulumi teams, Infisical is one option worth evaluating. It's an open-source secrets management platform that centralizes secrets, certificates, and privileged access in a single tool. More importantly for this context, it integrates natively with Pulumi through dedicated ESC providers for authentication and secret retrieval, so you don't have to rearchitect your existing workflows to adopt it.

Here's how Infisical maps to the specific gaps in Pulumi's native secrets model:

### Granular access control instead of all-or-nothing stacks

Infisical supports [role-based access control](https://infisical.com/docs/documentation/platform/access-controls/overview) at the project, environment, and individual secret level. You can grant a CI/CD pipeline read-only access to production database credentials without exposing API keys for third-party services in the same environment.

Beyond RBAC, Infisical also supports [ABAC](https://infisical.com/docs/documentation/platform/access-controls/attribute-based-access-controls), where permissions are evaluated dynamically based on metadata attributes on the identity requesting access. This is the kind of policy granularity that compliance frameworks like SOC 2 and ISO 27001 expect, and that Pulumi's stack-level model can't provide on its own.

### Dynamic and temporary credentials instead of static secrets

Infisical can generate [dynamic secrets](https://infisical.com/docs/documentation/platform/dynamic-secrets/overview) on demand for a wide range of backends: including PostgreSQL, MySQL, MongoDB, Oracle, MSSQL, Cassandra, Redis, RabbitMQ, Snowflake, AWS IAM, AWS ElastiCache, Azure Entra ID, Azure SQL, GCP IAM, LDAP, Elasticsearch, Couchbase, Mongo Atlas, SAP ASE, SAP HANA, Vertica, GitHub, TOTP, and Kubernetes service accounts. These credentials are short-lived and unique to each consumer, which means a compromised secret has a limited blast radius and expires automatically.

For individual users and operators, Infisical's [temporary access provisioning](https://infisical.com/docs/documentation/platform/access-controls/temporary-access) lets you grant time-boxed permissions that auto-revoke. Combined with [access request](https://infisical.com/docs/documentation/platform/access-controls/access-requests) workflows, this gives teams a self-service model for production access that doesn't require a platform engineer to manually update policies.

### Cross-platform audit trail

Infisical provides a centralized audit log that tracks every secret access, modification, and deletion across all consumers, whether that's a Pulumi stack, a Kubernetes deployment, a CI/CD pipeline, or a developer's local environment. For organizations that need to stream these logs to a SIEM or external monitoring tool, Infisical supports [audit log streaming](https://infisical.com/docs/documentation/platform/audit-log-streams) to providers like Datadog and Better Stack.

This is a meaningful difference from Pulumi's audit capabilities, which only cover operations within the Pulumi platform itself.

### How the integration works

Infisical connects to Pulumi through two providers available via [Pulumi ESC](https://www.pulumi.com/blog/esc-infisical-providers-launch/):

- **`infisical-login`** handles authentication. It generates short-lived OIDC tokens for Infisical, so your Pulumi stacks never need long-lived API keys or service tokens to access secrets. Credentials are created just-in-time and expire automatically.
- **`infisical-secrets`** handles secret retrieval. It dynamically fetches secrets from Infisical at runtime, respecting whatever access controls and policies you've configured. Secrets are resolved during `pulumi up` and made available to your program without being hardcoded in config files or environment variables.

The key architectural point: Infisical becomes the source of truth for secrets, while Pulumi remains the orchestration layer for infrastructure. Your Pulumi code references secrets by name, and Infisical handles who can access them, when they expire, how they're rotated, and who accessed them last.

## Implementing Infisical with Pulumi

The fastest way to get started is through the [Pulumi ESC providers](https://www.pulumi.com/docs/esc/integrations/) for Infisical. The setup uses OIDC-based authentication so your Pulumi stacks never store long-lived Infisical credentials.

### Prerequisites

Before starting, you'll need:

- A Pulumi Cloud **organization** account (not just an individual account) with ESC enabled: ESC environments and RBAC require an organization context
- The **Pulumi ESC CLI** (`esc`) installed alongside your existing Pulumi CLI
- An Infisical account with a project containing secrets you want to consume
- An Infisical Machine Identity configured with OIDC authentication pointed at `https://api.pulumi.com/oidc`
- The Identity ID from that OIDC configuration

**Important:** There is a [known issue](https://github.com/pulumi/pulumi/issues/14509) when integrating Pulumi ESC with Pulumi IaC (as opposed to standalone ESC use): the default OIDC subject identifier sent to Infisical does not work out of the box. You will need to either configure a custom `subjectAttributes` in your ESC environment definition, or add the literal subject claim `pulumi:environments:org:{your-org}:env:<yaml>` to your Infisical Identity's allowed subjects: replacing `{your-org}` with your Pulumi organization name. Skipping this step will result in silent authentication failures when running `pulumi up`.

### Step 1: Configure dynamic authentication

Create a Pulumi ESC environment that handles authentication with Infisical. This environment generates a short-lived OIDC token each time it's opened, so no static credentials are stored anywhere.

Create an environment (for example, `your-org/infisical-auth/oidc-login`) with the following definition:

```js
# Environment: your-org/infisical-auth/oidc-login
values:
  infisical:
    login:
      fn::open::infisical-login:
        oidc:
          identityId: <your-identity-id> # Replace with your Infisical Identity ID

  environmentVariables:
    INFISICAL_TOKEN: ${infisical.login.accessToken}
```

Validate the setup by running:

```js
esc open your-org/infisical-auth/oidc-login
```

The output should include an `accessToken` under `infisical.login`. If you see an authentication error, double-check that the Identity ID is correct and that the OIDC configuration in Infisical points to `https://api.pulumi.com/oidc` with the correct subject claim as noted in the prerequisites.

### Step 2: Fetch secrets from Infisical

Create a second ESC environment for the secrets your application or infrastructure actually needs. This environment imports the authentication environment from Step 1 and uses the `infisical-secrets` provider to pull secrets at runtime.

Note that `infisical-secrets` must be nested as a sibling of `login` under the same `infisical` key. This is required for the `${infisical.login}` interpolation to resolve correctly.

For example, create `your-org/my-app/dev`:

```js
# Environment: your-org/my-app/dev
imports:
  - your-org/infisical-auth/oidc-login

values:
  infisical:
    secrets:
      fn::open::infisical-secrets:
        login: ${infisical.login}
        get:
          dbPassword:
            projectId: <your-infisical-project-id>
            environment: dev
            secretKey: DATABASE_PASSWORD
          stripeKey:
            projectId: <your-infisical-project-id>
            environment: dev
            secretKey: STRIPE_API_KEY

  # environmentVariables injects secrets as OS-level env vars (useful for CLI tools and subprocesses)
  environmentVariables:
    DATABASE_PASSWORD: ${infisical.secrets.dbPassword}
    STRIPE_API_KEY: ${infisical.secrets.stripeKey}

  # pulumiConfig makes secrets available via the Pulumi config API in your IaC program (config.requireSecret)
  pulumiConfig:
    DATABASE_PASSWORD: ${infisical.secrets.dbPassword}
    STRIPE_API_KEY: ${infisical.secrets.stripeKey}
```

Validate with:

```js
esc open your-org/my-app/dev
```

You should see the fetched secret values under `infisicalSecrets` and the corresponding environment variables.

### Step 3: Use secrets in your Pulumi stack

To make these secrets available in your Pulumi IaC program, reference the ESC environment in your stack configuration file. For production stacks, pin the environment to a specific version or tag to prevent unexpected changes from affecting live deployments:

```js
# Pulumi.dev.yaml
environment:
  - your-org/my-app/dev         # always latest
  # - your-org/my-app/dev@7     # pinned to revision 7 (recommended for production)
```

From there, your Pulumi program can access the secrets through the standard configuration API. Note that `config.requireSecret()` reads from the `pulumiConfig` block: not from `environmentVariables`:

```ts
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const dbPassword = config.requireSecret("DATABASE_PASSWORD");
const stripeKey = config.requireSecret("STRIPE_API_KEY");
```

Secrets fetched this way are resolved at runtime during `pulumi up`. They're never hardcoded in your config files, and Infisical's access controls, audit logging, and rotation policies apply to every retrieval.

### Step 4: Inject secrets into CI/CD pipelines

A key advantage of the ESC-based setup is that the same environment integrates cleanly into your CI/CD workflows without requiring any additional Infisical credentials to be stored in GitHub or another CI/CD platform.

Here is a minimal GitHub Actions example that uses Pulumi's OIDC action to exchange a short-lived GitHub token for a Pulumi access token, which then opens the ESC environment and injects secrets for `pulumi up`:

```ts
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate with Pulumi Cloud (OIDC)
        uses: pulumi/auth-actions@v1
        with:
          organization: your-org
          requested-token-type: urn:pulumi:token-type:access_token:team
          team: your-team-name

      - name: Deploy with Pulumi
        uses: pulumi/actions@v6
        with:
          command: up
          stack-name: your-org/your-stack-name
```

When `pulumi up` runs, the Pulumi CLI automatically opens the ESC environment referenced in `Pulumi.dev.yaml`, fetches secrets from Infisical via OIDC, and makes them available to your program. No secrets are stored in GitHub Actions at any point in this flow.

### Step 5: Inject secrets into other tools

The same ESC environment can inject secrets into any CLI tool or process using `esc run`:

```js
# Run a database migration with secrets injected as env vars
esc run your-org/my-app/dev -- npx prisma migrate deploy

# Run Infisical CLI commands directly
esc run your-org/infisical-auth/oidc-login -- infisical secrets list --projectId=<your-project-id>
```

This makes the integration useful beyond Pulumi itself. CI/CD pipelines, local development workflows, and application runtimes can all consume secrets from the same source without duplicating credentials across systems.

## Beyond Secrets: Infisical Across the Infrastructure Lifecycle

One of the less obvious advantages of using Infisical alongside Pulumi is that it covers more than secrets. The infrastructure Pulumi provisions generates ongoing access and certificate management requirements that go well beyond what a secrets manager alone can address. Infisical's platform covers these adjacent use cases, letting you consolidate tooling rather than reaching for separate products.

### Kubernetes: keeping secrets in sync with your workloads

Pulumi may provision your Kubernetes clusters, but the workloads running in them need a reliable path to the same secrets. Infisical's Kubernetes Operator bridges that gap by syncing secrets directly into native Kubernetes Secrets via three Custom Resource Definitions (CRDs):

- **`InfisicalSecret`**: syncs secrets from Infisical into Kubernetes, and automatically reloads dependent Deployments, DaemonSets, and StatefulSets when values change.
- **`InfisicalPushSecret`**: pushes secrets from a Kubernetes Secret back into Infisical, enabling bi-directional sync.
- **`InfisicalDynamicSecret`**: syncs dynamic secrets and manages time-bound leases automatically inside the cluster.

The operator is installed via Helm and can be scoped to a single namespace or deployed cluster-wide. It also exposes Prometheus metrics for reconciliation monitoring. If you're already using the External Secrets Operator, the Infisical provider for ESO is supported as well.

This means your Pulumi stack and your Kubernetes workloads can both draw from the same Infisical source of truth, with no manual sync steps between them.

### Certificate Management: full lifecycle automation for X.509

Infrastructure provisioned by Pulumi routinely requires TLS certificates: for load balancers, internal services, databases, and inter-service mTLS. Managing those certificates as static secrets is error-prone and doesn't scale. Infisical's Certificate Management product handles the complete X.509 lifecycle:

- **Private CA hierarchies**: create and manage root and intermediate CAs directly within Infisical, with a visual management dashboard.
- **External CA integrations**: connect to Let's Encrypt, DigiCert, Microsoft AD CS, AWS Private CA, and any ACME-compatible CA for publicly trusted certificates.
- **Enrollment automation**: issue certificates via API, ACME, or EST, enabling standard automation tools like `certbot` and Kubernetes `cert-manager` to work against Infisical as a backend.
- **Certificate syncs**: push certificates to AWS Certificate Manager, AWS Elastic Load Balancer, Azure Key Vault, and Cloudflare automatically.
- **Certificate discovery**: scan IP ranges, CIDR blocks, and domains across TLS ports to build a complete inventory of deployed certificates across your infrastructure, including certificates issued outside of Infisical. Scheduled scans keep the inventory current.
- **Expiration alerts**: receive configurable notifications and webhook events before certificates expire, preventing the kind of surprise outages that static management inevitably produces.

For teams using Pulumi to provision infrastructure where certificates are a first-class concern: Kubernetes clusters, service meshes, internal APIs: having certificate lifecycle automation in the same platform as secrets management eliminates an entire category of operational gap.

### Privileged Access Management: securing access to the infrastructure Pulumi builds

Once Pulumi has provisioned your databases and servers, someone needs to access them: for debugging, migrations, and incident response. Static credentials shared over Slack or stored in `.env` files are the most common approach, and the most common source of exposure.

Infisical PAM addresses this by decoupling user identity from infrastructure credentials. The core workflow:

1. A user opens Infisical and sees a catalog of resources they are permitted to access: databases, servers, and Kubernetes clusters.
2. They select a resource and initiate a connection via the Infisical CLI.
3. Infisical validates the request, establishes a secure tunnel through its lightweight Gateway, and injects the credentials automatically. **The user never sees the underlying password or key.**
4. The entire session is logged and recorded for audit purposes.

The Gateway is deployed with a single CLI command and operates via outbound-only SSH tunnels, requiring no inbound firewall rule changes. Session recording covers database queries, SSH, RDP, and Kubernetes access, and automated credential rotation ensures that the accounts behind those sessions are cycled regularly.

For teams operating production infrastructure provisioned by Pulumi, this closes the loop between "what Pulumi built" and "how people access what Pulumi built": under a single audit trail.

## Start Managing Pulumi Secrets with Infisical

Pulumi gives you powerful infrastructure orchestration, but its native secrets model wasn't built to handle granular access control, automated rotation, or cross-platform auditing at scale. Infisical fills those gaps without requiring you to change how you write or deploy Pulumi code. With OIDC-based authentication, dynamic secret fetching, and centralized policy enforcement, your secrets stay secure across every stack, pipeline, and runtime environment.

Infisical is open source, SOC 2 compliant, and used by organizations like Hugging Face to secure over 500 million secrets daily. Whether you need cloud-hosted convenience or full self-hosted control, the platform supports both deployment models, with advanced features like dynamic secrets, audit log streaming, and approval workflows available under an Enterprise license.

You can [get started with Infisical for free](https://app.infisical.com/signup) and have it integrated with your Pulumi workflows in minutes.

![Ashwin Punj avatar](https://infisical.com/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Frzezkvk1rm65%2Fg5Y7lYtiWBLfgKzjvnSBX%2F25d556fb926c9d994542213d16423f67%2Fimage__6_.png&w=256&q=75)

### Ashwin Punj

Solutions Engineer, Infisical

Starting with Infisical is simple, fast, and free.