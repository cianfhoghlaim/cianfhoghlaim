import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import { Suspense } from "react";
import appCss from "@/styles.css?url";
import {
  TenantProvider,
  fetchTenantConfig,
  defaultTenantContext,
} from "@/lib/tenant";
import type { TenantClientContext } from "@/lib/tenant";

export const Route = createRootRoute({
  // Load tenant config before rendering
  beforeLoad: async ({ context }) => {
    try {
      const tenantConfig = await fetchTenantConfig();
      return { tenantConfig };
    } catch (error) {
      console.error("Failed to load tenant config:", error);
      return { tenantConfig: defaultTenantContext };
    }
  },
  head: () => {
    // Use default context for head - tenant config loaded async may not be available
    const tenant = defaultTenantContext;

    return {
      meta: [
        { charSet: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { title: tenant.seo.title },
        { name: "description", content: tenant.seo.description },
        { name: "keywords", content: tenant.seo.keywords.join(", ") },
        // Open Graph
        { property: "og:title", content: tenant.seo.title },
        { property: "og:description", content: tenant.seo.description },
        { property: "og:image", content: tenant.seo.ogImage },
        { property: "og:type", content: "website" },
        // Twitter
        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:title", content: tenant.seo.title },
        { name: "twitter:description", content: tenant.seo.description },
        ...(tenant.seo.twitterHandle
          ? [{ name: "twitter:site", content: tenant.seo.twitterHandle }]
          : []),
      ],
      links: [
        { rel: "stylesheet", href: appCss },
        { rel: "icon", href: tenant.theme.favicon },
      ],
    };
  },
  component: RootComponent,
});

function RootComponent() {
  const { tenantConfig } = Route.useRouteContext() as {
    tenantConfig: TenantClientContext;
  };

  return (
    <TenantProvider config={tenantConfig || defaultTenantContext}>
      <RootDocument tenant={tenantConfig || defaultTenantContext}>
        <Suspense
          fallback={
            <div className="flex items-center justify-center min-h-screen">
              <div className="animate-pulse text-lg">Loading...</div>
            </div>
          }
        >
          <Outlet />
        </Suspense>
      </RootDocument>
    </TenantProvider>
  );
}

interface RootDocumentProps {
  children: React.ReactNode;
  tenant: TenantClientContext;
}

function RootDocument({ children, tenant }: RootDocumentProps) {
  return (
    <html lang={tenant.languages.primary} className="dark">
      <head>
        <HeadContent />
        {/* Dynamic CSS variables for tenant theme */}
        <style
          dangerouslySetInnerHTML={{
            __html: `
              :root {
                --color-primary: ${tenant.theme.primaryColor};
                --color-secondary: ${tenant.theme.secondaryColor};
                --color-accent: ${tenant.theme.accentColor};
                --color-background: ${tenant.theme.backgroundColor};
                --color-foreground: ${tenant.theme.foregroundColor};
                --font-family: ${tenant.theme.fontFamily};
                --font-heading: ${tenant.theme.fontHeading};
                --radius: ${tenant.theme.borderRadius};
              }
            `,
          }}
        />
      </head>
      <body
        className={`min-h-screen bg-background antialiased tenant-${tenant.id} tenant-type-${tenant.type}`}
        style={{ fontFamily: tenant.theme.fontFamily }}
      >
        {children}
        <Scripts />
      </body>
    </html>
  );
}
