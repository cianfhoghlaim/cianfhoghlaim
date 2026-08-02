import { os } from "@orpc/server";
import { z } from "zod";

// Dashboard configuration schema
const DashboardConfigSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(["marimo", "dagster"]),
  url: z.string(),
  enabled: z.boolean(),
});

type DashboardConfig = z.infer<typeof DashboardConfigSchema>;

// In-memory dashboard configurations (in production, use a database)
const dashboards: DashboardConfig[] = [
  {
    id: "marimo-analytics",
    name: "Analytics Dashboard",
    type: "marimo",
    url: "/api/proxy/marimo/",
    enabled: true,
  },
  {
    id: "dagster-pipelines",
    name: "Data Pipelines",
    type: "dagster",
    url: "/api/proxy/dagster/",
    enabled: true,
  },
];

/**
 * oRPC router for managing embedded dashboards
 */
export const router = {
  // List all available dashboards
  listDashboards: os.handler(() => {
    return dashboards.filter((d) => d.enabled);
  }),

  // Get a specific dashboard by ID
  getDashboard: os
    .input(z.object({ id: z.string() }))
    .handler(({ input }) => {
      const dashboard = dashboards.find((d) => d.id === input.id);
      if (!dashboard) {
        throw new Error(`Dashboard not found: ${input.id}`);
      }
      return dashboard;
    }),

  // Get dashboard status (check if service is reachable)
  getDashboardStatus: os
    .input(z.object({ id: z.string() }))
    .handler(async ({ input }) => {
      const dashboard = dashboards.find((d) => d.id === input.id);
      if (!dashboard) {
        return { id: input.id, status: "not_found" as const };
      }

      // In production, actually check service health
      // For now, return a mock status
      return {
        id: input.id,
        status: "healthy" as const,
        lastChecked: new Date().toISOString(),
      };
    }),

  // Get embedding configuration for a dashboard
  getEmbedConfig: os
    .input(z.object({ id: z.string() }))
    .handler(({ input }) => {
      const dashboard = dashboards.find((d) => d.id === input.id);
      if (!dashboard) {
        throw new Error(`Dashboard not found: ${input.id}`);
      }

      return {
        ...dashboard,
        iframeAttributes: {
          sandbox: "allow-scripts allow-same-origin allow-forms allow-popups",
          loading: "lazy" as const,
          referrerPolicy: "no-referrer" as const,
        },
      };
    }),
};

export type Router = typeof router;
