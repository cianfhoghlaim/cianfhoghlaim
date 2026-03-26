# react-sql-workbench-embedded

A React wrapper component for [sql-workbench-embedded](https://github.com/tobilg/sql-workbench-embedded), enabling interactive SQL execution environments powered by DuckDB WASM directly in your React applications.

## Features

- **React 18 & 19 Compatible**: Works with both React 18 and React 19
- **Zero Backend Required**: All SQL execution happens in the browser via DuckDB WASM
- **Type-Safe**: Full TypeScript support with comprehensive type definitions
- **Flexible API**: Use as a simple component or with global configuration via Context Provider
- **Customizable**: Support for themes (light/dark/auto), custom themes, and extensive configuration options
- **Modern Development**: Built with Vite, tested with Vitest
- **Privacy-Focused**: No data leaves the browser
- **Multiple Distribution Formats**: Available as ESM and UMD builds for maximum compatibility
- **CDN-Ready**: Can be used directly from CDN without build tools

## Installation

### Via npm

```bash
npm install react-sql-workbench-embedded
```

### Via CDN (UMD)

```html
<!-- React and ReactDOM (use React 18 for UMD compatibility) -->
<script crossorigin src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js"></script>

<!-- React SQL Workbench Embedded -->
<script src="https://cdn.jsdelivr.net/npm/react-sql-workbench-embedded/dist/react-sql-workbench-embedded.umd.js"></script>

<script>
  const { SQLWorkbenchEmbedded } = window.SQLWorkbenchEmbedded;
  // Use the component...
</script>
```

### Via CDN (ESM with Import Maps)

```html
<script type="importmap">
{
  "imports": {
    "react": "https://cdn.jsdelivr.net/npm/react@18/+esm",
    "react-dom": "https://cdn.jsdelivr.net/npm/react-dom@18/+esm",
    "@duckdb/duckdb-wasm": "https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@1.31.1-dev1.0/+esm",
    "react-sql-workbench-embedded": "https://cdn.jsdelivr.net/npm/react-sql-workbench-embedded/dist/react-sql-workbench-embedded.esm.js"
  }
}
</script>

<script type="module">
  import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';
  // Use the component...
</script>
```

## Quick Start

### Basic Usage (npm)

```tsx
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

function App() {
  return (
    <SQLWorkbenchEmbedded
      initialCode="SELECT * FROM generate_series(1, 10);"
      theme="auto"
      editable={true}
    />
  );
}
```

### With Provider (Global Configuration)

```tsx
import { SQLWorkbenchProvider, SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

function App() {
  return (
    <SQLWorkbenchProvider
      config={{
        theme: 'dark',
        editable: true,
        initQueries: [
          'INSTALL spatial',
          'LOAD spatial'
        ]
      }}
    >
      <SQLWorkbenchEmbedded
        initialCode="SELECT ST_AsText(ST_Point(1, 2)) as point;"
      />
    </SQLWorkbenchProvider>
  );
}
```

## API Reference

### `SQLWorkbenchEmbedded` Component

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `initialCode` | `string` | `''` | Initial SQL code to display in the workbench |
| `theme` | `'light' \| 'dark' \| 'auto' \| string` | `'auto'` | Theme for the workbench |
| `editable` | `boolean` | `true` | Whether the SQL editor is editable |
| `showOpenButton` | `boolean` | `true` | Show "Open in SQL Workbench" button |
| `className` | `string` | `''` | Custom className for the container element |
| `style` | `React.CSSProperties` | - | Custom styles for the container element |
| `onReady` | `(instance) => void` | - | Callback when workbench is ready |
| `onError` | `(error) => void` | - | Callback when initialization fails |

#### Ref API

```tsx
import { useRef } from 'react';
import { SQLWorkbenchEmbedded, type SQLWorkbenchEmbeddedRef } from 'react-sql-workbench-embedded';

function App() {
  const ref = useRef<SQLWorkbenchEmbeddedRef>(null);

  return (
    <SQLWorkbenchEmbedded
      ref={ref}
      initialCode="SELECT 1;"
    />
  );
}
```

Methods available via ref:
- `getInstance()`: Get the underlying SQLWorkbench instance
- `getElement()`: Get the container element

### `SQLWorkbenchProvider` Component

Provides global configuration for all SQLWorkbenchEmbedded components.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| `config` | `SQLWorkbenchConfig` | Global configuration options |
| `children` | `ReactNode` | Child components |
| `onReady` | `() => void` | Callback when SQL Workbench is ready |
| `onError` | `(error) => void` | Callback when initialization fails |

#### Configuration Options

```typescript
interface SQLWorkbenchConfig {
  selector?: string;
  baseUrl?: string;
  theme?: 'light' | 'dark' | 'auto' | string;
  autoInit?: boolean;
  duckdbVersion?: string;
  duckdbCDN?: string;
  editable?: boolean;
  showOpenButton?: boolean;
  initQueries?: string[];
  customThemes?: Record<string, CustomThemeConfig>;
}
```

### `useSQLWorkbench` Hook

Hook to access SQL Workbench context status.

```tsx
import { useSQLWorkbench } from 'react-sql-workbench-embedded';

function MyComponent() {
  const { isReady, error } = useSQLWorkbench();

  if (error) return <div>Error: {error.message}</div>;
  if (!isReady) return <div>Loading...</div>;

  return <SQLWorkbenchEmbedded initialCode="SELECT 1;" />;
}
```

## Usage Examples

### 1. Simple Component

The simplest way to use the component:

```tsx
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <div>
      <h1>My SQL Workbench</h1>
      <SQLWorkbenchEmbedded
        initialCode="SELECT * FROM generate_series(1, 10);"
      />
    </div>
  );
}
```

### 2. With Callbacks

Handle initialization events:

```tsx
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchEmbedded
      initialCode="SELECT 1 + 1 as result;"
      onReady={(instance) => {
        console.log('Workbench ready!', instance);
      }}
      onError={(error) => {
        console.error('Failed to initialize:', error);
      }}
    />
  );
}
```

### 3. Theme Switching

Allow users to switch themes:

```tsx
import { useState } from 'react';
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('auto');

  return (
    <div>
      <select value={theme} onChange={(e) => setTheme(e.target.value)}>
        <option value="auto">Auto</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>

      <SQLWorkbenchEmbedded
        key={theme} // Force remount on theme change
        initialCode="SELECT 'Hello World' as message;"
        theme={theme}
      />
    </div>
  );
}
```

### 4. Using Provider for Multiple Instances

Share configuration across multiple workbenches:

```tsx
import { SQLWorkbenchProvider, SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchProvider
      config={{
        theme: 'dark',
        editable: true
      }}
    >
      <div>
        <h2>Query 1</h2>
        <SQLWorkbenchEmbedded
          initialCode="SELECT 'First Query' as title;"
        />

        <h2>Query 2</h2>
        <SQLWorkbenchEmbedded
          initialCode="SELECT 'Second Query' as title;"
        />
      </div>
    </SQLWorkbenchProvider>
  );
}
```

### 5. Loading DuckDB Extensions

Load extensions for spatial operations:

```tsx
import { SQLWorkbenchProvider, SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchProvider
      config={{
        initQueries: [
          'INSTALL spatial',
          'LOAD spatial'
        ]
      }}
    >
      <SQLWorkbenchEmbedded
        initialCode={`
          SELECT
            ST_AsText(ST_Point(1.5, 2.5)) as point,
            ST_AsText(ST_MakePolygon(
              'LINESTRING(0 0, 0 1, 1 1, 1 0, 0 0)'
            )) as polygon;
        `}
      />
    </SQLWorkbenchProvider>
  );
}
```

### 6. Read-Only Mode

Create a read-only SQL display:

```tsx
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchEmbedded
      initialCode="SELECT * FROM generate_series(1, 100);"
      editable={false}
      showOpenButton={false}
    />
  );
}
```

### 7. Using Refs

Access the underlying instance:

```tsx
import { useRef } from 'react';
import { SQLWorkbenchEmbedded, SQLWorkbenchEmbeddedRef } from 'react-sql-workbench-embedded';

export default function App() {
  const workbenchRef = useRef<SQLWorkbenchEmbeddedRef>(null);

  const handleClick = () => {
    const instance = workbenchRef.current?.getInstance();
    console.log('Current instance:', instance);
  };

  return (
    <div>
      <button onClick={handleClick}>
        Get Instance
      </button>

      <SQLWorkbenchEmbedded
        ref={workbenchRef}
        initialCode="SELECT 1;"
      />
    </div>
  );
}
```

### 8. Loading Data from URLs

Query CSV files from URLs using httpfs extension:

```tsx
import { SQLWorkbenchProvider, SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchProvider
      config={{
        initQueries: [
          'INSTALL httpfs',
          'LOAD httpfs'
        ]
      }}
    >
      <SQLWorkbenchEmbedded
        initialCode={`
          SELECT *
          FROM read_csv_auto('https://example.com/data.csv')
          LIMIT 10;
        `}
      />
    </SQLWorkbenchProvider>
  );
}
```

### 9. Custom Styling

Add custom styles to the workbench:

```tsx
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  return (
    <SQLWorkbenchEmbedded
      initialCode="SELECT * FROM generate_series(1, 5);"
      className="my-custom-workbench"
      style={{
        border: '2px solid #3498db',
        borderRadius: '8px',
        padding: '1rem'
      }}
    />
  );
}
```

### 10. Conditional Rendering with Hook

Use the `useSQLWorkbench` hook to handle loading states:

```tsx
import { SQLWorkbenchProvider, SQLWorkbenchEmbedded, useSQLWorkbench } from 'react-sql-workbench-embedded';

function WorkbenchContent() {
  const { isReady, error } = useSQLWorkbench();

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!isReady) {
    return <div>Loading SQL Workbench...</div>;
  }

  return (
    <SQLWorkbenchEmbedded
      initialCode="SELECT 'Ready!' as status;"
    />
  );
}

export default function App() {
  return (
    <SQLWorkbenchProvider>
      <WorkbenchContent />
    </SQLWorkbenchProvider>
  );
}
```

### 11. Custom Themes

```tsx
<SQLWorkbenchProvider
  config={{
    theme: 'ocean',
    customThemes: {
      ocean: {
        extends: 'dark',
        config: {
          primaryBg: '#0ea5e9',
          editorBg: '#1e3a5f',
          syntaxKeyword: '#4fc3f7'
        }
      }
    }
  }}
>
  <SQLWorkbenchEmbedded initialCode="SELECT 1;" />
</SQLWorkbenchProvider>
```

### 12. Multiple Instances with Different Themes

```tsx
function App() {
  return (
    <div>
      <h2>Light Theme</h2>
      <SQLWorkbenchEmbedded
        initialCode="SELECT 'Hello' as greeting;"
        theme="light"
      />

      <h2>Dark Theme</h2>
      <SQLWorkbenchEmbedded
        initialCode="SELECT 'World' as subject;"
        theme="dark"
      />
    </div>
  );
}
```

## TypeScript Usage

The library is fully typed. Here's how to use types:

```tsx
import { useState, useRef } from 'react';
import type {
  SQLWorkbenchEmbeddedRef,
  SQLWorkbenchConfig,
  Theme
} from 'react-sql-workbench-embedded';

const config: SQLWorkbenchConfig = {
  theme: 'dark',
  editable: true,
  initQueries: ['INSTALL spatial']
};

function MyComponent() {
  const [theme, setTheme] = useState<Theme>('auto');
  const ref = useRef<SQLWorkbenchEmbeddedRef>(null);

  // ... rest of component
}
```

## Common Patterns

### Error Boundaries

Wrap the component in an error boundary:

```tsx
import { Component, ReactNode } from 'react';

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <h2>Something went wrong.</h2>;
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <SQLWorkbenchEmbedded initialCode="SELECT 1;" />
    </ErrorBoundary>
  );
}
```

### Dynamic Code Updates

Update SQL code dynamically:

```tsx
import { useState } from 'react';
import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';

export default function App() {
  const [code, setCode] = useState("SELECT 1;");

  const queries = [
    "SELECT * FROM generate_series(1, 10);",
    "SELECT DATE '2024-01-01' + INTERVAL (n) DAY FROM generate_series(0, 6) t(n);",
    "SELECT 'Hello', 'World';"
  ];

  return (
    <div>
      <div>
        {queries.map((query, idx) => (
          <button key={idx} onClick={() => setCode(query)}>
            Query {idx + 1}
          </button>
        ))}
      </div>

      <SQLWorkbenchEmbedded
        key={code} // Force remount when code changes
        initialCode={code}
      />
    </div>
  );
}
```

## Tips

1. **Force Remount**: Use the `key` prop to force component remount when you want to reset the workbench completely.

2. **Provider vs. Component Config**: Use Provider for shared configuration across multiple instances. Use component props for instance-specific overrides.

3. **Init Queries**: Use `initQueries` to install and load DuckDB extensions. These run once before any user queries.

4. **Theme Priority**: Component prop > HTML attribute > Provider config. Choose the level that makes sense for your use case.

5. **Performance**: The DuckDB WASM runtime is lazy-loaded only when needed, so initial page load stays fast.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/tobilg/react-sql-workbench-embedded.git
cd react-sql-workbench-embedded

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Build the library
npm run build
```

### Project Structure

```
react-sql-workbench-embedded/
├── src/
│   ├── components/
│   │   ├── SQLWorkbenchEmbedded.tsx    # Main component
│   │   ├── SQLWorkbenchProvider.tsx    # Context provider
│   │   └── __tests__/                  # Component tests
│   ├── demo/                           # Demo application
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── types.ts                        # TypeScript types
│   └── index.ts                        # Main entry point
├── vite.config.ts                      # Vite configuration
├── vitest.config.ts                    # Vitest configuration
└── package.json
```

## Requirements

- React 18+ or React 19+
- TypeScript 5.6+ (for development)
- Modern browser with WebAssembly support

## Browser Compatibility

This library requires a modern browser with support for:
- ES Modules (for ESM builds)
- WebAssembly
- Import Maps (for ESM CDN usage)

For the UMD build, all major modern browsers are supported without additional configuration.

## Distribution Formats

This library is distributed in two formats:

### ESM (ES Module)
- **File**: `dist/react-sql-workbench-embedded.esm.js` (~32 KB, ~10 KB gzipped)
- **Use case**: Modern build tools (Vite, Webpack, etc.) or direct browser usage with import maps
- **Dependencies**: Requires React, ReactDOM, and @duckdb/duckdb-wasm to be available

### UMD (Universal Module Definition)
- **File**: `dist/react-sql-workbench-embedded.umd.js` (~31 KB, ~10 KB gzipped)
- **Use case**: Direct browser usage via `<script>` tags or legacy module systems
- **Global**: Exposed as `window.SQLWorkbenchEmbedded`
- **Dependencies**: Requires React and ReactDOM to be loaded first (use React 18 for UMD compatibility)

Both formats:
- Bundle `sql-workbench-embedded` internally (no manual installation needed)
- Externalize React and ReactDOM (expected as peer dependencies)
- Use classic JSX runtime for maximum compatibility
- Include no polyfills (work directly in modern browsers)

## License

MIT
