// Type alias for the Embedded instance with React-friendly naming
import type { Embedded, SQLWorkbenchConfig } from 'sql-workbench-embedded';

// Re-export types from sql-workbench-embedded
export type {
  SQLWorkbenchConfig,
  EmbeddedOptions,
  Embedded,
  QueryResult
} from 'sql-workbench-embedded';

// Extract theme type from SQLWorkbenchConfig
export type Theme = NonNullable<SQLWorkbenchConfig['theme']>;

// Type alias for the Embedded instance with React-friendly naming
export type SQLWorkbenchEmbeddedInstance = Embedded;

// Extend the Window interface for TypeScript
declare global {
  interface Window {
    SQLWorkbench?: typeof import('sql-workbench-embedded').SQLWorkbench;
  }
}
