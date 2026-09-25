/**
 * AgenticCanvas — the declarative UI surface for AGUI-rendered agents.
 *
 * Per openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/.
 * Mirrors `.agents/skills/copilotkit-a2ui-renderer/SKILL.md`.
 *
 * Renders the `createSurface` / `updateComponents` / `updateDataModel` A2UI
 * operations emitted by agents through CopilotKit + AG-UI. The surface lives
 * inline with the chat panel — when an agent emits a `createSurface` op, the
 * canvas mounts; when it emits `updateComponents`, the canvas re-renders.
 *
 * ## What this component does
 *
 * 1. Listens for `agui_surface_message` events on the chat stream.
 * 2. Mounts the A2UIProvider for the active surface id.
 * 3. Renders the A2UIRenderer with the current `components` map + `dataModel`.
 * 4. Cleans up the surface on `removeSurface` (Phase 2 — not yet wired).
 *
 * ## Why not just ChatMessage content?
 *
 * The A2UI pattern keeps structured UI separate from the chat text stream:
 * - The agent emits **structured ops** (createSurface / updateComponents /
 *   updateDataModel), not HTML.
 * - The renderer owns the component tree (the model cannot inject raw HTML).
 * - The data model binds form inputs to state — the model writes structured
 *   data, the renderer maps it to UI primitives.
 *
 * ## Usage
 *
 * ```tsx
 * <OideachasChat />
 * <AgenticCanvas />  // sits beside the chat
 * ```
 */
import { useEffect, useState } from "react";
import { useCopilotChat } from "@copilotkit/react-core/v2";

interface A2UIComponent {
  id: string;
  component: string;
  props?: Record<string, unknown>;
  children?: A2UIComponent[];
}

interface A2UISurface {
  id: string;
  components: Record<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
}

interface AguiSurfaceMessage {
  type: "agui_surface_message";
  surfaceId: string;
  op: "createSurface" | "updateComponents" | "updateDataModel";
  payload: unknown;
}

export function AgenticCanvas() {
  const { visibleMessages } = useCopilotChat();
  const [surfaces, setSurfaces] = useState<Record<string, A2UISurface>>({});

  useEffect(() => {
    for (const m of visibleMessages) {
      const payload = (m as unknown as { response?: unknown[] }).response;
      if (!Array.isArray(payload)) continue;
      for (const op of payload as AguiSurfaceMessage[]) {
        if (op.type !== "agui_surface_message") continue;
        setSurfaces((prev) => {
          const cur = prev[op.surfaceId] ?? {
            id: op.surfaceId,
            components: {},
            dataModel: {},
          };
          if (op.op === "createSurface") {
            return { ...prev, [op.surfaceId]: { ...cur, ...(op.payload as Partial<A2UISurface>) } };
          }
          if (op.op === "updateComponents") {
            return {
              ...prev,
              [op.surfaceId]: {
                ...cur,
                components: { ...cur.components, ...(op.payload as Record<string, A2UIComponent>) },
              },
            };
          }
          if (op.op === "updateDataModel") {
            return {
              ...prev,
              [op.surfaceId]: {
                ...cur,
                dataModel: { ...cur.dataModel, ...(op.payload as Record<string, unknown>) },
              },
            };
          }
          return prev;
        });
      }
    }
  }, [visibleMessages]);

  return (
    <div className="flex flex-col gap-4">
      {Object.values(surfaces).map((surface) => (
        <div
          key={surface.id}
          className="bg-slate-800 border border-slate-700 rounded-lg p-4"
          data-surface-id={surface.id}
        >
          <div className="text-xs text-slate-500 font-mono mb-2">
            A2UI surface · {surface.id}
          </div>
          {Object.values(surface.components).map((comp) => (
            <A2UIComp key={comp.id} comp={comp} dataModel={surface.dataModel} />
          ))}
        </div>
      ))}
      {Object.keys(surfaces).length === 0 && (
        <div className="text-slate-500 text-sm">
          _No A2UI surface mounted. Agents will emit one when they need structured UI._
        </div>
      )}
    </div>
  );
}

function A2UIComp({ comp, dataModel }: { comp: A2UIComponent; dataModel: Record<string, unknown> }) {
  switch (comp.component) {
    case "Text":
      return (
        <div className="text-slate-200">
          {String(comp.props?.text ?? "")}
        </div>
      );
    case "Heading":
      return (
        <h2 className="text-slate-100 text-lg font-bold mt-2">
          {String(comp.props?.text ?? "")}
        </h2>
      );
    case "Button": {
      const label = String(comp.props?.label ?? "Run");
      const action = String(comp.props?.action ?? "");
      return (
        <button
          className="btn-tactile mt-2"
          onClick={() => {
            // Phase 2: dispatch the action via the A2UI bridge.
            if (action) console.log("[A2UI] dispatch:", action, dataModel);
          }}
        >
          {label}
        </button>
      );
    }
    case "Form":
      return (
        <div className="flex flex-col gap-2 mt-2">
          {comp.children?.map((c) => (
            <A2UIComp key={c.id} comp={c} dataModel={dataModel} />
          ))}
        </div>
      );
    case "TextInput": {
      const field = String(comp.props?.field ?? "");
      return (
        <input
          type="text"
          placeholder={String(comp.props?.placeholder ?? "")}
          className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200"
          defaultValue={String(dataModel[field] ?? "")}
        />
      );
    }
    case "Chart":
      return (
        <div className="bg-slate-900 border border-slate-700 rounded p-2 mt-2 text-slate-400 text-sm">
          [Chart: {String(comp.props?.kind ?? "bar")} — Phase 2 render]
        </div>
      );
    default:
      return (
        <div className="text-slate-500 text-xs font-mono">
          [Unknown A2UI component: {comp.component}]
        </div>
      );
  }
}
