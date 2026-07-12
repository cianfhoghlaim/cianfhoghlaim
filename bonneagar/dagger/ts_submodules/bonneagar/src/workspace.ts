/**
 * Workspace Orchestration Module
 *
 * Single command to start development environment with all apps.
 */

import {
  dag,
  Container,
  Directory,
  Service,
  Secret,
  object,
  func,
} from "@dagger.io/dagger";

import { AppRegistry, APP_CONFIGS, AppConfig, PortAllocation } from "./apps.js";
import { SecretsManager } from "./secrets.js";
import { ServiceOrchestrator } from "./services.js";

@object()
export class Workspace {
  private registry: AppRegistry;
  private secrets: SecretsManager;
  private services: ServiceOrchestrator;

  constructor() {
    this.registry = new AppRegistry();
    this.secrets = new SecretsManager();
    this.services = new ServiceOrchestrator();
  }

  /**
   * Create a Bun container for frontend apps
   */
  private bunContainer(source: Directory, appPath: string): Container {
    return dag
      .container()
      .from("oven/bun:latest")
      .withMountedCache("/root/.bun/install/cache", dag.cacheVolume("bun-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + appPath);
  }

  /**
   * Create a uv container for Python apps
   */
  private uvContainer(source: Directory, appPath: string): Container {
    return dag
      .container()
      .from("ghcr.io/astral-sh/uv:python3.12-bookworm")
      .withEnvVariable("UV_SYSTEM_PYTHON", "1")
      .withMountedCache("/root/.cache/uv", dag.cacheVolume("uv-cache"))
      .withDirectory("/src", source)
      .withWorkdir("/src/" + appPath);
  }

  /**
   * Start a single app as a service
   */
  @func()
  async startApp(
    source: Directory,
    appName: string,
    opToken?: Secret,
    connectHost?: string
  ): Promise<Service> {
    const app = APP_CONFIGS[appName];
    if (!app) {
      throw new Error("Unknown app: " + appName + ". Available: " + Object.keys(APP_CONFIGS).join(", "));
    }

    // Create base container based on runtime
    let container: Container;
    if (app.runtime === "bun") {
      container = this.bunContainer(source, app.path);
    } else if (app.runtime === "uv") {
      container = this.uvContainer(source, app.path);
    } else {
      container = dag.container().from("node:22-slim")
        .withDirectory("/src", source)
        .withWorkdir("/src/" + app.path);
    }

    // Start infrastructure dependencies
    for (const dep of app.dependencies) {
      if (dep === "postgres") {
        const postgres = this.services.createPostgres(appName.replace(/-/g, "_"));
        container = container.withServiceBinding("postgres", postgres);
      } else if (dep === "redis" || dep === "dragonfly") {
        const redis = this.services.createRedis();
        container = container.withServiceBinding("redis", redis);
      }
    }

    // Load secrets if 1Password is configured
    if (opToken && connectHost && app.requiresAuth) {
      container = await this.secrets.applySecretsToContainer(
        container,
        opToken,
        connectHost,
        appName
      );
    }

    // Set port environment variable
    container = container.withEnvVariable("PORT", String(app.defaultPort));

    // Install dependencies and start
    if (app.runtime === "bun") {
      container = container
        .withExec(["bun", "install"])
        .withExposedPort(app.defaultPort);
      
      // Start dev server
      container = container.withExec(app.devCommand);
    } else if (app.runtime === "uv") {
      container = container
        .withExec(["uv", "sync"])
        .withExposedPort(app.defaultPort);
      
      container = container.withExec(app.devCommand);
    }

    return container.asService();
  }

  /**
   * Start multiple apps with coordinated ports
   */
  @func()
  async startApps(
    source: Directory,
    appNamesJson: string,
    opToken?: Secret,
    connectHost?: string
  ): Promise<string> {
    const appNames = JSON.parse(appNamesJson) as string[];
    const allocations = this.registry.allocatePorts(appNames);
    const orderedApps = this.registry.getDependencyOrder(appNames);
    
    const results: string[] = ["Starting apps in dependency order:"];

    for (const appName of orderedApps) {
      const allocation = allocations.find(a => a.app === appName);
      if (!allocation) continue;

      try {
        await this.startApp(source, appName, opToken, connectHost);
        results.push("  " + appName + ": http://localhost:" + allocation.port + " [OK]");
      } catch (e) {
        results.push("  " + appName + ": FAILED - " + String(e));
      }
    }

    return results.join("\n");
  }

  /**
   * Start the full development environment
   */
  @func()
  async devAll(
    source: Directory,
    opToken?: Secret,
    connectHost?: string
  ): Promise<string> {
    const allApps = Object.keys(APP_CONFIGS);
    return this.startApps(source, JSON.stringify(allApps), opToken, connectHost);
  }

  /**
   * Start only frontend apps
   */
  @func()
  async devFrontends(
    source: Directory,
    opToken?: Secret,
    connectHost?: string
  ): Promise<string> {
    const frontendApps = this.registry.getAppsByType("frontend").map(a => a.name);
    return this.startApps(source, JSON.stringify(frontendApps), opToken, connectHost);
  }

  /**
   * Start only backend apps
   */
  @func()
  async devBackends(
    source: Directory,
    opToken?: Secret,
    connectHost?: string
  ): Promise<string> {
    const backendApps = this.registry.getAppsByType("backend").map(a => a.name);
    return this.startApps(source, JSON.stringify(backendApps), opToken, connectHost);
  }

  /**
   * Get port allocations for apps
   */
  @func()
  getPorts(appNamesJson?: string): string {
    const appNames = appNamesJson 
      ? JSON.parse(appNamesJson) as string[]
      : Object.keys(APP_CONFIGS);
    
    const allocations = this.registry.allocatePorts(appNames);
    
    const lines = ["Port Allocations:", ""];
    for (const alloc of allocations) {
      lines.push("  " + alloc.app + ": " + alloc.port + " (" + alloc.type + ")");
    }
    
    return lines.join("\n");
  }

  /**
   * List all available apps
   */
  @func()
  listApps(): string {
    const lines = ["Available Apps:", ""];
    
    for (const [name, config] of Object.entries(APP_CONFIGS)) {
      const auth = config.requiresAuth ? "[AUTH]" : "";
      lines.push("  " + name + " (" + config.runtime + ") - port " + config.defaultPort + " " + auth);
    }
    
    return lines.join("\n");
  }

  /**
   * Check if all required secrets are configured
   */
  @func()
  async validateSecrets(
    opToken: Secret,
    connectHost: string,
    appNamesJson?: string
  ): Promise<string> {
    const appNames = appNamesJson 
      ? JSON.parse(appNamesJson) as string[]
      : this.registry.getAppsRequiringAuth().map(a => a.name);
    
    const results: string[] = ["Secret Validation:", ""];
    
    for (const appName of appNames) {
      const validation = await this.secrets.validateSecrets(opToken, connectHost, appName);
      if (validation.valid) {
        results.push("  " + appName + ": OK");
      } else {
        results.push("  " + appName + ": MISSING - " + validation.missing.join(", "));
      }
    }
    
    return results.join("\n");
  }
}
