/**
 * Tenant Configuration Loader
 * Loads tenant configs from YAML files at runtime
 */

import { parse } from "yaml";
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import type { TenantConfig, TenantClientContext } from "@/types/tenant";
import { hostnameToTenant } from "@/types/tenant";

// Cache for loaded configs
const configCache = new Map<string, TenantConfig>();

/**
 * Get the path to tenant config files
 */
function getConfigPath(tenantId: string): string {
  // Resolve from project root
  const projectRoot = process.env.PROJECT_ROOT || process.cwd();
  return join(projectRoot, "config", "tenants", `${tenantId}.yaml`);
}

/**
 * Load tenant config from YAML file
 */
export function loadTenantConfig(tenantId: string): TenantConfig {
  // Check cache first
  if (configCache.has(tenantId)) {
    return configCache.get(tenantId)!;
  }

  const configPath = getConfigPath(tenantId);

  if (!existsSync(configPath)) {
    throw new Error(`Tenant config not found: ${tenantId} at ${configPath}`);
  }

  try {
    const yamlContent = readFileSync(configPath, "utf-8");
    const config = parse(yamlContent) as TenantConfig;

    // Validate required fields
    if (!config.tenant?.id || !config.theme || !config.routes) {
      throw new Error(`Invalid tenant config: missing required fields`);
    }

    // Cache the config
    configCache.set(tenantId, config);

    return config;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load tenant config ${tenantId}: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Get tenant config from request headers or hostname
 */
export function getTenantFromRequest(request: Request): string {
  // First check X-Tenant-ID header (set by Traefik middleware)
  const headerTenant = request.headers.get("x-tenant-id");
  if (headerTenant) {
    return headerTenant;
  }

  // Fall back to hostname mapping
  const url = new URL(request.url);
  return hostnameToTenant(url.host);
}

/**
 * Get tenant config for a request
 */
export function getTenantConfigFromRequest(request: Request): TenantConfig {
  const tenantId = getTenantFromRequest(request);
  return loadTenantConfig(tenantId);
}

/**
 * Clear the config cache (useful for hot reload in development)
 */
export function clearConfigCache(): void {
  configCache.clear();
}

/**
 * List all available tenant IDs
 */
export function listTenants(): string[] {
  const projectRoot = process.env.PROJECT_ROOT || process.cwd();
  const tenantsDir = join(projectRoot, "config", "tenants");

  try {
    const { readdirSync } = require("fs");
    const files = readdirSync(tenantsDir) as string[];
    return files
      .filter((f: string) => f.endsWith(".yaml"))
      .map((f: string) => f.replace(".yaml", ""));
  } catch {
    return [];
  }
}
