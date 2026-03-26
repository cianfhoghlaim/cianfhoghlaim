/**
 * AG-UI Component Registry
 *
 * Provides dynamic component rendering for Generative UI events.
 * Components are lazy-loaded to optimize bundle size.
 *
 * @example
 * ```tsx
 * // Agent emits:
 * { type: "GENERATIVE_UI", component: "CurriculumCard", props: { title: "..." }, slot: "main" }
 *
 * // Frontend renders:
 * <AgentComponent event={event} />
 * ```
 */

import React, { lazy, Suspense, ComponentType } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import { cn } from "../../lib/utils";

/**
 * GenerativeUI event from AG-UI protocol.
 */
export interface GenerativeUIEvent {
  type: "GENERATIVE_UI";
  component: string;
  props: Record<string, unknown>;
  slot: "main" | "sidebar" | "overlay";
  component_id: string;
}

/**
 * Stored component instance for tracking rendered components.
 */
export interface RenderedComponent {
  id: string;
  component: string;
  props: Record<string, unknown>;
  slot: "main" | "sidebar" | "overlay";
  timestamp: Date;
}

/**
 * Props for dynamically rendered components.
 * All agent components receive these base props.
 */
export interface AgentComponentProps {
  componentId: string;
  [key: string]: unknown;
}

/**
 * Registry of lazy-loaded components that can be rendered by agents.
 *
 * Add new components here as they are created.
 * The key must match the `component` field in GenerativeUIEvent.
 */
const COMPONENT_REGISTRY: Record<
  string,
  React.LazyExoticComponent<ComponentType<AgentComponentProps>>
> = {
  // Curriculum components
  CurriculumCard: lazy(() => import("./components/CurriculumCard")),
  CurriculumCompare: lazy(() => import("./components/CurriculumCompare")),
  LearningOutcome: lazy(() => import("./components/LearningOutcome")),

  // Translation components
  TranslationResult: lazy(() => import("./components/TranslationResult")),

  // Data display components
  DataTable: lazy(() => import("./components/DataTable")),
  Chart: lazy(() => import("./components/Chart")),

  // Search results
  SearchResults: lazy(() => import("./components/SearchResults")),

  // Status/feedback components
  ProgressIndicator: lazy(() => import("./components/ProgressIndicator")),
  StatusCard: lazy(() => import("./components/StatusCard")),
};

/**
 * Loading skeleton for components during lazy load.
 */
function ComponentSkeleton({ name }: { name: string }) {
  return (
    <div className="animate-pulse rounded-lg border bg-muted/50 p-4">
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading {name}...</span>
      </div>
    </div>
  );
}

/**
 * Error fallback when a component fails to load or doesn't exist.
 */
function ComponentError({
  name,
  error,
}: {
  name: string;
  error?: string;
}) {
  return (
    <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
      <div className="flex items-center gap-2 text-destructive">
        <AlertCircle className="h-4 w-4" />
        <span className="text-sm font-medium">
          Failed to render component: {name}
        </span>
      </div>
      {error && (
        <p className="mt-2 text-xs text-muted-foreground">{error}</p>
      )}
    </div>
  );
}

/**
 * Error boundary for catching component rendering errors.
 */
interface ErrorBoundaryProps {
  children: React.ReactNode;
  componentName: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ComponentErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <ComponentError
          name={this.props.componentName}
          error={this.state.error?.message}
        />
      );
    }
    return this.props.children;
  }
}

/**
 * Main component renderer for AG-UI GenerativeUI events.
 *
 * Dynamically loads and renders components based on the event's
 * component name. Handles loading states and errors gracefully.
 *
 * @example
 * ```tsx
 * const event: GenerativeUIEvent = {
 *   type: "GENERATIVE_UI",
 *   component: "CurriculumCard",
 *   props: { title: "Junior Cycle Mathematics", nation: "Ireland" },
 *   slot: "main",
 *   component_id: "abc123"
 * };
 *
 * <AgentComponent event={event} />
 * ```
 */
export function AgentComponent({
  event,
  className,
}: {
  event: GenerativeUIEvent;
  className?: string;
}) {
  const Component = COMPONENT_REGISTRY[event.component];

  if (!Component) {
    return (
      <ComponentError
        name={event.component}
        error={`Component "${event.component}" is not registered. Available: ${Object.keys(COMPONENT_REGISTRY).join(", ")}`}
      />
    );
  }

  return (
    <ComponentErrorBoundary componentName={event.component}>
      <Suspense fallback={<ComponentSkeleton name={event.component} />}>
        <div
          className={cn("agent-component", className)}
          data-component-id={event.component_id}
          data-component-name={event.component}
          data-slot={event.slot}
        >
          <Component
            componentId={event.component_id}
            {...(event.props as Record<string, unknown>)}
          />
        </div>
      </Suspense>
    </ComponentErrorBoundary>
  );
}

/**
 * Check if a component name is registered.
 */
export function isComponentRegistered(name: string): boolean {
  return name in COMPONENT_REGISTRY;
}

/**
 * Get list of all registered component names.
 */
export function getRegisteredComponents(): string[] {
  return Object.keys(COMPONENT_REGISTRY);
}

/**
 * Register a new component dynamically.
 * Useful for plugins or runtime component loading.
 */
export function registerComponent(
  name: string,
  component: React.LazyExoticComponent<ComponentType<AgentComponentProps>>
): void {
  COMPONENT_REGISTRY[name] = component;
}

export default AgentComponent;
