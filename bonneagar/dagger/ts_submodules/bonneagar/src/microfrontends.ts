/**
 * Microfrontends Configuration Generator
 *
 * Generates Turborepo-compatible routing config for unified dev proxy.
 * Based on the Turborepo microfrontends feature.
 */

import { dag, Directory, object, func } from "@dagger.io/dagger";
import { APP_CONFIGS, AppConfig } from "./apps.js";

export interface MicrofrontendRoute {
  path: string;
  app: string;
  port: number;
}

export interface TurboMicrofrontendsConfig {
  $schema: string;
  options: {
    localProxyPort: number;
  };
  applications: Record<string, {
    development: {
      local: {
        port: number;
      };
    };
    routing?: Array<{
      paths: string[];
    }>;
  }>;
}

/**
 * Path routing for each app
 */
const APP_ROUTES: Record<string, string[]> = {
  "aleyum": ["/", "/:path*"],  // Default/root app
  "aleyum-portal": ["/portal", "/portal/:path*"],
  "crypteolas": ["/crypto", "/crypto/:path*"],
  "tuath": ["/tuath", "/tuath/:path*"],
  "oideachais-web": ["/curriculum", "/curriculum/:path*"],
};

@object()
export class Microfrontends {
  /**
   * Generate routing based on active apps
   */
  @func()
  generateRoutes(activeAppsJson: string): string {
    const activeApps = JSON.parse(activeAppsJson) as string[];
    const routes: MicrofrontendRoute[] = [];

    for (const appName of activeApps) {
      const app = APP_CONFIGS[appName];
      if (!app || app.type === "backend") continue;

      const paths = APP_ROUTES[appName] || ["/" + appName, "/" + appName + "/:path*"];
      routes.push({
        path: paths[0],
        app: appName,
        port: app.defaultPort,
      });
    }

    return JSON.stringify(routes, null, 2);
  }

  /**
   * Generate microfrontends.json for Turborepo proxy
   */
  @func()
  generateConfig(
    activeAppsJson: string,
    proxyPort: number = 3024,
    defaultApp: string = "aleyum"
  ): string {
    const activeApps = JSON.parse(activeAppsJson) as string[];

    const applications: TurboMicrofrontendsConfig["applications"] = {};

    for (const appName of activeApps) {
      const app = APP_CONFIGS[appName];
      if (!app || app.type === "backend") continue;

      const appConfig: TurboMicrofrontendsConfig["applications"][string] = {
        development: {
          local: {
            port: app.defaultPort,
          },
        },
      };

      // Add routing for non-default apps
      const routes = APP_ROUTES[appName];
      if (routes && appName !== defaultApp) {
        appConfig.routing = [{ paths: routes }];
      }

      applications[appName] = appConfig;
    }

    const config: TurboMicrofrontendsConfig = {
      $schema: "https://turborepo.com/microfrontends/schema.json",
      options: {
        localProxyPort: proxyPort,
      },
      applications,
    };

    return JSON.stringify(config, null, 2);
  }

  /**
   * Write microfrontends.json to source directory
   */
  @func()
  async writeConfig(
    source: Directory,
    activeAppsJson: string,
    proxyPort: number = 3024
  ): Promise<Directory> {
    const config = this.generateConfig(activeAppsJson, proxyPort);

    return source.withNewFile("microfrontends.json", config);
  }

  /**
   * Generate nginx proxy config for production
   */
  @func()
  generateNginxConfig(activeAppsJson: string): string {
    const activeApps = JSON.parse(activeAppsJson) as string[];
    
    let config = "# Auto-generated nginx config for microfrontends\n\n";
    config += "server {\n";
    config += "    listen 80;\n";
    config += "    server_name _;\n\n";

    for (const appName of activeApps) {
      const app = APP_CONFIGS[appName];
      if (!app || app.type === "backend") continue;

      const routes = APP_ROUTES[appName] || ["/" + appName];
      const basePath = routes[0].replace("/:path*", "");

      if (basePath === "/" || basePath === "") {
        // Default app - handle at the end
        continue;
      }

      config += "    location " + basePath + " {\n";
      config += "        proxy_pass http://localhost:" + app.defaultPort + ";\n";
      config += "        proxy_http_version 1.1;\n";
      config += "        proxy_set_header Upgrade $http_upgrade;\n";
      config += "        proxy_set_header Connection 'upgrade';\n";
      config += "        proxy_set_header Host $host;\n";
      config += "        proxy_cache_bypass $http_upgrade;\n";
      config += "    }\n\n";
    }

    // Default app (aleyum) catches everything else
    const defaultApp = APP_CONFIGS["aleyum"];
    if (defaultApp) {
      config += "    location / {\n";
      config += "        proxy_pass http://localhost:" + defaultApp.defaultPort + ";\n";
      config += "        proxy_http_version 1.1;\n";
      config += "        proxy_set_header Upgrade $http_upgrade;\n";
      config += "        proxy_set_header Connection 'upgrade';\n";
      config += "        proxy_set_header Host $host;\n";
      config += "        proxy_cache_bypass $http_upgrade;\n";
      config += "    }\n";
    }

    config += "}\n";
    return config;
  }

  /**
   * Generate Caddy config for production (alternative to nginx)
   */
  @func()
  generateCaddyConfig(domain: string, activeAppsJson: string): string {
    const activeApps = JSON.parse(activeAppsJson) as string[];
    
    let config = "# Auto-generated Caddyfile for microfrontends\n\n";
    config += domain + " {\n";

    for (const appName of activeApps) {
      const app = APP_CONFIGS[appName];
      if (!app || app.type === "backend") continue;

      const routes = APP_ROUTES[appName] || ["/" + appName];
      const basePath = routes[0].replace("/:path*", "");

      if (basePath === "/" || basePath === "") {
        continue;
      }

      config += "    handle_path " + basePath + "/* {\n";
      config += "        reverse_proxy localhost:" + app.defaultPort + "\n";
      config += "    }\n\n";
    }

    // Default app
    const defaultApp = APP_CONFIGS["aleyum"];
    if (defaultApp) {
      config += "    handle {\n";
      config += "        reverse_proxy localhost:" + defaultApp.defaultPort + "\n";
      config += "    }\n";
    }

    config += "}\n";
    return config;
  }

  /**
   * Get the proxy URL for development
   */
  @func()
  getProxyUrl(proxyPort: number = 3024): string {
    return "http://localhost:" + proxyPort;
  }

  /**
   * List available route mappings
   */
  @func()
  listRoutes(): string {
    const lines = ["Route Mappings:", ""];
    
    for (const [appName, routes] of Object.entries(APP_ROUTES)) {
      lines.push("  " + appName + ": " + routes.join(", "));
    }
    
    return lines.join("\n");
  }
}
