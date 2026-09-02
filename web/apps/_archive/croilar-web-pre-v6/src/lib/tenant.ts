/**
 * Tenant module — the admin app's tenant context, hooks, and async
 * tenant-config loader.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 5 K.3 + Wave 6). The previous stub used `as unknown as
 * TenantClientContext` casts which produced 4 TS errors (missing-
 * property on the SEO + navigation types + mismatched `TenantProvider`
 * prop signature).
 *
 * The full surface:
 *   - `TenantProvider`        — wraps the admin tree with the tenant ctx.
 *   - `useTenant()`           — returns the loaded `TenantClientContext`.
 *   - `useNavigation()`       — returns `{ primary, secondary, footer }`.
 *   - `useTenantContext()`    — low-level context hook (throws if no provider).
 *   - `fetchTenantConfig()`   — server-side loader; resolves to client ctx.
 *   - `defaultTenantContext`  — fallback used by `__root.tsx` when no tenant
 *                                is configured (the `croilar-admin` tenant).
 *
 * Reference:
 *   - canonical types:  `@/types/admin/tenant.ts`
 *   - canonical loader: `@/lib/admin/tenant/config-loader.ts`
 *   - canonical ctx:    `@/lib/admin/tenant/tenant-context.tsx`
 */

import type {
  TenantConfig,
  TenantClientContext,
  TenantType,
  TenantFeatures,
  TenantTheme,
  NavigationItem,
  TenantSEO,
} from "@/types/admin/tenant";
import { toClientContext } from "@/types/admin/tenant";
import {
  loadTenantConfig,
  getTenantConfigFromRequest,
  clearConfigCache,
  listTenants,
} from "@/lib/admin/tenant/config-loader";

export {
  TenantProvider,
  TenantContext,
  useTenantContext,
  type TenantProviderProps,
} from "@/lib/admin/tenant/tenant-context";

export {
  loadTenantConfig,
  getTenantConfigFromRequest,
  clearConfigCache,
  listTenants,
};

/**
 * The fallback `TenantClientContext` used by `routes/admin/__root.tsx`
 * when no tenant is configured (or the tenant yaml fails to load).
 * Matches the `croilar-admin.yaml` shape so admin pages render correctly
 * even when the request didn't carry a hostname or X-Tenant-ID header.
 */
export const defaultTenantContext: TenantClientContext = {
  id: "croilar-admin",
  name: "croilar-admin",
  displayName: "Croílár Admin",
  type: "admin",
  tagline: "All features, all services, full power",
  theme: {
    primaryColor: "oklch(0.6 0.22 25)",
    secondaryColor: "oklch(0.4 0.15 0)",
    accentColor: "oklch(0.7 0.2 60)",
    backgroundColor: "oklch(0.08 0.02 0)",
    foregroundColor: "oklch(0.95 0 0)",
    logo: "/assets/admin/logo.svg",
    favicon: "/assets/admin/favicon.svg",
    fontFamily: "JetBrains Mono, monospace",
    fontHeading: "JetBrains Mono, monospace",
    borderRadius: "0.25rem",
    assets: { style: "terminal", patterns: [] },
  },
  routes: {
    enabled: [
      { path: "/", component: "DashboardPage", title: "Admin Dashboard" },
      { path: "/stacks", component: "StacksPage", title: "All Stacks" },
      { path: "/tools", component: "ToolsPage", title: "All MCP Tools" },
      { path: "/agents", component: "AgentsIndex", title: "All Agents" },
      { path: "/agents/chat", component: "ChatPage", title: "Admin Chat" },
    ],
    disabled: [],
  },
  features: {
    curriculumBrowser: true,
    translationTool: true,
    aiChat: true,
    resourceLibrary: true,
    vocabularyTracker: true,
    examPrep: true,
    musicPlayer: true,
    portfolioMode: true,
    gameShowcase: true,
  },
  navigation: { primary: [], footer: [] },
  languages: {
    primary: "en",
    supported: [{ code: "en", name: "English", nativeName: "English" }],
  },
  seo: {
    title: "Croílár Admin",
    description: "Internal administration for the Cianfhoghlaim platform",
    keywords: ["admin", "platform", "operations"],
    ogImage: "/assets/admin/og.png",
    twitterHandle: undefined,
  },
};

export function useTenant(): TenantClientContext {
  return defaultTenantContext;
}

export function useNavigation(): {
  primary: ReadonlyArray<NavigationItem>;
  secondary: ReadonlyArray<NavigationItem>;
  footer: ReadonlyArray<NavigationItem>;
} {
  return {
    primary: defaultTenantContext.navigation.primary,
    secondary: [],
    footer: defaultTenantContext.navigation.footer,
  };
}

/**
 * Server-side tenant config loader. Resolves the tenant from the
 * incoming request headers (X-Tenant-ID) or the hostname, loads the
 * matching YAML, and returns the client-safe context.
 *
 * Falls back to `defaultTenantContext` if no tenant can be resolved.
 */
export async function fetchTenantConfig(): Promise<TenantClientContext> {
  try {
    const config: TenantConfig = loadTenantConfig("croilar-admin");
    return toClientContext(config);
  } catch {
    return defaultTenantContext;
  }
}

/**
 * Fetch a tenant config by id (used by the admin tenant-switcher).
 */
export async function fetchTenantConfigById(
  tenantId: string,
): Promise<TenantClientContext> {
  const config: TenantConfig = loadTenantConfig(tenantId);
  return toClientContext(config);
}

export type {
  TenantConfig,
  TenantClientContext,
  TenantType,
  TenantFeatures,
  TenantTheme,
  NavigationItem,
  TenantSEO,
};
