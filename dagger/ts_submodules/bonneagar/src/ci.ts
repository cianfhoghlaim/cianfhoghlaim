/**
 * CI/CD Orchestration Module
 *
 * Orchestrates the full deployment pipeline:
 * 1. Lint and validate Ansible
 * 2. Validate Docker Compose files
 * 3. Deploy to staging
 * 4. Run health checks
 * 5. Deploy to production
 *
 * Also provides polyglot CI:
 * - Python (pytest, pyright, ruff)
 * - TypeScript (tsc, eslint, bun)
 * - Rust (cargo, clippy)
 * - Cloudflare (Pages, Workers)
 */

import {
  dag,
  Container,
  Directory,
  Secret,
  object,
  func,
} from "@dagger.io/dagger";

import { Bonneagar, DockerCompose, OnePassword } from "./index.js";
import { Python } from "./python.js";
import { TypeScript } from "./typescript.js";
import { Rust } from "./rust.js";
import { Cloudflare } from "./cloudflare.js";
import { APP_CONFIGS } from "./apps.js";

@object()
export class CI {
  @func()
  async runPipeline(
    ansibleDir: Directory,
    composeDir: Directory,
    sshKey: Secret,
    opToken: Secret,
    opConnectHost: string,
    targetHosts: string = "security.hetzner",
    dryRun: boolean = false
  ): Promise<string> {
    const results: string[] = [];

    // Step 1: Lint Ansible
    results.push("=== Step 1: Linting Ansible ===");
    const bonneagar = new Bonneagar(ansibleDir);
    try {
      const lintResult = await bonneagar.lint();
      results.push(`Lint passed:\n${lintResult}`);
    } catch (e) {
      results.push(`Lint failed: ${e}`);
      if (!dryRun) throw e;
    }

    // Step 2: Validate Docker Compose
    results.push("\n=== Step 2: Validating Docker Compose ===");
    const compose = new DockerCompose(composeDir);
    try {
      const validateResult = await compose.validate();
      results.push(`Compose validation passed:\n${validateResult.slice(0, 500)}...`);
    } catch (e) {
      results.push(`Compose validation failed: ${e}`);
      if (!dryRun) throw e;
    }

    // Step 3: Health check target hosts
    results.push("\n=== Step 3: Health Check ===");
    try {
      const healthResult = await bonneagar.healthCheck(targetHosts, sshKey);
      results.push(`Health check passed:\n${healthResult}`);
    } catch (e) {
      results.push(`Health check failed: ${e}`);
      if (!dryRun) throw e;
    }

    // Step 4: Deploy (if not dry run)
    if (!dryRun) {
      results.push("\n=== Step 4: Deploying Infrastructure ===");
      try {
        const deployResult = await bonneagar.deployInfrastructure(
          targetHosts,
          sshKey,
          opToken,
          opToken
        );
        results.push(`Deployment succeeded:\n${deployResult}`);
      } catch (e) {
        results.push(`Deployment failed: ${e}`);
        throw e;
      }

      // Step 5: Post-deployment health check
      results.push("\n=== Step 5: Post-Deployment Health Check ===");
      const postHealthResult = await bonneagar.healthCheck(targetHosts, sshKey);
      results.push(`Post-deployment health check:\n${postHealthResult}`);
    } else {
      results.push("\n=== Step 4: Dry Run - Skipping Deployment ===");
    }

    return results.join("\n");
  }

  /**
   * Deploy just the observability stack
   */
  @func()
  async deployObservability(
    ansibleDir: Directory,
    sshKey: Secret,
    host: string = "security.hetzner"
  ): Promise<string> {
    const bonneagar = new Bonneagar(ansibleDir);

    return bonneagar.runPlaybook(
      "playbooks/deploy-infrastructure.yml",
      "inventory/hosts.yml",
      undefined,
      "observability",
      host
    );
  }

  /**
   * Deploy storage stack (PostgreSQL, DuckDB, LanceDB)
   */
  @func()
  async deployStorage(
    ansibleDir: Directory,
    sshKey: Secret,
    host: string = "security.hetzner"
  ): Promise<string> {
    const bonneagar = new Bonneagar(ansibleDir);

    return bonneagar.runPlaybook(
      "playbooks/deploy-infrastructure.yml",
      "inventory/hosts.yml",
      undefined,
      "storage",
      host
    );
  }

  /**
   * Full Hetzner deployment
   */
  @func()
  async deployHetzner(
    ansibleDir: Directory,
    sshKey: Secret,
    domain: string = "baile.ie"
  ): Promise<string> {
    const results: string[] = [];
    const bonneagar = new Bonneagar(ansibleDir);

    // Deploy 1Password Connect first
    results.push("=== Deploying 1Password Connect ===");
    const opResult = await bonneagar.runPlaybook(
      "playbooks/deploy-infrastructure.yml",
      "inventory/hosts.yml",
      undefined,
      "onepassword",
      "security.hetzner"
    );
    results.push(opResult);

    // Deploy Pangolin
    results.push("\n=== Deploying Pangolin ===");
    const pangolinResult = await bonneagar.deployPangolin(
      "security.hetzner",
      sshKey,
      domain
    );
    results.push(pangolinResult);

    // Deploy Komodo
    results.push("\n=== Deploying Komodo ===");
    const komodoResult = await bonneagar.deployKomodo(
      "security.hetzner",
      sshKey
    );
    results.push(komodoResult);

    return results.join("\n");
  }

  /**
   * Deploy periphery agents to all managed hosts
   */
  @func()
  async deployAllPeriphery(
    ansibleDir: Directory,
    sshKey: Secret
  ): Promise<string> {
    const bonneagar = new Bonneagar(ansibleDir);

    return bonneagar.deployPeriphery(
      "komodo",  // All hosts in komodo group
      sshKey
    );
  }

  // =========================================================================
  // Polyglot CI Functions
  // =========================================================================

  /**
   * Run full CI pipeline (Python + TypeScript + Rust)
   */
  @func()
  async ci(source: Directory): Promise<string> {
    const results: string[] = [];
    const python = new Python();
    const typescript = new TypeScript();
    const rust = new Rust();

    // Python checks
    results.push("=== Python CI ===");
    try {
      const pythonResult = await python.check(source, ".");
      results.push(pythonResult);
    } catch (e) {
      results.push(`Python CI failed: ${e}`);
    }

    // TypeScript checks
    results.push("\n=== TypeScript CI ===");
    try {
      const tsResult = await typescript.check(source);
      results.push(tsResult);
    } catch (e) {
      results.push(`TypeScript CI failed: ${e}`);
    }

    // Rust checks (Locket)
    results.push("\n=== Rust CI ===");
    try {
      const rustResult = await rust.check(source, "bonneagar/locket");
      results.push(rustResult);
    } catch (e) {
      results.push(`Rust CI failed: ${e}`);
    }

    return results.join("\n");
  }

  /**
   * Test all Python projects
   */
  @func()
  async testPython(source: Directory): Promise<string> {
    const python = new Python();
    return python.testAll(source);
  }

  /**
   * Test TypeScript projects
   */
  @func()
  async testTypescript(source: Directory): Promise<string> {
    const typescript = new TypeScript();
    return typescript.check(source);
  }

  /**
   * Test Rust projects
   */
  @func()
  async testRust(source: Directory): Promise<string> {
    const rust = new Rust();
    return rust.check(source, "bonneagar/locket");
  }

  /**
   * Build and deploy docs to Cloudflare Pages
   */
  @func()
  async deployCloudflare(
    source: Directory,
    apiToken: Secret,
    accountId: string
  ): Promise<string> {
    const cloudflare = new Cloudflare();
    return cloudflare.deployDocs(source, apiToken, accountId);
  }

  /**
   * Build all projects
   */
  @func()
  async buildAll(source: Directory): Promise<string> {
    const results: string[] = [];
    const typescript = new TypeScript();
    const rust = new Rust();

    // Build TypeScript
    results.push("=== Building TypeScript ===");
    try {
      const tsResult = await typescript.build(source);
      results.push(tsResult || "Build successful");
    } catch (e) {
      results.push(`TypeScript build failed: ${e}`);
    }

    // Build Rust
    results.push("\n=== Building Rust ===");
    try {
      const rustResult = await rust.build(source, "bonneagar/locket", true);
      results.push(rustResult || "Build successful");
    } catch (e) {
      results.push(`Rust build failed: ${e}`);
    }

    // Build Docs
    results.push("\n=== Building Documentation ===");
    try {
      await typescript.buildDocs(source);
      results.push("Docs build successful");
    } catch (e) {
      results.push(`Docs build failed: ${e}`);
    }

    return results.join("\n");
  }

  /**
   * Run tests for all languages
   */
  @func()
  async testAll(source: Directory): Promise<string> {
    const results: string[] = [];

    results.push("=== Python Tests ===");
    results.push(await this.testPython(source));

    results.push("\n=== TypeScript Tests ===");
    results.push(await this.testTypescript(source));

    results.push("\n=== Rust Tests ===");
    results.push(await this.testRust(source));

    return results.join("\n");
  }

  // =========================================================================
  // App-Specific Testing Functions
  // =========================================================================

  /**
   * Test a specific TypeScript/Bun app
   */
  @func()
  async testTypescriptApp(
    source: Directory,
    appName: string
  ): Promise<string> {
    const app = APP_CONFIGS[appName];
    if (!app) {
      throw new Error("Unknown app: " + appName);
    }

    if (app.runtime !== "bun") {
      throw new Error("App " + appName + " is not a TypeScript/Bun app");
    }

    const container = dag
      .container()
      .from("oven/bun:latest")
      .withMountedCache("/root/.bun/install/cache", dag.cacheVolume("bun-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + app.path);

    const results: string[] = ["Testing " + appName + " (" + app.path + "):", ""];

    // Install dependencies
    let testContainer = container.withExec(["bun", "install"]);

    // Run typecheck if available
    results.push("=== Typecheck ===");
    try {
      const typecheckOutput = await testContainer
        .withExec(["bun", "run", "typecheck"])
        .stdout();
      results.push(typecheckOutput || "Typecheck passed");
    } catch (e) {
      results.push("Typecheck failed: " + String(e));
    }

    // Run tests if test script exists
    results.push("\n=== Tests ===");
    try {
      const testOutput = await testContainer
        .withExec(["bun", "test"])
        .stdout();
      results.push(testOutput || "Tests passed");
    } catch (e) {
      results.push("Tests skipped or failed: " + String(e));
    }

    return results.join("\n");
  }

  /**
   * Test a specific Python app
   */
  @func()
  async testPythonApp(
    source: Directory,
    appName: string
  ): Promise<string> {
    const app = APP_CONFIGS[appName];
    if (!app) {
      throw new Error("Unknown app: " + appName);
    }

    if (app.runtime !== "uv") {
      throw new Error("App " + appName + " is not a Python app");
    }

    const container = dag
      .container()
      .from("ghcr.io/astral-sh/uv:python3.12-bookworm")
      .withEnvVariable("UV_SYSTEM_PYTHON", "1")
      .withMountedCache("/root/.cache/uv", dag.cacheVolume("uv-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + app.path);

    const results: string[] = ["Testing " + appName + " (" + app.path + "):", ""];

    // Install dependencies
    let testContainer = container.withExec(["uv", "sync"]);

    // Run pytest
    results.push("=== Tests ===");
    try {
      const testOutput = await testContainer
        .withExec(["uv", "run", "pytest", "-v"])
        .stdout();
      results.push(testOutput || "Tests passed");
    } catch (e) {
      results.push("Tests failed: " + String(e));
    }

    // Run pyright
    results.push("\n=== Type Check ===");
    try {
      const typecheckOutput = await testContainer
        .withExec(["uv", "run", "pyright", "."])
        .stdout();
      results.push(typecheckOutput || "Typecheck passed");
    } catch (e) {
      results.push("Typecheck skipped or failed: " + String(e));
    }

    return results.join("\n");
  }

  /**
   * Test all apps in the monorepo
   */
  @func()
  async testApps(
    source: Directory,
    appNamesJson?: string
  ): Promise<string> {
    const appNames = appNamesJson
      ? JSON.parse(appNamesJson) as string[]
      : Object.keys(APP_CONFIGS);

    const results: string[] = ["Testing " + appNames.length + " apps:", ""];

    for (const appName of appNames) {
      const app = APP_CONFIGS[appName];
      if (!app) continue;

      results.push("\n" + "=".repeat(50));
      results.push(appName.toUpperCase());
      results.push("=".repeat(50));

      try {
        if (app.runtime === "bun") {
          results.push(await this.testTypescriptApp(source, appName));
        } else if (app.runtime === "uv") {
          results.push(await this.testPythonApp(source, appName));
        } else {
          results.push("Skipping: unsupported runtime " + app.runtime);
        }
      } catch (e) {
        results.push("FAILED: " + String(e));
      }
    }

    return results.join("\n");
  }

  /**
   * Run integration test: start backend and test frontend against it
   */
  @func()
  async integrationTest(
    source: Directory,
    frontendApp: string,
    backendService: string
  ): Promise<string> {
    const frontend = APP_CONFIGS[frontendApp];
    const backend = APP_CONFIGS[backendService];

    if (!frontend || !backend) {
      throw new Error("Unknown app(s): " + frontendApp + ", " + backendService);
    }

    const results: string[] = [
      "Integration Test: " + frontendApp + " -> " + backendService,
      ""
    ];

    // Start backend service
    results.push("=== Starting Backend Service ===");
    let backendContainer = dag
      .container()
      .from("ghcr.io/astral-sh/uv:python3.12-bookworm")
      .withEnvVariable("UV_SYSTEM_PYTHON", "1")
      .withMountedCache("/root/.cache/uv", dag.cacheVolume("uv-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + backend.path)
      .withExec(["uv", "sync"])
      .withExposedPort(backend.defaultPort);

    const backendSvc = backendContainer
      .withExec(backend.devCommand)
      .asService();

    // Run frontend tests with backend binding
    results.push("=== Running Frontend Tests ===");
    const frontendContainer = dag
      .container()
      .from("oven/bun:latest")
      .withMountedCache("/root/.bun/install/cache", dag.cacheVolume("bun-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + frontend.path)
      .withServiceBinding("backend", backendSvc)
      .withEnvVariable("API_URL", "http://backend:" + backend.defaultPort)
      .withExec(["bun", "install"]);

    try {
      const testOutput = await frontendContainer
        .withExec(["bun", "test"])
        .stdout();
      results.push(testOutput || "Integration tests passed");
    } catch (e) {
      results.push("Integration tests failed: " + String(e));
    }

    return results.join("\n");
  }

  /**
   * Build Docker images for all apps
   */
  @func()
  async buildImages(
    source: Directory,
    registry: string = "ghcr.io/cianfhoghlaim",
    tag: string = "latest"
  ): Promise<string> {
    const results: string[] = ["Building Docker images:", ""];

    for (const [appName, app] of Object.entries(APP_CONFIGS)) {
      if (app.type === "backend") continue; // Skip for now

      results.push("\n=== " + appName + " ===");

      let container: Container;

      if (app.runtime === "bun") {
        container = dag
          .container()
          .from("oven/bun:latest")
          .withMountedCache("/root/.bun/install/cache", dag.cacheVolume("bun-cache"))
          .withDirectory("/app", source.directory(app.path))
          .withWorkdir("/app")
          .withExec(["bun", "install", "--production"])
          .withExec(["bun", "run", "build"])
          .withEntrypoint(["bun", "run", "start"]);
      } else if (app.runtime === "uv") {
        container = dag
          .container()
          .from("ghcr.io/astral-sh/uv:python3.12-bookworm-slim")
          .withEnvVariable("UV_SYSTEM_PYTHON", "1")
          .withMountedCache("/root/.cache/uv", dag.cacheVolume("uv-cache"))
          .withDirectory("/app", source.directory(app.path))
          .withWorkdir("/app")
          .withExec(["uv", "sync", "--no-dev"])
          .withEntrypoint(["uv", "run"]);
      } else {
        results.push("Skipping: unsupported runtime");
        continue;
      }

      const imageRef = registry + "/" + appName + ":" + tag;
      try {
        const address = await container.publish(imageRef);
        results.push("Published: " + address);
      } catch (e) {
        results.push("Failed to publish: " + String(e));
      }
    }

    return results.join("\n");
  }

  /**
   * List all apps and their test status
   */
  @func()
  listApps(): string {
    const lines: string[] = ["Available Apps for Testing:", ""];

    for (const [name, config] of Object.entries(APP_CONFIGS)) {
      lines.push("  " + name + " (" + config.runtime + ") - " + config.path);
    }

    return lines.join("\n");
  }
}
