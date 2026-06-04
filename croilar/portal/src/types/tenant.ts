/**
 * Tenant Type Definitions
 * Shared types for multi-tenant configuration
 */

export type TenantType =
  | "education"
  | "portfolio"
  | "music"
  | "game"
  | "corporate";

export interface TenantTheme {
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  backgroundColor: string;
  foregroundColor: string;
  logo: string;
  favicon: string;
  fontFamily: string;
  fontHeading: string;
  borderRadius: string;
  assets: {
    style: string;
    patterns: string[];
  };
}

export interface TenantFeatures {
  curriculumBrowser: boolean;
  translationTool: boolean;
  aiChat: boolean;
  resourceLibrary: boolean;
  vocabularyTracker: boolean;
  examPrep: boolean;
  musicPlayer: boolean;
  portfolioMode: boolean;
  gameShowcase: boolean;
  spotifyEmbed?: boolean;
  soundcloudEmbed?: boolean;
}

export interface NavigationItem {
  label: string;
  path: string;
  icon?: string;
}

export interface RouteConfig {
  path: string;
  component: string;
  title: string;
}

export interface TenantLanguage {
  code: string;
  name: string;
  nativeName: string;
}

export interface TenantSEO {
  title: string;
  description: string;
  keywords: string[];
  ogImage: string;
  twitterHandle?: string;
}

export interface TenantOwner {
  name: string;
  title: string;
  email: string;
  github?: string;
  spotify?: string;
  soundcloud?: string;
  youtube?: string;
}

export interface TenantConfig {
  tenant: {
    id: string;
    name: string;
    displayName: string;
    domains: string[];
    type: TenantType;
    description: string;
    tagline: string;
  };
  owner?: TenantOwner;
  theme: TenantTheme;
  routes: {
    enabled: RouteConfig[];
    disabled: string[];
  };
  features: TenantFeatures;
  navigation: {
    primary: NavigationItem[];
    footer: NavigationItem[];
  };
  languages: {
    primary: string;
    supported: TenantLanguage[];
  };
  dataSources?: {
    yaml: string[];
    database: string[];
    external: string[];
  };
  storage?: {
    duckdbPath: string;
    lancedbPath: string;
    assetsPath: string;
  };
  analytics?: {
    enabled: boolean;
    provider: string;
    siteId: string;
  };
  seo: TenantSEO;
}

/**
 * Client-side tenant context (subset of TenantConfig)
 */
export interface TenantClientContext {
  id: string;
  name: string;
  displayName: string;
  type: TenantType;
  tagline: string;
  theme: TenantTheme;
  routes: {
    enabled: RouteConfig[];
    disabled: string[];
  };
  features: TenantFeatures;
  navigation: {
    primary: NavigationItem[];
    footer: NavigationItem[];
  };
  languages: {
    primary: string;
    supported: TenantLanguage[];
  };
  seo: TenantSEO;
}

/**
 * Convert full TenantConfig to client-safe TenantClientContext
 */
export function toClientContext(config: TenantConfig): TenantClientContext {
  return {
    id: config.tenant.id,
    name: config.tenant.name,
    displayName: config.tenant.displayName,
    type: config.tenant.type,
    tagline: config.tenant.tagline,
    theme: config.theme,
    routes: config.routes,
    features: config.features,
    navigation: config.navigation,
    languages: config.languages,
    seo: config.seo,
  };
}

/**
 * Hostname to tenant ID mapping
 */
const hostnameMap: Record<string, string> = {
  "aleyum.cianfhoghlaim.ie": "aleyum",
  "cianfhoghlaim.ie": "cianfhoghlaim",
  "localhost:3001": "aleyum",
  "localhost:3002": "aleyum",
  "localhost:3003": "aleyum",
  "localhost:3000": "cianfhoghlaim",
};

/**
 * Get tenant ID from hostname
 */
export function hostnameToTenant(hostname: string): string {
  return hostnameMap[hostname] || "aleyum";
}
