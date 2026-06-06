import {
  IconCirclePlusFilled,
  IconDashboard,
  IconLink,
  IconReport,
} from "@tabler/icons-react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useNavigate } from "@tanstack/react-router";

export function NavMain() {
  const nav = useNavigate();

  const items = [
    {
      title: "Dashboard",
      navigate: () =>
        nav({
          to: "/app",
        }),
      icon: IconDashboard,
    },
    {
      title: "Links",
      navigate: () =>
        nav({
          to: "/app/links",
        }),
      icon: IconLink,
    },
    {
      title: "Evaluations",
      navigate: () =>
        nav({
          to: "/app/evaluations",
        }),
      icon: IconReport,
    },
  ];

  return (
    <SidebarGroup>
      <SidebarGroupContent className="flex flex-col gap-2">
        <SidebarMenu>
          <SidebarMenuItem className="flex items-center gap-2">
            <SidebarMenuButton
              onClick={() =>
                nav({
                  to: "/app/create",
                })
              }
              tooltip="Quick Create"
              className="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear"
            >
              <IconCirclePlusFilled />
              <span>Create Link</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton onClick={item.navigate} tooltip={item.title}>
                {item.icon && <item.icon />}
                <span>{item.title}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
