// /ga/__layout.tsx — Irish locale layout
// Shared by all /ga/* routes. Provides the GA locale context.
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/ga")({
  component: GaLayoutComponent,
});

function GaLayoutComponent() {
  return <Outlet />;
}
