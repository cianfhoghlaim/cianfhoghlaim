// /en/__layout.tsx — English locale layout
// Shared by all /en/* routes. Provides the EN locale context.
import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/en/__layout")({
  component: EnLayoutComponent,
});

function EnLayoutComponent() {
  return <Outlet />;
}
