/**
 * Component Registry for AG-UI Generative UI.
 *
 * Maps component names from agent events to React components,
 * enabling dynamic UI rendering from agent responses.
 *
 * Usage:
 * - Agent emits: GENERATIVE_UI { component: "CurriculumCard", props: {...}, slot: "main" }
 * - Registry renders: <CurriculumCard {...props} />
 */

import { ComponentType, useState, useCallback, useMemo } from "react";
import { CurriculumCard, type CurriculumCardProps } from "./CurriculumCard";
import { PronunciationButton, type PronunciationButtonProps } from "./PronunciationButton";
import { AssessmentWidget, type AssessmentWidgetProps } from "./AssessmentWidget";
import { ProgressChart, type ProgressChartProps } from "./ProgressChart";

// ============================================================================
// Types
// ============================================================================

export type SlotType = "main" | "sidebar" | "overlay";

export interface GenerativeUIEvent {
  type: "GENERATIVE_UI";
  component: string;
  props: Record<string, unknown>;
  slot: SlotType;
  component_id: string;
  timestamp: string;
}

export interface RenderedComponent {
  id: string;
  component: string;
  props: Record<string, unknown>;
  slot: SlotType;
  timestamp: Date;
}

// ============================================================================
// Component Registry
// ============================================================================

/**
 * Registry mapping component names to React components.
 * Add new generative UI components here.
 */
export const componentRegistry: Record<string, ComponentType<any>> = {
  CurriculumCard,
  PronunciationButton,
  AssessmentWidget,
  ProgressChart,
};

/**
 * Check if a component is registered.
 */
export function isRegisteredComponent(name: string): boolean {
  return name in componentRegistry;
}

/**
 * Get a component from the registry.
 */
export function getComponent(name: string): ComponentType<any> | null {
  return componentRegistry[name] ?? null;
}

// ============================================================================
// Generative UI Renderer Hook
// ============================================================================

export interface UseGenerativeUIOptions {
  /** Maximum number of components to keep in each slot */
  maxComponentsPerSlot?: number;
  /** Callback when a component is rendered */
  onComponentRendered?: (component: RenderedComponent) => void;
  /** Callback when a component is dismissed */
  onComponentDismissed?: (componentId: string) => void;
}

export interface UseGenerativeUIReturn {
  /** All rendered components by slot */
  componentsBySlot: Record<SlotType, RenderedComponent[]>;
  /** Add a new component from an event */
  addComponent: (event: GenerativeUIEvent) => void;
  /** Remove a component by ID */
  removeComponent: (componentId: string) => void;
  /** Clear all components in a slot */
  clearSlot: (slot: SlotType) => void;
  /** Clear all components */
  clearAll: () => void;
  /** Get components for a specific slot */
  getSlotComponents: (slot: SlotType) => RenderedComponent[];
}

/**
 * Hook to manage generative UI components.
 */
export function useGenerativeUI(
  options: UseGenerativeUIOptions = {}
): UseGenerativeUIReturn {
  const {
    maxComponentsPerSlot = 10,
    onComponentRendered,
    onComponentDismissed,
  } = options;

  const [components, setComponents] = useState<RenderedComponent[]>([]);

  const componentsBySlot = useMemo(() => {
    const result: Record<SlotType, RenderedComponent[]> = {
      main: [],
      sidebar: [],
      overlay: [],
    };

    for (const component of components) {
      result[component.slot].push(component);
    }

    return result;
  }, [components]);

  const addComponent = useCallback(
    (event: GenerativeUIEvent) => {
      if (!isRegisteredComponent(event.component)) {
        console.warn(
          `[GenerativeUI] Unknown component: ${event.component}. ` +
            `Available: ${Object.keys(componentRegistry).join(", ")}`
        );
        return;
      }

      const newComponent: RenderedComponent = {
        id: event.component_id,
        component: event.component,
        props: event.props,
        slot: event.slot,
        timestamp: new Date(event.timestamp),
      };

      setComponents((prev) => {
        // Filter to slot and enforce max
        const slotComponents = prev.filter((c) => c.slot === event.slot);
        const otherComponents = prev.filter((c) => c.slot !== event.slot);

        let updatedSlot = [...slotComponents, newComponent];

        // Remove oldest if exceeding max
        if (updatedSlot.length > maxComponentsPerSlot) {
          updatedSlot = updatedSlot.slice(-maxComponentsPerSlot);
        }

        return [...otherComponents, ...updatedSlot];
      });

      onComponentRendered?.(newComponent);
    },
    [maxComponentsPerSlot, onComponentRendered]
  );

  const removeComponent = useCallback(
    (componentId: string) => {
      setComponents((prev) => prev.filter((c) => c.id !== componentId));
      onComponentDismissed?.(componentId);
    },
    [onComponentDismissed]
  );

  const clearSlot = useCallback((slot: SlotType) => {
    setComponents((prev) => prev.filter((c) => c.slot !== slot));
  }, []);

  const clearAll = useCallback(() => {
    setComponents([]);
  }, []);

  const getSlotComponents = useCallback(
    (slot: SlotType) => componentsBySlot[slot],
    [componentsBySlot]
  );

  return {
    componentsBySlot,
    addComponent,
    removeComponent,
    clearSlot,
    clearAll,
    getSlotComponents,
  };
}

// ============================================================================
// Slot Renderer Component
// ============================================================================

export interface SlotRendererProps {
  slot: SlotType;
  components: RenderedComponent[];
  onDismiss?: (componentId: string) => void;
  className?: string;
}

/**
 * Renders all components in a specific slot.
 */
export function SlotRenderer({
  slot,
  components,
  onDismiss,
  className = "",
}: SlotRendererProps) {
  if (components.length === 0) {
    return null;
  }

  const slotStyles: Record<SlotType, string> = {
    main: "space-y-4",
    sidebar: "space-y-3",
    overlay: "fixed inset-0 z-50 flex items-center justify-center bg-black/50",
  };

  return (
    <div className={`generative-ui-slot generative-ui-${slot} ${slotStyles[slot]} ${className}`}>
      {components.map((rendered) => {
        const Component = getComponent(rendered.component);
        if (!Component) return null;

        return (
          <div key={rendered.id} className="generative-ui-component">
            <Component
              {...rendered.props}
              componentId={rendered.id}
              onDismiss={() => onDismiss?.(rendered.id)}
            />
          </div>
        );
      })}
    </div>
  );
}

// ============================================================================
// Full Layout Component
// ============================================================================

export interface GenerativeUILayoutProps {
  componentsBySlot: Record<SlotType, RenderedComponent[]>;
  onDismiss?: (componentId: string) => void;
  children?: React.ReactNode;
  mainClassName?: string;
  sidebarClassName?: string;
}

/**
 * Complete layout with main, sidebar, and overlay slots.
 */
export function GenerativeUILayout({
  componentsBySlot,
  onDismiss,
  children,
  mainClassName = "",
  sidebarClassName = "",
}: GenerativeUILayoutProps) {
  const hasMainComponents = componentsBySlot.main.length > 0;
  const hasSidebarComponents = componentsBySlot.sidebar.length > 0;
  const hasOverlayComponents = componentsBySlot.overlay.length > 0;

  return (
    <>
      <div className={`flex gap-6 ${hasSidebarComponents ? "" : ""}`}>
        {/* Main content area */}
        <div className={`flex-1 ${mainClassName}`}>
          {children}
          {hasMainComponents && (
            <div className="mt-6">
              <SlotRenderer
                slot="main"
                components={componentsBySlot.main}
                onDismiss={onDismiss}
              />
            </div>
          )}
        </div>

        {/* Sidebar */}
        {hasSidebarComponents && (
          <aside className={`w-80 flex-shrink-0 ${sidebarClassName}`}>
            <SlotRenderer
              slot="sidebar"
              components={componentsBySlot.sidebar}
              onDismiss={onDismiss}
            />
          </aside>
        )}
      </div>

      {/* Overlay */}
      {hasOverlayComponents && (
        <SlotRenderer
          slot="overlay"
          components={componentsBySlot.overlay}
          onDismiss={onDismiss}
        />
      )}
    </>
  );
}

// Export types for component props
export type {
  CurriculumCardProps,
  PronunciationButtonProps,
  AssessmentWidgetProps,
  ProgressChartProps,
};

export default componentRegistry;
