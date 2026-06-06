---
domain: web
title: UI Components
description: Consolidated shadcn/ui, CopilotKit UI, component library patterns, drag-and-drop (dnd-kit), exam builder, and frontend visual design.
supersedes:
  - docs/web/React Drag-and-Drop for Exam Builder.md
  - docs/web/ref-ui-inspiration.md
  - docs/web/Frontend Idea Catalog Development.md
  - docs/web/Asset Management for Full-Stack App.md
  - docs/web/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md
cognee_entities:
  - entity: shadcnUI
    type: ComponentLibrary
    relationships:
      - built_on: RadixUI
      - works_with: TailwindCSS
  - entity: CopilotKit
    type: AIIntegration
    relationships:
      - implements: AGUIProtocol
      - renders: GenerativeUI
  - entity: dndKit
    type: Library
    relationships:
      - enables: DragAndDrop
      - integrates_with: TanStackTable
ccc_query_hints:
  - "shadcn/ui component patterns"
  - "CopilotKit generative UI"
  - "drag and drop exam builder"
  - "accessible component Radix UI"
  - "educational UI design patterns"
updated: 2026-06-06
---

# UI Components

Consolidated reference for the component library, agent UI integration, drag-and-drop patterns, and visual design system used across the product web application and educational interfaces.

## 1. shadcn/ui + Radix UI: Component Foundation

### Architecture

shadcn/ui is a copy-paste component system built on Radix UI primitives:

```
shadcn/ui Components (Button, Card, Dialog, Form, Table, ...)
    ↓
Radix UI Primitives (Accessible, unstyled React components)
    ↓
Tailwind CSS 4 (Utility-first styling, dark/light themes)
```

### Component Inventory

| Component | Base | Usage |
|-----------|------|-------|
| **Button** | Radix | Primary/secondary/ghost/destructive variants |
| **Card** | Custom | Content containers with shadow/border |
| **Dialog** | Radix Dialog | Modals, confirmations, forms |
| **DropdownMenu** | Radix Menu | Navigation, action menus |
| **Form** | Radix + react-hook-form | Validated form components |
| **Input** | Custom | Text inputs, textareas |
| **Select** | Radix Select | Dropdown selection |
| **Table** | TanStack Table (headless) | Sortable, filterable data tables |
| **Tabs** | Radix Tabs | Content organization |
| **Sheet** | Radix Dialog | Side panels, drawers |
| **Toast** | Sonner | Notifications |
| **Tooltip** | Radix Tooltip | Hover information |

### Theme System (next-themes)

```typescript
import { ThemeProvider } from "next-themes"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  )
}

// CSS custom properties toggle via class="dark" on <html>
```

### Icons

- **lucide-react** — Primary icon library (~1000+ icons)

### Animation

- `tw-animate-css` — Tailwind animation utilities
- CSS keyframes for entrance/exit transitions

## 2. Drag-and-Drop (dnd-kit)

### Architecture

`@dnd-kit` provides accessible, customizable drag-and-drop:

| Package | Purpose |
|---------|---------|
| `@dnd-kit/core` | Core DnD engine |
| `@dnd-kit/sortable` | Sortable list primitives |
| `@dnd-kit/modifiers` | Constraint modifiers (axis lock, grid snap) |
| `@dnd-kit/accessibility` | Screen reader and keyboard support |

### Exam Builder Pattern

The drag-and-drop exam builder enables educators to construct quizzes by dragging question components into a canvas:

```typescript
import { DndContext, closestCenter } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

// Sortable question item
function SortableQuestion({ id, question }: { id: string; question: Question }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <QuestionCard question={question} />
    </div>
  )
}

// Canvas with sortable questions
function ExamCanvas({ questions }: { questions: Question[] }) {
  const [items, setItems] = useState(questions)

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (over && active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex((q) => q.id === active.id)
        const newIndex = items.findIndex((q) => q.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={items.map(q => q.id)} strategy={verticalListSortingStrategy}>
        {items.map((q) => <SortableQuestion key={q.id} id={q.id} question={q} />)}
      </SortableContext>
    </DndContext>
  )
}
```

### Question Types Supported
- Multiple choice (radio buttons)
- Multiple answer (checkboxes)
- True/False
- Short answer (text input)
- Essay (rich text with Tiptap editor)
- Drag-and-drop matching
- Fill in the blank
- Voice response (audio recording)

### Component Palette Pattern

```
┌──────────────────────────────────────────────────────┐
│  Question Palette        │  Quiz Canvas               │
│  (available types)       │  (assembled questions)     │
│                          │                            │
│  [Multiple Choice]       │  Q1: What is...?           │
│  [True/False]            │  Q2: Which of the...?      │
│  [Short Answer]          │  Q3: Explain why...        │
│  [Essay]                 │                            │
│  [Fill in Blank]         │                            │
│  [Voice Response]        │                            │
│                          │                            │
│  Drag types from left    │  Reorder by dragging       │
│  onto the canvas →       │  within the canvas         │
└──────────────────────────────────────────────────────┘
```

## 3. CopilotKit: AI Agent UI

CopilotKit provides React components for integrating AI agents into the UI.

### Core Components

```typescript
import { CopilotKit, CopilotChat, CopilotTextarea } from "@copilotkit/react-core"

// Wrap app with provider
function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      {children}
    </CopilotKit>
  )
}

// Chat interface (floating or embedded)
<CopilotChat
  labels={{ title: "Learning Assistant", initial: "Hi! Ask me anything about the lesson." }}
/>

// AI-enhanced text areas
<CopilotTextarea
  placeholder="Write your answer..."
  autosuggestionsConfig={{ textareaPurpose: "Essay response for Leaving Cert history" }}
/>
```

### Generative UI

CopilotKit enables agents to render React components dynamically:

```typescript
import { useCopilotAction } from "@copilotkit/react-core"

// Agent can render a quiz card
useCopilotAction({
  name: "render_quiz",
  description: "Display a quiz question to the student",
  parameters: [
    { name: "question", type: "string" },
    { name: "options", type: "string[]" },
    { name: "correctIndex", type: "number" },
  ],
  render: ({ args }) => <QuizCard question={args.question} options={args.options} />,
})
```

### MCP-UI Integration

MCP-UI extends the Model Context Protocol to include UI resources:

```typescript
// Server-side MCP tool that returns UI
const quizTool = {
  name: "get_node_challenge",
  description: "Generate a curriculum challenge for the current node",
  returns: {
    type: "ui",
    component: "QuizComponent",
    render: "inline_html" // or "external_url"
  }
}

// Client renders the UI resource
<MCPRenderer tool={quizTool} context={{ playerProgress, curriculumNode }} />
```

### AG-UI Protocol

The open Agent User Interaction protocol standardizes agent↔UI communication:

| Event | Description |
|-------|-------------|
| `text` | Streaming text response |
| `tool_call` | Agent invoking a tool |
| `tool_result` | Tool execution result |
| `agent_handoff` | Sub-agent delegation |
| `done` | Stream complete |

## 4. Data Visualization

### TanStack React Table

Headless table library for sortable, filterable data tables:

```typescript
import { useReactTable, getCoreRowModel, getSortedRowModel } from "@tanstack/react-table"

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})
```

### Charts (Recharts)

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

<LineChart width={600} height={300} data={progressData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="week" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="score" stroke="#8884d8" />
</LineChart>
```

## 5. Game Interface Patterns

### Player Dashboard
- **Soul Level**: Progress visualization with Celtic knotwork styling
- **Tuath Balance**: Token display with animated counter
- **Active Geasa**: Taboo/challenge status cards
- **Anam Cara Bonds**: Social connection network view

### Map Interface
- Real-world British Isles overlay (Leaflet/MapLibre)
- Zone unlocking based on proficiency
- Live weather integration (Met Éireann, BBC)

### Assessment Interface
- MCP-UI embedded quizzes
- Voice input (Oracy Mining)
- Handwriting capture (Translation Mining — PDF.js for rendering)

### NFT Gallery
- Dynamic Cúchulainn avatar evolution
- Artifact collection grid
- Achievement badge display

## 6. Frontend Idea Catalog

Feature ideas documented for the educational web platform:

| Feature | Status | Priority |
|---------|--------|----------|
| Interactive curriculum map (Pokémon Go-style) | Planned | High |
| AI tutor chat (CopilotKit) | Implemented | High |
| Drag-and-drop quiz builder | Implemented | High |
| Voice-based language practice | Research | Medium |
| Handwriting recognition integration | Research | Medium |
| Collaborative whiteboard | Planned | Medium |
| Real-time leaderboard | Planned | Low |
| Achievement badge system | Planned | Low |

## 7. Asset Management

### File Upload Pattern (Convex)

```typescript
// Generate upload URL
export const generateUploadUrl = mutation(async (ctx) => {
  return await ctx.storage.generateUploadUrl()
})

// Client upload
const uploadUrl = await generateUploadUrl()
const result = await fetch(uploadUrl, {
  method: "POST",
  headers: { "Content-Type": file.type },
  body: file,
})
const { storageId } = await result.json()

// Retrieve file URL
const url = await ctx.storage.getUrl(storageId)
```

### 3D Asset Pipeline
- Blender → glTF export
- Babylon.js for web rendering
- Godot 4 for native clients
- Multi-engine export: .tres, .tscn, .prefab, .uasset, .babylon

## 8. Design Tokens & Inspiration

Design patterns studied from leading products:

| Source | Pattern | Applied To |
|--------|---------|------------|
| **Khan Academy** | Learning path visualization, progress rings | Curriculum map |
| **Duolingo** | Gamification: streaks, XP, crowns | Motivation system |
| **Hades** | Color palette, typography, atmospheric UI | Celtic MMO theme |
| **MotherDuck** | Data visualization, clean dashboard layouts | Analytics views |
| **PostHog** | Feature flags, progressive disclosure UX | Admin panels |

### Celtic Design Language
- **Color Palette**: Deep greens, gold/amber, stone grays
- **Typography**: Serif headers (Cinzel/Cormorant) + sans-serif body
- **Borders & Dividers**: Subtle knotwork-inspired patterns
- **Iconography**: Triskele, spiral, and Ogham-inspired symbols

## 9. Development Workflow

```bash
# Add shadcn components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add table

# Component locations
src/components/ui/     # shadcn base components
src/components/        # Custom composed components

# Styling
src/styles.css         # Tailwind directives + CSS custom properties
```

### Accessibility Standards
- All components built on Radix UI (WCAG 2.1 AA compliant primitives)
- Keyboard navigation support
- Screen reader labels via `@dnd-kit/accessibility`
- Focus management for modals and dialogs
- ARIA attributes automatically managed by Radix
