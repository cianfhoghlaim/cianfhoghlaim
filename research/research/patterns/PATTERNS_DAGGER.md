# Dagger Patterns for Cianfhoghlaim

Consolidated patterns for infrastructure automation using Dagger TypeScript SDK.

**Module:** `bonneagar/dagger/` | **Engine:** v0.19.2 | **SDK:** TypeScript

---

## Quick Reference

```bash
# Initialize module
cd bonneagar/dagger && dagger develop

# List all functions
dagger functions

# Common invocations
dagger call bonneagar --ansible-dir=./ansible run-playbook --playbook=deploy.yml
dagger call ci run-pipeline --source=. --ssh-key=env:SSH_KEY
dagger call git-ops-setup setup-complete --forgejo-host=https://git.example.com
dagger call pangolin-deployment deploy-full --target-host=192.168.1.1 --domain=example.com
```

---

## Container Patterns

### Base Container Setup

Most modules follow a consistent base container pattern:

```typescript
@func()
baseContainer(): Container {
  return dag
    .container()
    .from("curlimages/curl:8.11.1");  // For API calls
}

// Alternative bases by use case:
// - "python:3.12-slim"           - Python/Ansible
// - "oven/bun:latest"            - TypeScript/Bun
// - "node:22-slim"               - Node.js/npm
// - "rust:1.83-slim"             - Rust/cargo
// - "1password/op:2"             - 1Password CLI
// - "docker:27-cli"              - Docker operations
// - "ghcr.io/astral-sh/uv:python3.12-bookworm" - Python with uv
// - "alpine:3.19"                - Minimal with shell
```

### Secret Mounting

```typescript
// Environment variable injection (preferred for API keys)
container
  .withSecretVariable("API_KEY", apiKeySecret)
  .withExec(["sh", "-c", "curl -H 'Authorization: Bearer $API_KEY' ..."])

// File mounting (for SSH keys, config files)
container
  .withMountedSecret("/root/.ssh/id_ed25519", sshKey)
  .withExec(["chmod", "600", "/root/.ssh/id_ed25519"])
```

### Cache Mounting

```typescript
// Package manager caches
container
  .withMountedCache("/root/.cache/pip", dag.cacheVolume("pip-cache"))
  .withMountedCache("/root/.npm", dag.cacheVolume("npm-cache"))
  .withMountedCache("/root/.cargo", dag.cacheVolume("cargo-cache"))
```

---

## Infrastructure Automation

### Ansible Playbook Execution

```typescript
@func()
async runPlaybook(
  playbook: string,
  inventory: string = "inventory/hosts.yml",
  extraVars?: string,
  tags?: string,
  limit?: string
): Promise<string> {
  let container = await this.ansibleContainer();

  const args = ["ansible-playbook", `-i ${inventory}`, playbook];
  if (extraVars) args.push(`-e '${extraVars}'`);
  if (tags) args.push(`--tags ${tags}`);
  if (limit) args.push(`-l ${limit}`);

  return container.withExec(["sh", "-c", args.join(" ")]).stdout();
}
```

### Docker Compose Validation

```typescript
@func()
async validate(composeFile: string = "docker-compose.yml"): Promise<string> {
  return dag
    .container()
    .from("docker:27-cli")
    .withMountedDirectory("/compose", this.composeDir)
    .withWorkdir("/compose")
    .withExec(["docker", "compose", "-f", composeFile, "config"])
    .stdout();
}
```

### 1Password Secret Retrieval

```typescript
@func()
async getSecret(
  reference: string,        // e.g., "op://vault/item/field"
  connectHost: string,      // 1Password Connect server
  connectToken: Secret
): Promise<Secret> {
  const output = await dag
    .container()
    .from("1password/op:2")
    .withSecretVariable("OP_CONNECT_TOKEN", connectToken)
    .withEnvVariable("OP_CONNECT_HOST", connectHost)
    .withExec(["op", "read", reference])
    .stdout();

  return dag.setSecret("op-secret", output.trim());
}
```

---

## Deployment Orchestration

### Multi-Stage Deployment (PangolinDeployment)

10-stage platform deployment with resume capability:

```typescript
// Stage definitions
const STAGES = [
  "init_server",           // SSH access, Docker setup
  "deploy_op_connect",     // 1Password Connect
  "deploy_pangolin_core",  // Pangolin with TinyAuth
  "setup_pocketid_admin",  // WebAuthn admin setup (human-in-the-loop)
  "create_oauth_client",   // PocketID OAuth for TinyAuth
  "generate_crowdsec_key", // CrowdSec enrollment
  "deploy_komodo",         // Komodo Core
  "deploy_forgejo",        // Git server
  "create_pangolin_sites", // Site configurations
  "deploy_app_stacks",     // Application deployments
];

// Resume from specific stage
@func()
async deployFrom(
  startStage: string,
  stateJson?: string  // Previous DeploymentState
): Promise<string> {
  const state: DeploymentState = stateJson
    ? JSON.parse(stateJson)
    : this.initState();

  const startIndex = STAGES.indexOf(startStage);
  for (let i = startIndex; i < STAGES.length; i++) {
    const result = await this.executeStage(STAGES[i], state);
    if (!result.success) {
      return JSON.stringify({ ...state, failedAt: STAGES[i] });
    }
  }
  return JSON.stringify(state);
}
```

### Stage Result Pattern

```typescript
interface StageResult {
  stage: string;
  success: boolean;
  message?: string;
  data?: Record<string, unknown>;
  error?: string;
  duration: number;
}

async executeStage(stage: string, state: DeploymentState): Promise<StageResult> {
  const start = Date.now();
  try {
    const data = await this.stageHandlers[stage](state);
    return {
      stage,
      success: true,
      data,
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      stage,
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      duration: Date.now() - start,
    };
  }
}
```

---

## API Integration Patterns

### REST API Wrapper (Komodo)

Generic request methods with typed responses:

```typescript
@object()
export class Komodo {
  private curlContainer(): Container {
    return dag
      .container()
      .from("curlimages/curl:8.11.1")
      .withSecretVariable("API_KEY", this.apiKey)
      .withSecretVariable("API_SECRET", this.apiSecret);
  }

  @func()
  async read(operation: string, params: string = "{}"): Promise<string> {
    return this.curlContainer()
      .withExec([
        "sh", "-c",
        `curl -sf -X POST "${this.coreUrl}/read/${operation}" \
          -H "Content-Type: application/json" \
          -H "x-api-key: $API_KEY" \
          -H "x-api-secret: $API_SECRET" \
          -d '${params}'`,
      ])
      .stdout();
  }

  // Specific typed methods
  @func()
  async listStacks(): Promise<string> {
    return this.read("ListStacks", "{}");
  }

  @func()
  async deployStack(stackName: string): Promise<string> {
    return this.execute("DeployStack", JSON.stringify({ stack: stackName }));
  }
}
```

### Pangolin Integration API

30+ methods for complete platform management:

```typescript
// Organization management
await api.createOrg(orgId, name, subnet);
await api.listOrgs();

// Site management with defaults
await api.createSiteWithDefaults(orgId, name, "newt");

// Resource and target creation
await api.createResource(orgId, name, http, protocol, domainId);
await api.createTarget(resourceId, siteId, ip, port);

// Blueprint application
await api.applyBlueprint(orgId, blueprintBase64);

// Identity provider setup
await api.createOidcIdp(name, clientId, clientSecret, authUrl, tokenUrl, ...);
```

### Error Handling

```typescript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  return response.json();
} catch (error) {
  // Log and re-throw with context
  console.error(`${operation} failed:`, error);
  throw error;
}
```

---

## CI/CD Patterns

### Polyglot Testing

```typescript
@object()
export class CI {
  @func()
  async testAll(source: Directory): Promise<string> {
    const results: string[] = [];

    // Python tests
    const python = new Python();
    results.push(await python.testAll(source));

    // TypeScript tests
    const typescript = new TypeScript();
    results.push(await typescript.check(source));

    // Rust tests (if Cargo.toml exists)
    const rust = new Rust();
    results.push(await rust.check(source, "bonneagar/locket"));

    return results.join("\n\n");
  }
}
```

### Python CI with uv

```typescript
@func()
baseContainer(): Container {
  return dag
    .container()
    .from("ghcr.io/astral-sh/uv:python3.12-bookworm");
}

@func()
async testAll(source: Directory): Promise<string> {
  const container = this.baseContainer()
    .withDirectory("/src", source)
    .withWorkdir("/src")
    .withExec(["uv", "sync"]);

  // Run all checks
  await container.withExec(["uv", "run", "pytest"]).sync();
  await container.withExec(["uv", "run", "pyright"]).sync();
  await container.withExec(["uv", "run", "ruff", "check", "."]).sync();

  return "All Python checks passed";
}
```

### TypeScript CI with Bun

```typescript
@func()
async check(source: Directory): Promise<string> {
  const container = dag
    .container()
    .from("oven/bun:latest")
    .withDirectory("/src", source)
    .withWorkdir("/src")
    .withExec(["bun", "install", "--frozen-lockfile"]);

  // Type checking
  await container.withExec(["bunx", "tsc", "--noEmit"]).sync();

  // Linting
  await container.withExec(["bunx", "eslint", "."]).sync();

  return "All TypeScript checks passed";
}
```

### Rust CI

```typescript
@func()
async check(source: Directory, project: string): Promise<string> {
  const container = dag
    .container()
    .from("rust:1.83-slim")
    .withExec(["apt-get", "update"])
    .withExec(["apt-get", "install", "-y", "pkg-config", "libssl-dev"])
    .withDirectory("/src", source)
    .withWorkdir(`/src/${project}`);

  // Add components and run checks
  await container
    .withExec(["rustup", "component", "add", "clippy", "rustfmt"])
    .withExec(["cargo", "clippy", "--", "-D", "warnings"])
    .withExec(["cargo", "fmt", "--", "--check"])
    .withExec(["cargo", "test"])
    .sync();

  return "All Rust checks passed";
}
```

### Cloudflare Deployment

```typescript
@func()
async deployPages(
  buildDir: Directory,
  projectName: string,
  apiToken: Secret,
  accountId: string
): Promise<string> {
  return dag
    .container()
    .from("node:22-slim")
    .withExec(["npm", "install", "-g", "wrangler"])
    .withSecretVariable("CLOUDFLARE_API_TOKEN", apiToken)
    .withEnvVariable("CLOUDFLARE_ACCOUNT_ID", accountId)
    .withDirectory("/build", buildDir)
    .withWorkdir("/build")
    .withExec(["wrangler", "pages", "deploy", ".", "--project-name", projectName])
    .stdout();
}
```

---

## Browser Automation

### Stagehand Integration

```typescript
@object()
export class BrowserAutomation {
  @field()
  serverUrl: string;  // sruth/browser/ multi-backend router

  @field()
  backend: string;    // "stagehand", "browserbase", etc.

  // Core operations
  @func() async navigate(url: string): Promise<string>;
  @func() async act(action: string): Promise<string>;      // Natural language
  @func() async observe(instruction: string): Promise<string>;
  @func() async extract(instruction: string): Promise<string>;
  @func() async screenshot(name?: string): Promise<string>;

  // Form automation
  @func()
  async fillForm(fields: string): Promise<string> {
    const formFields: FormField[] = JSON.parse(fields);
    return this.browserRequest("/api/form/fill", "POST", {
      fields: formFields,
      backend: this.backend,
    });
  }
}
```

### Human-in-the-Loop Approval

For WebAuthn and manual steps:

```typescript
@func()
async requestHumanApproval(
  task: string,
  instructions: string,  // JSON array of steps
  url?: string,
  timeout: number = 300
): Promise<string> {
  const request: HumanApprovalRequest = {
    task,
    instructions: JSON.parse(instructions),
    url,
    timeout,
  };
  return this.browserRequest("/api/approval/request", "POST", request);
}

// Usage in PocketID admin setup
@func()
async setupPocketIdAdmin(domain: string): Promise<string> {
  const approvalResult = await this.requestHumanApproval(
    "PocketID Admin Setup",
    JSON.stringify([
      `Navigate to https://auth.${domain}/setup`,
      "Create admin account with a secure username",
      "Register your passkey (WebAuthn) when prompted",
      "Complete the setup wizard",
    ]),
    `https://auth.${domain}/setup`,
    600  // 10 minute timeout
  );
  // ...
}
```

### OAuth Client Creation (Automated)

```typescript
@func()
async createOAuthClient(domain: string, redirectUri: string): Promise<string> {
  await this.createSession();
  await this.navigate(`https://auth.${domain}/admin`);
  await this.act("Click on OIDC Clients in the navigation menu");
  await this.act("Click the Add Client button");

  await this.fillForm(JSON.stringify([
    { name: "name", value: "TinyAuth", type: "text" },
    { name: "redirectUri", value: redirectUri, type: "text" },
  ]));

  await this.act("Click Save");

  const credentials = await this.extract(
    "Extract the Client ID and Client Secret values"
  );

  await this.closeSession();
  return credentials;
}
```

---

## GitOps Patterns

### 8-Step GitOps Pipeline

```typescript
@object()
export class GitOpsSetup {
  // Full pipeline execution
  @func()
  async setupComplete(): Promise<string> {
    const steps = [
      () => this.createRenovateUser(),
      () => this.generateToken(),
      () => this.setActionsSecret(),
      () => this.configureWebhooks(),
      () => this.createGitProvider(),
      () => this.deployRunner(),
      () => this.triggerSync(),
      () => this.verify(),
    ];

    for (const step of steps) {
      const result = await step();
      if (!result.success) return JSON.stringify(result);
    }
    return JSON.stringify({ success: true });
  }
}
```

### Forgejo Webhook Configuration

```typescript
@func()
async createWebhook(
  owner: string,
  repo: string,
  targetUrl: string,
  events: string[] = ["push"]
): Promise<string> {
  return this.curlContainer()
    .withExec([
      "sh", "-c",
      `curl -sf -X POST "${this.baseUrl}/api/v1/repos/${owner}/${repo}/hooks" \
        -H "Authorization: token $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "type": "forgejo",
          "config": { "url": "${targetUrl}", "content_type": "json" },
          "events": ${JSON.stringify(events)},
          "active": true
        }'`,
    ])
    .stdout();
}
```

### Komodo Resource Sync Trigger

```typescript
// Webhook URL format for Komodo sync
const webhookUrl = `https://komodo.${domain}/listener/github/resource_sync/${syncName}/main`;

// Trigger sync after push
@func()
async runSync(syncName: string): Promise<string> {
  return this.execute("RunSync", JSON.stringify({ sync: syncName }));
}
```

---

## Secret Migration Patterns

### Hardcoded Secret Detection

```typescript
const SECRET_PATTERNS = [
  /^[a-zA-Z0-9_-]{32,}$/,  // Long alphanumeric strings
  /^sk[-_]/i,              // OpenAI style keys
  /^ghp_/i,                // GitHub tokens
  /^hf_/i,                 // HuggingFace tokens
  /^bb_live_/i,            // Browserbase keys
];

@func()
async scanForHardcodedSecrets(configPath: string): Promise<string> {
  // Scan JSON config for values matching secret patterns
  // Returns array of { filePath, jsonPath, suggestedEnvVar, secretType }
}
```

### Locket Sidecar Generation

```typescript
@func()
async generateLocketTemplate(serverName: string, secrets: string): Promise<string> {
  const secretMappings: SecretMapping[] = JSON.parse(secrets);

  return `# Locket Sidecar Configuration
version: "1"
services:
  ${serverName}:
    secrets_file: /secrets/${serverName}.env
    refresh_interval: 300s

secrets:
${secretMappings.map(s => `  - env_var: ${s.envVar}
    op_reference: "${s.opReference}"`).join('\n')}
`;
}
```

---

## MCP Server Patterns

### Repository Analysis

```typescript
@func()
async analyzeGitHubRepo(repoUrl: string): Promise<string> {
  // Clone repo, analyze package.json/pyproject.toml
  // Extract: language, install command, run command, env vars
  // Determine complexity and deployment recommendation
  return JSON.stringify({
    repo: { language, url, stars },
    spec: { transport, installCommand, runCommand, envVars },
    complexity: 1-3,
    recommendation: "deploy" | "test" | "manual",
  });
}
```

### Protocol Compliance Testing

```typescript
@func()
async testMcpProtocol(serverCommand: string, serverArgs: string): Promise<string> {
  // Spawn MCP server
  // Send initialize request with MCP protocol
  // Verify response format and capabilities
  return JSON.stringify({
    success: boolean,
    protocolVersion: string,
    capabilities: {},
    tools: [],
    latency: { initializeMs: number },
  });
}
```

---

## Periphery Agent Deployment

### Connection Modes

```typescript
// Core→Periphery mode: Same network, Core connects to Periphery
// Periphery→Core mode: Remote server, Periphery connects outbound

@func()
async deploySingle(
  serverName: string,
  sshHost: string,
  sshUser: string,
  connectionMode: "core_to_periphery" | "periphery_to_core"
): Promise<string> {
  let envVars = "";
  if (connectionMode === "periphery_to_core") {
    envVars = `
      -e PERIPHERY_CORE_ADDRESSES="${this.komodoAddress}"
      -e PERIPHERY_CONNECT_AS="${serverName}"
    `;
  }

  // Deploy container with appropriate mode
  await this.sshExec(sshHost, sshUser, `
    docker run -d --name komodo-periphery \
      -v /var/run/docker.sock:/var/run/docker.sock \
      ${envVars} \
      ghcr.io/moghtech/komodo-periphery:${this.peripheryVersion}
  `);
}
```

### Public Key Registration

```typescript
// Extract public key from Periphery logs
const publicKey = await this.sshExec(host, user, `
  docker logs komodo-periphery 2>&1 | grep -oE 'MCow[A-Za-z0-9+/=]+' | head -1
`);

// Register in Komodo Core
await komodo.write("UpdateServer", {
  id: serverName,
  config: {
    address: `https://${host}:8120`,
    attempted_public_key: publicKey,
  },
});
```

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Secret not found` | 1Password reference invalid | Verify vault/item/field path with `op read` |
| `Connection refused` | Service not running | Check container status, verify port bindings |
| `SSH timeout` | Network/firewall issue | Verify SSH key permissions, check security groups |
| `Permission denied` | Missing sudo/docker group | Add user to docker group, check file permissions |
| `Container not found` | Image not pulled | Run `docker pull` first or check image name |
| `API 401 Unauthorized` | Invalid/expired token | Regenerate API key, check secret mounting |
| `Webhook delivery failed` | URL unreachable | Verify webhook URL, check Pangolin tunnel |
| `Resource sync failed` | Git provider not configured | Create Git provider in Komodo first |
| `Browser action timeout` | Element not found | Use `observe()` before `act()`, verify selectors |
| `WebAuthn required` | Can't automate passkey | Use human-in-the-loop approval workflow |

---

## Type Definitions

Key interfaces used across modules:

```typescript
interface StageResult {
  stage: string;
  success: boolean;
  message?: string;
  data?: Record<string, unknown>;
  error?: string;
  duration: number;
}

interface DeploymentResult {
  success: boolean;
  stages: StageResult[];
  state?: DeploymentState;
  error?: string;
}

interface ServiceHealth {
  name: string;
  status: "healthy" | "degraded" | "unhealthy";
  latency?: number;
  error?: string;
}

interface SecretMapping {
  envVar: string;
  opReference: string;
  description?: string;
  required?: boolean;
}
```

---

## Module Inventory

| Module | Class | Primary Purpose |
|--------|-------|-----------------|
| `index.ts` | `Bonneagar` | Ansible playbook execution |
| `index.ts` | `DockerCompose` | Compose validation |
| `index.ts` | `OnePassword` | 1Password secret retrieval |
| `pangolin.ts` | `PangolinDeployment` | 10-stage platform deployment |
| `pangolin-api.ts` | `PangolinApi` | Pangolin REST API (30+ methods) |
| `komodo.ts` | `Komodo` | Komodo Core API wrapper |
| `periphery.ts` | `Periphery` | Periphery agent deployment |
| `forgejo.ts` | `Forgejo` | Forgejo API automation |
| `gitops.ts` | `GitOpsSetup` | 8-step GitOps pipeline |
| `ci.ts` | `CI` | Polyglot CI/CD orchestration |
| `browser.ts` | `BrowserAutomation` | Stagehand browser automation |
| `typescript.ts` | `TypeScript` | TypeScript/Bun CI |
| `python.ts` | `Python` | Python/uv CI |
| `rust.ts` | `Rust` | Rust/cargo CI |
| `cloudflare.ts` | `Cloudflare` | Pages/Workers deployment |
| `mcp.ts` | `McpResearch` | MCP server discovery/testing |
| `secrets.ts` | `SecretMigration` | Secret migration to 1Password |
