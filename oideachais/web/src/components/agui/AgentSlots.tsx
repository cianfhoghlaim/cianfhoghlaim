/**
 * AG-UI Agent Slots Layout Component
 *
 * Provides a slot-based layout for rendering Generative UI components.
 * Agents can emit components to specific slots: main, sidebar, overlay.
 *
 * @example
 * ```tsx
 * <AgentSlotsProvider>
 *   <AgentSlots
 *     components={components}
 *     onDismissOverlay={handleDismiss}
 *   />
 *   <ChatInterface />
 * </AgentSlotsProvider>
 * ```
 */

import React, { createContext, useContext, useState, useCallback } from "react";
import { X } from "lucide-react";
import { cn } from "../../lib/utils";
import {
  AgentComponent,
  GenerativeUIEvent,
  RenderedComponent,
} from "./ComponentRegistry";

/**
 * Context for managing agent-rendered components across the app.
 */
interface AgentSlotsContextValue {
  components: RenderedComponent[];
  addComponent: (event: GenerativeUIEvent) => void;
  removeComponent: (componentId: string) => void;
  clearSlot: (slot: "main" | "sidebar" | "overlay") => void;
  clearAll: () => void;
}

const AgentSlotsContext = createContext<AgentSlotsContextValue | null>(null);

/**
 * Hook to access the agent slots context.
 */
export function useAgentSlots(): AgentSlotsContextValue {
  const context = useContext(AgentSlotsContext);
  if (!context) {
    throw new Error("useAgentSlots must be used within AgentSlotsProvider");
  }
  return context;
}

/**
 * Provider for agent slots state management.
 */
export function AgentSlotsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [components, setComponents] = useState<RenderedComponent[]>([]);

  const addComponent = useCallback((event: GenerativeUIEvent) => {
    const rendered: RenderedComponent = {
      id: event.component_id,
      component: event.component,
      props: event.props,
      slot: event.slot,
      timestamp: new Date(),
    };

    setComponents((prev) => {
      // For overlay slot, replace existing overlay
      if (event.slot === "overlay") {
        return [...prev.filter((c) => c.slot !== "overlay"), rendered];
      }
      // For other slots, append or replace by ID
      const existing = prev.findIndex((c) => c.id === event.component_id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = rendered;
        return updated;
      }
      return [...prev, rendered];
    });
  }, []);

  const removeComponent = useCallback((componentId: string) => {
    setComponents((prev) => prev.filter((c) => c.id !== componentId));
  }, []);

  const clearSlot = useCallback((slot: "main" | "sidebar" | "overlay") => {
    setComponents((prev) => prev.filter((c) => c.slot !== slot));
  }, []);

  const clearAll = useCallback(() => {
    setComponents([]);
  }, []);

  return (
    <AgentSlotsContext.Provider
      value={{
        components,
        addComponent,
        removeComponent,
        clearSlot,
        clearAll,
      }}
    >
      {children}
    </AgentSlotsContext.Provider>
  );
}

/**
 * Props for the AgentSlots layout component.
 */
interface AgentSlotsProps {
  /** Components to render in slots */
  components: RenderedComponent[];
  /** Callback when overlay is dismissed */
  onDismissOverlay?: () => void;
  /** Callback when a component is removed */
  onRemoveComponent?: (componentId: string) => void;
  /** Custom class for the container */
  className?: string;
  /** Whether to show the sidebar */
  showSidebar?: boolean;
  /** Sidebar width */
  sidebarWidth?: string;
}

/**
 * Main slots layout component.
 *
 * Renders agent components in their designated slots:
 * - main: Primary content area (left/center)
 * - sidebar: Side panel (right)
 * - overlay: Modal overlay (centered, with backdrop)
 */
export function AgentSlots({
  components,
  onDismissOverlay,
  onRemoveComponent,
  className,
  showSidebar = true,
  sidebarWidth = "320px",
}: AgentSlotsProps) {
  const mainComponents = components.filter((c) => c.slot === "main");
  const sidebarComponents = components.filter((c) => c.slot === "sidebar");
  const overlayComponent = components.find((c) => c.slot === "overlay");

  const renderComponent = (rendered: RenderedComponent) => {
    const event: GenerativeUIEvent = {
      type: "GENERATIVE_UI",
      component: rendered.component,
      props: rendered.props,
      slot: rendered.slot,
      component_id: rendered.id,
    };

    return (
      <div key={rendered.id} className="relative group">
        <AgentComponent event={event} />
        {onRemoveComponent && (
          <button
            onClick={() => onRemoveComponent(rendered.id)}
            className={cn(
              "absolute top-2 right-2 p-1 rounded-full",
              "bg-background/80 hover:bg-destructive/10",
              "opacity-0 group-hover:opacity-100 transition-opacity",
              "text-muted-foreground hover:text-destructive"
            )}
            aria-label="Remove component"
          >
            <X className="h-3 w-3" />
          </button>
        )}
      </div>
    );
  };

  return (
    <div className={cn("agent-slots", className)}>
      {/* Main + Sidebar Layout */}
      <div className="flex gap-4">
        {/* Main Content Area */}
        {mainComponents.length > 0 && (
          <div className="agent-slot-main flex-1 space-y-4">
            {mainComponents.map(renderComponent)}
          </div>
        )}

        {/* Sidebar */}
        {showSidebar && sidebarComponents.length > 0 && (
          <aside
            className="agent-slot-sidebar space-y-4 flex-shrink-0"
            style={{ width: sidebarWidth }}
          >
            {sidebarComponents.map(renderComponent)}
          </aside>
        )}
      </div>

      {/* Overlay */}
      {overlayComponent && (
        <div
          className={cn(
            "agent-slot-overlay",
            "fixed inset-0 z-50",
            "bg-background/80 backdrop-blur-sm",
            "flex items-center justify-center p-4"
          )}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              onDismissOverlay?.();
            }
          }}
        >
          <div
            className={cn(
              "relative bg-background rounded-lg border shadow-lg",
              "max-w-2xl w-full max-h-[90vh] overflow-auto"
            )}
          >
            {/* Close button */}
            <button
              onClick={onDismissOverlay}
              className={cn(
                "absolute top-4 right-4 p-1.5 rounded-full",
                "hover:bg-muted transition-colors",
                "text-muted-foreground hover:text-foreground"
              )}
              aria-label="Close overlay"
            >
              <X className="h-4 w-4" />
            </button>

            {/* Overlay content */}
            <div className="p-6">{renderComponent(overlayComponent)}</div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version of AgentSlots for embedding within chat messages.
 * Only renders main slot components inline.
 */
export function InlineAgentSlot({
  components,
  className,
}: {
  components: RenderedComponent[];
  className?: string;
}) {
  const mainComponents = components.filter((c) => c.slot === "main");

  if (mainComponents.length === 0) return null;

  return (
    <div className={cn("inline-agent-slot space-y-2", className)}>
      {mainComponents.map((rendered) => {
        const event: GenerativeUIEvent = {
          type: "GENERATIVE_UI",
          component: rendered.component,
          props: rendered.props,
          slot: rendered.slot,
          component_id: rendered.id,
        };
        return <AgentComponent key={rendered.id} event={event} />;
      })}
    </div>
  );
}

export default AgentSlots;
