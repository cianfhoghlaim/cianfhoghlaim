/**
 * Sruth App Registry Module
 *
 * Defines all sruth monorepo apps with their configurations
 * for unified dev environment orchestration.
 */

import { object, func, field } from "@dagger.io/dagger";

export interface AppConfig {
  name: string;
  path: string;
  type: "frontend" | "backend" | "fullstack";
  runtime: "bun" | "uv" | "node";
  defaultPort: number;
  healthEndpoint: string;
  envFile: string;
  dependencies: string[];
  requiresAuth: boolean;
  devCommand: string[];
}

/**
 * App configurations for all sruth apps
 */
export const APP_CONFIGS: Record<string, AppConfig> = {
  aleyum: {
    name: "aleyum",
    path: "sruth/aleyum",
    type: "frontend",
    runtime: "bun",
    defaultPort: 3003,
    healthEndpoint: "/",
    envFile: ".env.example",
    dependencies: [],
    requiresAuth: false,
    devCommand: ["bun", "dev"],
  },
  "aleyum-portal": {
    name: "aleyum-portal",
    path: "sruth/aleyum/portal",
    type: "fullstack",
    runtime: "bun",
    defaultPort: 3001,
    healthEndpoint: "/api/health",
    envFile: ".env.example",
    dependencies: ["postgres"],
    requiresAuth: true,
    devCommand: ["bun", "dev"],
  },
  crypteolas: {
    name: "crypteolas",
    path: "sruth/crypteolas/ui",
    type: "frontend",
    runtime: "bun",
    defaultPort: 3002,
    healthEndpoint: "/",
    envFile: "../.env.example",
    dependencies: [],
    requiresAuth: true,
    devCommand: ["bun", "dev"],
  },
  tuath: {
    name: "tuath",
    path: "sruth/tuath/ui",
    type: "frontend",
    runtime: "bun",
    defaultPort: 3004,
    healthEndpoint: "/",
    envFile: "../.env.example",
    dependencies: [],
    requiresAuth: true,
    devCommand: ["bun", "dev"],
  },
  "oideachais-api": {
    name: "oideachais-api",
    path: "sruth/oideachais",
    type: "backend",
    runtime: "uv",
    defaultPort: 8000,
    healthEndpoint: "/health",
    envFile: ".env.local.example",
    dependencies: [],
    requiresAuth: false,
    devCommand: ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
  },
  "oideachais-web": {
    name: "oideachais-web",
    path: "sruth/oideachais/apps/web",
    type: "frontend",
    runtime: "bun",
    defaultPort: 3005,
    healthEndpoint: "/",
    envFile: "../../.env.local.example",
    dependencies: ["oideachais-api"],
    requiresAuth: true,
    devCommand: ["bun", "dev"],
  },
};

export interface PortAllocation {
  app: string;
  port: number;
  type: "frontend" | "backend" | "api";
}

@object()
export class AppRegistry {
  /**
   * Get configuration for a specific app
   */
  @func()
  getApp(name: string): AppConfig | undefined {
    return APP_CONFIGS[name];
  }

  /**
   * Get all app configurations
   */
  @func()
  getAllApps(): AppConfig[] {
    return Object.values(APP_CONFIGS);
  }

  /**
   * Get apps filtered by type
   */
  @func()
  getAppsByType(type: "frontend" | "backend" | "fullstack"): AppConfig[] {
    return this.getAllApps().filter((app) => app.type === type);
  }

  /**
   * Get apps filtered by runtime
   */
  @func()
  getAppsByRuntime(runtime: "bun" | "uv" | "node"): AppConfig[] {
    return this.getAllApps().filter((app) => app.runtime === runtime);
  }

  /**
   * Get apps that require authentication
   */
  @func()
  getAppsRequiringAuth(): AppConfig[] {
    return this.getAllApps().filter((app) => app.requiresAuth);
  }

  /**
   * Get all app names
   */
  @func()
  getAppNames(): string[] {
    return Object.keys(APP_CONFIGS);
  }

  /**
   * Allocate ports dynamically to avoid conflicts
   * Uses app's defaultPort if available, otherwise increments from base
   */
  @func()
  allocatePorts(appNames: string[]): PortAllocation[] {
    const allocations: PortAllocation[] = [];
    const usedPorts = new Set<number>();

    for (const name of appNames) {
      const app = this.getApp(name);
      if (!app) continue;

      let port = app.defaultPort;
      while (usedPorts.has(port)) {
        port++;
      }
      usedPorts.add(port);

      allocations.push({
        app: name,
        port,
        type: app.type === "backend" ? "api" : "frontend",
      });
    }

    return allocations;
  }

  /**
   * Get dependency order for starting apps
   * Returns apps in order where dependencies come first
   */
  @func()
  getDependencyOrder(appNames: string[]): string[] {
    const ordered: string[] = [];
    const remaining = new Set(appNames);

    // Keep processing until all apps are ordered
    while (remaining.size > 0) {
      let addedAny = false;

      for (const name of remaining) {
        const app = this.getApp(name);
        if (!app) {
          remaining.delete(name);
          continue;
        }

        // Check if all dependencies are already ordered
        const depsResolved = app.dependencies.every(
          (dep) => ordered.includes(dep) || !appNames.includes(dep)
        );

        if (depsResolved) {
          ordered.push(name);
          remaining.delete(name);
          addedAny = true;
        }
      }

      // If no progress, we have a circular dependency - just add remaining
      if (!addedAny) {
        for (const name of remaining) {
          ordered.push(name);
        }
        break;
      }
    }

    return ordered;
  }
}
