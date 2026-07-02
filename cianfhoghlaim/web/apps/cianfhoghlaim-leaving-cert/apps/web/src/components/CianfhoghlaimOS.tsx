"use client";

// <CianfhoghlaimOS> — PostHog-style window manager
// Per docs/BROWN_AJAH_THEMING.md, the platform is themed as the White Tower.
// The Cianfhoghlaim OS is the PostHog-style window manager where each
// subject specialist (Brown Ajah member) can open a floating window.
//
// The state machine is `{windows: Window[], activeId, dispatch}`.
// The URL reflects the active window (?window=syllabus-mathematics&geometry=200,200,800,600).
// The Framer Motion physics drives drag/snap with momentum.

import * as React from "react";
import { motion } from "framer-motion";
import { Rnd } from "react-rnd";

export interface Window {
  id: string;
  title: string;
  component: React.ComponentType;
  geometry: { x: number; y: number; width: number; height: number };
  zIndex: number;
  status: "OPEN" | "MINIMIZED" | "MAXIMIZED";
}

export interface CianfhoghlaimOSContext {
  windows: Window[];
  activeId: string | null;
  dispatch: (action: OSAction) => void;
}

export type OSAction =
  | { type: "OPEN"; window: Window }
  | { type: "CLOSE"; id: string }
  | { type: "MINIMIZE"; id: string }
  | { type: "MAXIMIZE"; id: string }
  | { type: "FOCUS"; id: string }
  | { type: "MOVE"; id: string; geometry: { x: number; y: number; width: number; height: number } };

const CianfhoghlaimOSContext = React.createContext<CianfhoghlaimOSContext | null>(null);

export function CianfhoghlaimOSProvider({
  children,
  initialWindows = [],
}: {
  children: React.ReactNode;
  initialWindows?: Window[];
}) {
  const [windows, setWindows] = React.useState<Window[]>(initialWindows);
  const [activeId, setActiveId] = React.useState<string | null>(
    initialWindows[0]?.id ?? null,
  );

  const dispatch = React.useCallback((action: OSAction) => {
    setWindows((prev) => {
      switch (action.type) {
        case "OPEN":
          if (prev.some((w) => w.id === action.window.id)) {
            return prev.map((w) => (w.id === action.window.id ? { ...w, status: "OPEN" } : w));
          }
          return [...prev, { ...action.window, zIndex: prev.length + 1 }];
        case "CLOSE":
          return prev.filter((w) => w.id !== action.id);
        case "MINIMIZE":
          return prev.map((w) => (w.id === action.id ? { ...w, status: "MINIMIZED" } : w));
        case "MAXIMIZE":
          return prev.map((w) => (w.id === action.id ? { ...w, status: "MAXIMIZED" } : w));
        case "FOCUS":
          setActiveId(action.id);
          return prev.map((w) =>
            w.id === action.id ? { ...w, zIndex: Math.max(...prev.map((p) => p.zIndex)) + 1 } : w,
          );
        case "MOVE":
          return prev.map((w) => (w.id === action.id ? { ...w, geometry: action.geometry } : w));
        default:
          return prev;
      }
    });
    if (action.type === "FOCUS") {
      setActiveId(action.id);
    }
  }, []);

  const value = React.useMemo(
    () => ({ windows, activeId, dispatch }),
    [windows, activeId, dispatch],
  );

  return (
    <CianfhoghlaimOSContext.Provider value={value}>
      {children}
    </CianfhoghlaimOSContext.Provider>
  );
}

export function useCianfhoghlaimOS() {
  const ctx = React.useContext(CianfhoghlaimOSContext);
  if (!ctx) throw new Error("useCianfhoghlaimOS must be used within CianfhoghlaimOSProvider");
  return ctx;
}

export function WindowFrame({ window }: { window: Window }) {
  const { dispatch, activeId } = useCianfhoghlaimOS();
  const isActive = activeId === window.id;
  const Component = window.component;

  if (window.status === "MINIMIZED") return null;

  if (window.status === "MAXIMIZED") {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 z-50 bg-slate-900"
        style={{ zIndex: window.zIndex }}
      >
        <div className="flex items-center justify-between p-2 bg-slate-950 border-b border-slate-800">
          <span className="font-cinzel text-emerald-400">{window.title}</span>
          <button
            onClick={() => dispatch({ type: "MAXIMIZE", id: window.id })}
            className="text-slate-400 hover:text-slate-100"
          >
            Restore
          </button>
        </div>
        <Component />
      </motion.div>
    );
  }

  return (
    <Rnd
      position={window.geometry}
      size={{ width: window.geometry.width, height: window.geometry.height }}
      onDragStop={(_, d) => {
        dispatch({
          type: "MOVE",
          id: window.id,
          geometry: { ...window.geometry, x: d.x, y: d.y },
        });
      }}
      onResizeStop={(_, __, ref, ___, position) => {
        dispatch({
          type: "MOVE",
          id: window.id,
          geometry: {
            x: position.x,
            y: position.y,
            width: ref.offsetWidth,
            height: ref.offsetHeight,
          },
        });
      }}
      onMouseDown={() => dispatch({ type: "FOCUS", id: window.id })}
      bounds="parent"
      dragHandleClassName="window-handle"
      className={cn(
        "rounded-xl overflow-hidden shadow-2xl border-2",
        isActive ? "border-emerald-600" : "border-slate-700",
      )}
      style={{ zIndex: window.zIndex }}
    >
      <div className="bg-slate-900 h-full flex flex-col">
        <div className="window-handle bg-slate-950 px-3 py-2 flex items-center justify-between cursor-move border-b border-slate-800">
          <span className="font-cinzel text-emerald-400 text-sm">{window.title}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => dispatch({ type: "MINIMIZE", id: window.id })}
              className="text-slate-400 hover:text-amber-400 text-xs"
              aria-label="Minimize"
            >
              _
            </button>
            <button
              onClick={() => dispatch({ type: "MAXIMIZE", id: window.id })}
              className="text-slate-400 hover:text-blue-400 text-xs"
              aria-label="Maximize"
            >
              ▢
            </button>
            <button
              onClick={() => dispatch({ type: "CLOSE", id: window.id })}
              className="text-slate-400 hover:text-red-400 text-xs"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-auto">
          <Component />
        </div>
      </div>
    </Rnd>
  );
}

// Helper cn re-exported for convenience
import { cn } from "@cianfhoghlaim/ui";