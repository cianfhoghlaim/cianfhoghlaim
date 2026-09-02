/**
 * Re-export module for `@/types/tenant` (the legacy short alias).
 *
 * The canonical tenant types live at `./admin/tenant.ts` (the path
 * created by the 2026-08-13 tenant rename). The short alias is
 * preserved for the 4 components that import from `@/types/tenant`.
 */

export type {
  TenantConfig,
  TenantClientContext,
  TenantType,
  TenantFeatures,
  TenantTheme,
  NavigationItem,
} from "./admin/tenant";

export function hostnameToTenant(_hostname: string): string {
  return "default";
}
