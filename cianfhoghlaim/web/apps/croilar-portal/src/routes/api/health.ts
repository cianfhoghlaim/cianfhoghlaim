import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/health")({
  server: {
    handlers: {
      GET: () => {
        return Response.json({
          status: "healthy",
          timestamp: new Date().toISOString(),
          service: "aleyum-portal",
          version: "1.0.0",
        });
      },
    },
  },
});
