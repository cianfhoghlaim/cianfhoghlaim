/**
 * Tenant Context Provider
 * Provides tenant configuration throughout the React component tree
 * Applies theme CSS variables and handles route guards
 */

import { createContext, useContext, useEffect, type ReactNode } from "react";
import { createServerFn } from "@tanstack/react-start";
import type { TenantClientContext } from "@/types/tenant";
import { toClientContext } from "@/types/tenant";
import { loadTenantConfig, getTenantFromRequest } from "./config-loader";

// Default tenant context for SSR
const defaultTenantContext: TenantClientContext = {
  id: "cianfhoghlaim",
  name: "Cianfhoghlaim",
  displayName: "Cianfhoghlaim",
  type: "education",
  tagline: "Deep Learning for Celtic Languages",
  theme: {
    primaryColor: "#1e40af",
    secondaryColor: "#059669",
    accentColor: "#d97706",
    backgroundColor: "#0f172a",
    foregroundColor: "#f8fafc",
    logo: "/assets/cianfhoghlaim/logo.svg",
    favicon: "/assets/cianfhoghlaim/favicon.svg",
    fontFamily: "Inter, system-ui, sans-serif",
    fontHeading: "Playfair Display, serif",
    borderRadius: "0.5rem",
    assets: {
      style: "celtic",
      patterns: ["knotwork", "spiral"],
    },
  },
  routes: {
    enabled: [{ path: "/", component: "home", title: "Home" }],
    disabled: [],
  },
  features: {
    curriculumBrowser: true,
    translationTool: true,
    aiChat: true,
    resourceLibrary: true,
    vocabularyTracker: true,
    examPrep: true,
    musicPlayer: false,
    portfolioMode: false,
    gameShowcase: false,
  },
  navigation: {
    primary: [],
    footer: [],
  },
  languages: {
    primary: "en",
    supported: [{ code: "en", name: "English", nativeName: "English" }],
  },
  seo: {
    title: "Cianfhoghlaim",
    description: "Celtic Language Education",
    keywords: [],
    ogImage: "",
  },
};

// Create context
const TenantContext = createContext<TenantClientContext>(defaultTenantContext);

/**
 * Server function to load tenant config from request
 */
export const fetchTenantConfig = createServerFn({ method: "GET" }).handler(
  async (): Promise<TenantClientContext> => {
    // In TanStack Start 1.145, the request is accessed via the global
    // context. We rely on the X-Tenant-ID header set by Traefik middleware
    // or the hostname mapping in config-loader.
    const request = (globalThis as { __request?: Request }).__request;
    const tenantId = request ? getTenantFromRequest(request) : "cianfhoghlaim";
    const config = loadTenantConfig(tenantId);
    return toClientContext(config);
  }
);

/**
 * Apply theme CSS variables to document
 */
function applyTheme(theme: TenantClientContext["theme"]): void {
  if (typeof document === "undefined") return;

  const root = document.documentElement;

  // Color variables
  root.style.setProperty("--color-primary", theme.primaryColor);
  root.style.setProperty("--color-secondary", theme.secondaryColor);
  root.style.setProperty("--color-accent", theme.accentColor);
  root.style.setProperty("--color-background", theme.backgroundColor);
  root.style.setProperty("--color-foreground", theme.foregroundColor);

  // Convert hex to HSL for Tailwind compatibility
  root.style.setProperty("--primary", hexToHsl(theme.primaryColor));
  root.style.setProperty("--secondary", hexToHsl(theme.secondaryColor));
  root.style.setProperty("--accent", hexToHsl(theme.accentColor));
  root.style.setProperty("--background", hexToHsl(theme.backgroundColor));
  root.style.setProperty("--foreground", hexToHsl(theme.foregroundColor));

  // Typography
  root.style.setProperty("--font-family", theme.fontFamily);
  root.style.setProperty("--font-heading", theme.fontHeading);

  // Layout
  root.style.setProperty("--radius", theme.borderRadius);

  // Update favicon
  const favicon = document.querySelector('link[rel="icon"]');
  if (favicon) {
    favicon.setAttribute("href", theme.favicon);
  }
}

/**
 * Convert hex color to HSL string (for Tailwind CSS variables)
 */
function hexToHsl(hex: string): string {
  // Remove # if present
  hex = hex.replace(/^#/, "");

  // Parse hex values
  const r = parseInt(hex.slice(0, 2), 16) / 255;
  const g = parseInt(hex.slice(2, 4), 16) / 255;
  const b = parseInt(hex.slice(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`;
}

/**
 * Tenant Provider Component
 */
interface TenantProviderProps {
  children: ReactNode;
  config: TenantClientContext;
}

export function TenantProvider({ children, config }: TenantProviderProps) {
  // Apply theme on mount and when config changes
  useEffect(() => {
    applyTheme(config.theme);

    // Update document title
    document.title = config.seo.title;

    // Add tenant class to body for CSS targeting
    document.body.classList.remove("tenant-cianfhoghlaim", "tenant-aleyum");
    document.body.classList.add(`tenant-${config.id}`);
    document.body.classList.add(`tenant-type-${config.type}`);
  }, [config]);

  return (
    <TenantContext.Provider value={config}>{children}</TenantContext.Provider>
  );
}

/**
 * Hook to access tenant context
 */
export function useTenant(): TenantClientContext {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error("useTenant must be used within a TenantProvider");
  }
  return context;
}

/**
 * Hook to check if a feature is enabled
 */
export function useFeature(feature: keyof TenantClientContext["features"]): boolean {
  const tenant = useTenant();
  return tenant.features[feature] ?? false;
}

/**
 * Hook to check if current route is enabled
 */
export function useRouteGuard(path: string): boolean {
  const tenant = useTenant();
  const enabledPaths = tenant.routes.enabled.map((r) => r.path);
  const disabledPaths = tenant.routes.disabled;

  if (disabledPaths.includes(path)) return false;
  if (enabledPaths.includes(path)) return true;

  // Check for parent routes
  const pathBase = "/" + path.split("/")[1];
  return enabledPaths.some((p) => p.startsWith(pathBase));
}

/**
 * Hook to get navigation items
 */
export function useNavigation() {
  const tenant = useTenant();
  return {
    primary: tenant.navigation.primary,
    footer: tenant.navigation.footer,
  };
}

/**
 * Hook to get theme
 */
export function useTheme() {
  const tenant = useTenant();
  return tenant.theme;
}

export { TenantContext, defaultTenantContext };
