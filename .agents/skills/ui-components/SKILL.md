---
name: ui-components
description: KCG component-library reference — shadcn/ui + Radix UI primitives, dnd-kit exam builder pattern, CopilotKit + AG-UI protocol, Tuatha MMO game UI (Soul Level, Geasa, Map, NFT gallery), 3D asset pipeline, Celtic design language (green/amber/stone palette, Cinzel/Cormorant fonts, triskele icons). Pairs with `frontend-design` (aesthetic taste) and `copilotkit` (agent UI framework).
---

# UI Components

## When to use this skill

Use when you need to:

- "Build a new UI component (modal, form, table, etc.)"
- "Design a form with validation (TanStack Form + Zod)"
- "Add drag-and-drop to a quiz or exam builder"
- "Wire an agent UI component (CopilotKit + AG-UI)"
- "Style a Celtic-themed interface (Tuatha MMO, marimo, etc.)"
- "Set up a 3D asset pipeline (Blender → glTF → Babylon)"

## 1. Component foundation (shadcn/ui + Radix + Tailwind 4)

The canonical KCG component stack is **shadcn/ui** (the
copy-paste component library built on Radix UI primitives +
Tailwind CSS). shadcn/ui is preferred over a full component
library (MUI, Mantine) because:

- Components are **copied into your repo** (not in
  `node_modules`)
- You own the code; no upstream lock-in
- Theming is via CSS variables; trivially customised for
  Celtic themes

```bash
# Initialise
bunx shadcn@latest init
# Install components one at a time
bunx shadcn@latest add button
bunx shadcn@latest add dialog
bunx shadcn@latest add form
```

**Component inventory** (the canonical KCG set):

| Component | Use case |
|:--|:--|
| `Button` | primary / secondary / ghost / destructive |
| `Dialog` | modal forms, confirmations |
| `Form` | TanStack Form + Zod validation |
| `Table` | TanStack Table (sortable, filterable, paginated) |
| `Tabs` | multi-step forms, dashboards |
| `Tooltip` | contextual help |
| `Popover` | action menus, dropdowns |
| `Sheet` | mobile-friendly modals |
| `Toast` | success / error feedback |
| `Combobox` | autocomplete search |
| `Card` | content containers |
| `Accordion` | collapsible content |

## 2. Drag-and-drop exam builder (`@dnd-kit`)

The KCG exam builder (used in `oideachais/web/src/components/
exam-builder/`) uses `@dnd-kit` for drag-and-drop question
reordering. The pattern:

```typescript
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";

function ExamBuilder({ questions, onReorder }: ExamBuilderProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = questions.findIndex((q) => q.id === active.id);
      const newIndex = questions.findIndex((q) => q.id === over.id);
      onReorder(arrayMove(questions, oldIndex, newIndex));
    }
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={questions.map((q) => q.id)} strategy={verticalListSortingStrategy}>
        {questions.map((q) => <SortableQuestion key={q.id} question={q} />)}
      </SortableContext>
    </DndContext>
  );
}
```

The pattern: `DndContext` + `SortableContext` + draggable
items. Pair with `accessibility` (the `KeyboardSensor` enables
keyboard reordering for a11y).

## 3. Agent UI (CopilotKit + AG-UI protocol)

For agent UIs (chat, tool calls, shared state), the
canonical pattern is **CopilotKit** consuming the **AG-UI
SSE protocol**:

```typescript
import { CopilotChat, useCopilotAction } from "@copilotkit/react";
import { z } from "zod";

function ExamChat() {
  // Define a typed tool the agent can call
  useCopilotAction({
    name: "getExamQuestion",
    description: "Get a specific question from the exam corpus.",
    parameters: z.object({
      questionId: z.string(),
    }),
    handler: async ({ questionId }) => {
      return await fetch(`/api/exam/${questionId}`).then((r) => r.json());
    },
  });

  return (
    <CopilotChat
      labels={{
        title: "Exam tutor",
        initial: "Ask me about Junior Cycle Mathematics!",
      }}
    />
  );
}
```

The `useCopilotAction` hook auto-generates the AG-UI tool
schema (Zod → JSON Schema). The `CopilotChat` consumes the
AG-UI SSE stream from any backend (Pydantic AI / Agno /
Google ADK / BAML).

For the full AG-UI protocol table (17 event types), see
`.agents/skills/ag-ui/SKILL.md`.

## 4. Data viz (TanStack Table + Recharts)

For tabular data + charts:

- **TanStack Table** for sortable, filterable, paginated
  tables (see `.agents/skills/tanstack-start/SKILL.md`)
- **Recharts** for declarative React charts
- **Visx** for low-level D3 + React
- **Tremor** for dashboard widgets

The KCG marimo dashboard uses **Altair** (Python) + **Plotly**
(not React); see `.agents/skills/marimo/SKILL.md` for the
analyst-side viz stack.

## 5. Game UI (Tuatha MMO)

The Tuatha MMO has 7 distinct UI surfaces (per the
blueprint):

| Surface | Component | Notes |
|:--|:--|:--|
| **Soul Level** | radial progress + level name | Top-left corner, always visible |
| **Tuath Balance** | numeric display + recent transactions | Top-right corner |
| **Geasa** | scrollable list of vows (binding + status) | Bottom-right |
| **Anam Cara** | soulbound-NFT list with thumbnails | Inventory tab |
| **Map interface** | Babylon.js minimap + main scene | Full-screen (immersive) |
| **NFT gallery** | grid of soulbound-NFT cards | Inventory tab |
| **Quest log** | active + completed quests | Bottom-left |

All 7 surfaces share the **Celtic design language** (see
§7 below). The Babylon.js scene composition is documented in
`.agents/skills/babylonjs/SKILL.md`.

## 6. 3D asset pipeline

```bash
# 1. Source (Blender .blend, Maya .fbx, or .glb/.gltf)
# 2. Compression — Draco mesh + KTX2/Basis textures
# 3. Storage — tuatha/game/assets/models/ (committed) or
#    S3 (for large assets)
# 4. Loading — Babylon.js SceneLoader.ImportMeshAsync
# 5. Metadata — BAML extraction of pedagogical content
```

For 3D characters and environments, use **glTF 2.0** (the
canonical web 3D format). See `.agents/skills/babylonjs/SKILL.md`
§"Asset pipeline" for the full pattern.

## 7. Celtic design language

The canonical KCG design tokens:

```css
/* colors */
--celtic-green: #2D5016;     /* primary */
--celtic-amber: #B8860B;     /* accent */
--celtic-stone: #4A4A4A;     /* surface */
--celtic-mist:  #E8E4D8;     /* background */
--celtic-gold:  #C9A961;     /* highlight (Soul Level + Geasa) */

/* fonts */
--font-display: "Cinzel", "Cormorant Garamond", serif;
--font-body:    "EB Garamond", "Crimson Text", serif;
--font-mono:     "JetBrains Mono", monospace;

/* icons */
--icon-triskele: url("/icons/triskele.svg");
--icon-clogaelach: url("/icons/clo-gaelach.svg");
--icon-ogham: url("/icons/ogham.svg");
```

Use these in Tailwind via `theme.extend.colors`:

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        celtic: {
          green: "#2D5016",
          amber: "#B8860B",
          stone: "#4A4A4A",
          mist:  "#E8E4D8",
          gold:  "#C9A961",
        },
      },
      fontFamily: {
        display: ["Cinzel", "Cormorant Garamond", "serif"],
        body: ["EB Garamond", "Crimson Text", "serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
};
```

## Cross-references

- `.agents/skills/frontend-design/SKILL.md` — the
  *aesthetic taste* skill (Anthropic brand-guidelines style)
- `.agents/skills/copilotkit/SKILL.md` — the agent UI
  *framework*
- `.agents/skills/babylonjs/SKILL.md` — the 3D game engine
  (for the 3D asset pipeline)
- `.agents/skills/tanstack-start/SKILL.md` — the canonical
  TanStack Start reference
- `.agents/skills/marimo/SKILL.md` — the analyst notebook
  surface (uses Altair, not Recharts)
- `.agents/skills/frontend-topology/SKILL.md` — the 5-surface
  cross-cutting map
- `.agents/skills/irish-edtech/SKILL.md` — the Agentic
  Academy vision
