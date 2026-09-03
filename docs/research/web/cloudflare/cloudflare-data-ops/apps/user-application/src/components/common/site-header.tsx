import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useRouterState } from "@tanstack/react-router";

export function SiteHeader() {
  const routerState = useRouterState();
  const pathname = routerState.location.pathname;

  const getPageTitle = (path: string) => {
    if (path === "/app") return "Dashboard";
    if (path === "/app/links") return "Links";
    if (path === "/app/create") return "Create Link";
    if (path.startsWith("/app/link/")) {
      return `Link`;
    }
    // Add more path mappings as needed
    return "Dashboard";
  };

  return (
    <header className="flex h-(--header-height) shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-2 data-[orientation=vertical]:h-4"
        />
        <h1 className="text-base font-medium">{getPageTitle(pathname)}</h1>
      </div>
    </header>
  );
}
