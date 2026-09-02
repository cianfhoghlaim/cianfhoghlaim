/**
 * Tenant React Context — exposes the loaded `TenantClientContext` to all
 * admin pages + admin components.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 5 K.3 + Wave 6). The previous stub was a placeholder
 * `{ Provider: () => null }` that produced `unknown` types and broke
 * the 6 admin components that read tenant metadata.
 *
 * The context is populated by `<TenantProvider config={...}>` in
 * `routes/admin/__root.tsx`. The config is loaded server-side via
 * `fetchTenantConfig()` (which calls `loadTenantConfig()` from
 * `./config-loader.ts`) and passed in as the `config` prop.
 *
 * Reference:
 *   - tenant yaml configs: `croilar-web/config/tenants/*.yaml`
 *   - tenant types:        `@/types/admin/tenant.ts`
 *   - canonical loader:    `./config-loader.ts`
 */

import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { TenantClientContext } from "@/types/admin/tenant";

export const TenantContext = createContext<TenantClientContext | null>(null);

export interface TenantProviderProps {
  config: TenantClientContext;
  children: ReactNode;
}

export function TenantProvider({
  config,
  children,
}: TenantProviderProps): ReactNode {
  return (
    <TenantContext.Provider value={config}>{children}</TenantContext.Provider>
  );
}

export function useTenantContext(): TenantClientContext {
  const ctx = useContext(TenantContext);
  if (ctx === null) {
    throw new Error(
      "useTenantContext must be called inside a <TenantProvider>. " +
        "Wrap your admin tree in routes/admin/__root.tsx.",
    );
  }
  return ctx;
}
