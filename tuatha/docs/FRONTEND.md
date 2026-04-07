# TanStack Start Frontend

Documentation for the Tuath Celtic Educational MMO frontend built with TanStack Start.

## Overview

The frontend provides a modern React-based UI for the Celtic educational platform. Built with TanStack Start for SSR (Server-Side Rendering) capabilities and seamless integration with the Babylon.js game client.

### Key Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| TanStack Start | 1.x | SSR React framework |
| TanStack Router | 1.x | File-based routing |
| React Query | 5.x | Server state management |
| Zustand | 5.x | Client state management |
| Tailwind CSS | 3.x | Styling |
| CopilotKit | 1.x | AI agent UI integration |
| wagmi/viem | 2.x | Wallet connection (SIWE) |

---

## Project Structure

```
ui/
├── package.json                    # Dependencies
├── tailwind.config.js              # Tailwind configuration
├── vite.config.ts                  # Vinxi/Vite config
└── src/
    ├── routes/                     # File-based routing
    │   ├── index.tsx               # Landing page (/)
    │   ├── game.tsx                # Game viewport (/game)
    │   ├── map.tsx                 # Interactive map (/map)
    │   ├── mythology.tsx           # Mythology browser (/mythology)
    │   └── learn/
    │       ├── irish.tsx           # Irish lessons (/learn/irish)
    │       ├── gaelic.tsx          # Gaelic lessons (/learn/gaelic)
    │       └── welsh.tsx           # Welsh lessons (/learn/welsh)
    │
    ├── components/                 # React components
    │   ├── auth/
    │   │   └── SIWEConnect.tsx     # Wallet authentication
    │   ├── payment/
    │   │   └── X402Paywall.tsx     # Micropayment UI
    │   └── copilot/
    │       ├── TuathCopilot.tsx    # AI assistant chat
    │       └── A2UIComponents.tsx  # AG-UI render components
    │
    ├── hooks/                      # Custom React hooks
    │   ├── useAuth.ts              # Authentication state
    │   ├── usePayment.ts           # x402 payment handling
    │   ├── useCoAgent.ts           # CopilotKit agent hook
    │   ├── useCurriculumSearch.ts  # Curriculum queries
    │   └── useMythologySearch.ts   # Mythology queries
    │
    └── server/                     # Server functions
        └── ...
```

---

## Routes

### Landing Page (`/`)

The entry point with language selection and feature overview.

```tsx
// routes/index.tsx
import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-900 to-slate-900">
      <header className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl font-bold text-amber-300">Tuath</h1>
        <p className="text-2xl text-emerald-100">
          Fáilte go Tuath • Fàilte gu Tuath • Croeso i Tuath
        </p>
      </header>

      {/* Language selection cards */}
      <div className="grid md:grid-cols-3 gap-8">
        <LanguageCard language="Irish" href="/learn/irish" />
        <LanguageCard language="Scottish Gaelic" href="/learn/gaelic" />
        <LanguageCard language="Welsh" href="/learn/welsh" />
      </div>
    </div>
  );
}
```

### Game Page (`/game`)

The 3D game viewport with Babylon.js integration.

```tsx
// routes/game.tsx
import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useRef, useState } from 'react';
import { initTuathGame, type TuathGame } from '../../game/client/src';
import { useAuth } from '../hooks/useAuth';

export const Route = createFileRoute('/game')({
  component: GamePage,
});

function GamePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<TuathGame | null>(null);
  const { sessionId } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!canvasRef.current) return;

    const initGame = async () => {
      const game = await initTuathGame({
        canvas: canvasRef.current!,
        sessionToken: sessionId,
        initialZone: 'gaeltacht',
        onLoadProgress: (progress) => setLoadProgress(progress),
      });
      gameRef.current = game;
      await game.start();
      setIsLoading(false);
    };

    initGame();
    return () => gameRef.current?.dispose();
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-slate-900">
      {isLoading && <LoadingScreen />}
      <canvas ref={canvasRef} className="w-full h-full" />
      <GameUI />
    </div>
  );
}
```

### Map Page (`/map`)

Interactive Celtic map with MapLibre GL.

```tsx
// routes/map.tsx
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/map')({
  component: MapPage,
});

function MapPage() {
  return (
    <div className="h-screen relative">
      <MapView />
      <MapControls />
      <LocationInfo />
    </div>
  );
}
```

### Mythology Browser (`/mythology`)

Explore Celtic mythology with hybrid search.

```tsx
// routes/mythology.tsx
import { createFileRoute } from '@tanstack/react-router';
import { useMythologySearch } from '../hooks/useMythologySearch';

export const Route = createFileRoute('/mythology')({
  component: MythologyPage,
});

function MythologyPage() {
  const { search, results, isLoading } = useMythologySearch();

  return (
    <div className="container mx-auto px-4 py-8">
      <SearchBar onSearch={search} />
      <CategoryFilter />
      <ResultsGrid results={results} />
    </div>
  );
}
```

### Learning Routes (`/learn/*`)

Language-specific learning paths.

```tsx
// routes/learn/irish.tsx
import { createFileRoute } from '@tanstack/react-router';
import { useCurriculumSearch } from '../../hooks/useCurriculumSearch';

export const Route = createFileRoute('/learn/irish')({
  component: IrishLearningPage,
});

function IrishLearningPage() {
  const { subjects, lessons, search } = useCurriculumSearch('irish');

  return (
    <div className="container mx-auto">
      <h1 className="text-4xl font-bold">Gaeilge</h1>
      <SubjectList subjects={subjects} />
      <LessonCarousel lessons={lessons} />
      <TuathCopilot language="ga" />
    </div>
  );
}
```

---

## Components

### SIWEConnect

Wallet authentication using Sign-In With Ethereum.

```tsx
// components/auth/SIWEConnect.tsx
interface SIWEConnectProps {
  onConnect?: (address: string, sessionId: string) => void;
  onDisconnect?: () => void;
}

export function SIWEConnect({ onConnect, onDisconnect }: SIWEConnectProps) {
  const handleConnect = async () => {
    // 1. Request wallet access
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts',
    });

    // 2. Get nonce from server
    const { nonce } = await fetch('/api/auth/nonce').then(r => r.json());

    // 3. Create and sign SIWE message
    const message = createSiweMessage({ ... });
    const signature = await window.ethereum.request({
      method: 'personal_sign',
      params: [message, accounts[0]],
    });

    // 4. Verify with server
    const { session_id } = await fetch('/api/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ message, signature }),
    }).then(r => r.json());

    onConnect?.(accounts[0], session_id);
  };

  return (
    <button onClick={handleConnect}>
      Connect Wallet
    </button>
  );
}
```

### TuathCopilot

AI assistant integration with CopilotKit/AG-UI.

```tsx
// components/copilot/TuathCopilot.tsx
interface TuathCopilotProps {
  sessionId?: string;
  language?: string;
  languageLevel?: string;
  currentQuest?: string;
  currentZone?: string;
  onPaymentRequired?: () => void;
}

export function TuathCopilot(props: TuathCopilotProps) {
  const {
    isLoading,
    isStreaming,
    messages,
    streamingContent,
    agentState,
    sendMessage,
    reset,
  } = useCoAgent({
    agentEndpoint: '/api/copilot/agent',
    ...props,
  });

  // Render state with custom components
  const stateIndicator = useCoAgentStateRender(agentState, (state) => (
    <XPIndicator xp={state.xpEarned} />
  ));

  return (
    <div className="fixed bottom-4 right-4 w-80">
      <MessageList messages={messages} />
      <StreamingIndicator content={streamingContent} />
      {stateIndicator}
      <ChatInput onSend={sendMessage} />
    </div>
  );
}
```

### X402Paywall

Micropayment UI for premium content.

```tsx
// components/payment/X402Paywall.tsx
interface X402PaywallProps {
  resourceType: string;
  children: React.ReactNode;
  onPaymentComplete?: (paymentId: string) => void;
}

export function X402Paywall({ resourceType, children, onPaymentComplete }: X402PaywallProps) {
  const { requestPayment, submitPayment, checkFreeUsage } = usePayment();
  const [hasFreeUsage, setHasFreeUsage] = useState<boolean | null>(null);

  useEffect(() => {
    checkFreeUsage(resourceType).then(setHasFreeUsage);
  }, [resourceType]);

  if (hasFreeUsage === true) {
    return <>{children}</>;
  }

  return (
    <PaymentModal
      resourceType={resourceType}
      onPay={async () => {
        const payment = await requestPayment(resourceType);
        // Trigger wallet transaction
        const txHash = await sendTransaction(payment);
        await submitPayment(payment.paymentId, txHash);
        onPaymentComplete?.(payment.paymentId);
      }}
    />
  );
}
```

### A2UIComponents

AG-UI protocol render components.

```tsx
// components/copilot/A2UIComponents.tsx

// XP indicator shown during agent responses
export function XPIndicator({ xp, vocabularyCount }: {
  xp: number;
  vocabularyCount: number;
}) {
  return (
    <div className="flex items-center gap-2 text-amber-300">
      <span>+{xp} XP</span>
      <span>{vocabularyCount} words learned</span>
    </div>
  );
}

// Tool call indicator
export function ToolCallIndicator({ toolName, status }: {
  toolName: string;
  status: 'pending' | 'running' | 'complete' | 'error';
}) {
  return (
    <div className={`flex items-center gap-2 ${statusColors[status]}`}>
      <span>{toolIcons[toolName]}</span>
      <span>{toolName}</span>
    </div>
  );
}

// Main A2UI renderer
export function A2UIRenderer({ components }: { components: RenderComponent[] }) {
  return (
    <>
      {components.map((comp, i) => (
        <DynamicComponent key={i} component={comp.component} props={comp.props} />
      ))}
    </>
  );
}
```

---

## Hooks

### useAuth

Authentication state management.

```typescript
// hooks/useAuth.ts
interface AuthState {
  isAuthenticated: boolean;
  sessionId: string | null;
  address: string | null;
  playerId: string | null;
}

export function useAuth(): AuthState & {
  login: (address: string, sessionId: string) => void;
  logout: () => void;
} {
  // Uses Zustand store for persistence
  const store = useAuthStore();

  return {
    ...store,
    login: (address, sessionId) => {
      store.setSession(address, sessionId);
    },
    logout: () => {
      store.clearSession();
    },
  };
}
```

### useCoAgent

CopilotKit agent communication with AG-UI protocol.

```typescript
// hooks/useCoAgent.ts
interface CoAgentOptions {
  agentEndpoint: string;
  sessionId?: string;
  paymentId?: string;
  language?: string;
  languageLevel?: string;
  context?: Record<string, unknown>;
}

interface CoAgentReturn {
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  agentState: AgentState | null;
  messages: AgentMessage[];
  streamingContent: string;
  sidebarComponents: RenderComponent[];
  mainComponents: RenderComponent[];
  overlayComponents: RenderComponent[];
  activeToolCalls: Map<string, ToolCall>;
  sendMessage: (content: string) => void;
  reset: () => void;
}

export function useCoAgent(options: CoAgentOptions): CoAgentReturn {
  // Manages SSE connection to agent endpoint
  // Handles A2UI events: lifecycle, state, tool calls, render components
}

// Render hook for agent state
export function useCoAgentStateRender<T>(
  state: AgentState | null,
  render: (state: AgentState) => T
): T | null {
  return state ? render(state) : null;
}
```

### usePayment

x402 micropayment handling.

```typescript
// hooks/usePayment.ts
interface PaymentState {
  isLoading: boolean;
  error: string | null;
  currentPayment: PaymentRequest | null;
  completedPayments: string[];
}

interface PaymentActions {
  requestPayment: (resourceType: string, token?: string) => Promise<PaymentRequest>;
  submitPayment: (paymentId: string, txHash: string) => Promise<boolean>;
  checkFreeUsage: (resourceType: string, sessionId?: string) => Promise<boolean>;
  clearPayment: () => void;
}

export function usePayment(): PaymentState & PaymentActions {
  // Manages payment flow with API
}
```

### useCurriculumSearch

Curriculum content search with React Query.

```typescript
// hooks/useCurriculumSearch.ts
interface CurriculumSearchOptions {
  subject: 'irish' | 'welsh' | 'scottish_gaelic';
  level?: string;
  topic?: string;
}

export function useCurriculumSearch(subject: string) {
  const subjectsQuery = useQuery({
    queryKey: ['curriculum', 'subjects'],
    queryFn: () => fetch('/api/curriculum/subjects').then(r => r.json()),
  });

  const searchMutation = useMutation({
    mutationFn: (query: string) =>
      fetch(`/api/search/curriculum?q=${query}&subject=${subject}`).then(r => r.json()),
  });

  return {
    subjects: subjectsQuery.data?.subjects ?? [],
    search: searchMutation.mutate,
    results: searchMutation.data?.results ?? [],
    isLoading: searchMutation.isPending,
  };
}
```

### useMythologySearch

Mythology hybrid search (vector + graph).

```typescript
// hooks/useMythologySearch.ts
export function useMythologySearch() {
  const searchMutation = useMutation({
    mutationFn: async (params: {
      query: string;
      mode?: 'vector' | 'graph' | 'hybrid';
      contentTypes?: string[];
    }) => {
      const response = await fetch('/api/search/mythology', {
        method: 'POST',
        body: JSON.stringify(params),
      });
      return response.json();
    },
  });

  return {
    search: searchMutation.mutate,
    results: searchMutation.data?.results ?? [],
    isLoading: searchMutation.isPending,
  };
}
```

---

## State Management

### Zustand Stores

```typescript
// stores/authStore.ts
interface AuthStore {
  sessionId: string | null;
  address: string | null;
  playerId: string | null;
  setSession: (address: string, sessionId: string) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      sessionId: null,
      address: null,
      playerId: null,
      setSession: (address, sessionId) =>
        set({ address, sessionId, playerId: sessionId }),
      clearSession: () =>
        set({ sessionId: null, address: null, playerId: null }),
    }),
    { name: 'tuath-auth' }
  )
);
```

```typescript
// stores/gameStore.ts
interface GameStore {
  currentZone: string | null;
  currentQuest: string | null;
  xp: number;
  level: number;
  setZone: (zone: string) => void;
  addXP: (amount: number) => void;
}

export const useGameStore = create<GameStore>((set) => ({
  currentZone: null,
  currentQuest: null,
  xp: 0,
  level: 1,
  setZone: (zone) => set({ currentZone: zone }),
  addXP: (amount) => set((state) => ({
    xp: state.xp + amount,
    level: calculateLevel(state.xp + amount),
  })),
}));
```

---

## Styling

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        celtic: {
          emerald: '#10b981',
          amber: '#f59e0b',
          slate: '#1e293b',
        },
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
};
```

### Color Scheme

| Color | Tailwind Class | Usage |
|-------|---------------|-------|
| Celtic Emerald | `emerald-500/700/900` | Primary accent, Irish theme |
| Celtic Amber | `amber-300/400/500` | Headers, highlights |
| Deep Slate | `slate-800/900` | Backgrounds |
| Sky Blue | `blue-400/500` | Scottish Gaelic theme |
| Dragon Red | `red-500/600` | Welsh theme |

---

## Development

### Running Locally

```bash
cd sruth/tuath/ui
pnpm install
pnpm dev
```

Frontend available at: http://localhost:3000

### Build

```bash
pnpm build
pnpm start  # Production server
```

### Type Checking

```bash
pnpm typecheck
```

### Linting

```bash
pnpm lint
```

---

## API Integration

### Endpoints Used

| Endpoint | Hook | Description |
|----------|------|-------------|
| `GET /auth/nonce` | useAuth | Get SIWE nonce |
| `POST /auth/verify` | useAuth | Verify SIWE signature |
| `POST /copilotkit/stream` | useCoAgent | Stream agent responses |
| `GET /curriculum/*` | useCurriculumSearch | Get curriculum content |
| `POST /search/mythology` | useMythologySearch | Hybrid search |
| `POST /search/curriculum` | useCurriculumSearch | Curriculum search |
| `POST /payments/request/*` | usePayment | Request payment |
| `POST /payments/verify` | usePayment | Verify payment |

### Error Handling

```typescript
// Centralized error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error.status === 401) return false; // Don't retry auth errors
        if (error.status === 402) return false; // Don't retry payment required
        return failureCount < 3;
      },
    },
  },
});
```

---

## Related Documentation

- [Architecture](./ARCHITECTURE.md) - System overview
- [Game Client](./GAME_CLIENT.md) - Babylon.js integration
- [API Reference](./API.md) - Backend endpoints
- [Agents](./AGENTS.md) - CopilotKit/AG-UI agents
