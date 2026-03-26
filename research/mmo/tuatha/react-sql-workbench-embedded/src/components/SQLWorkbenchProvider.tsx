// @ts-expect-error React import needed for classic JSX runtime
import React, { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { SQLWorkbenchConfig } from '../types';

interface SQLWorkbenchContextValue {
  isReady: boolean;
  error: Error | null;
}

const SQLWorkbenchContext = createContext<SQLWorkbenchContextValue | null>(null);

export interface SQLWorkbenchProviderProps {
  /**
   * Global configuration for SQL Workbench
   */
  config?: SQLWorkbenchConfig;

  /**
   * Children components
   */
  children: ReactNode;

  /**
   * Callback fired when SQL Workbench is ready
   */
  onReady?: () => void;

  /**
   * Callback fired when there's an error loading SQL Workbench
   */
  onError?: (error: Error) => void;
}

/**
 * Provider component for global SQL Workbench configuration
 *
 * @example
 * ```tsx
 * import { SQLWorkbenchProvider } from 'react-sql-workbench-embedded';
 *
 * function App() {
 *   return (
 *     <SQLWorkbenchProvider
 *       config={{
 *         theme: 'dark',
 *         editable: true,
 *         initQueries: ['INSTALL spatial', 'LOAD spatial']
 *       }}
 *     >
 *       <YourApp />
 *     </SQLWorkbenchProvider>
 *   );
 * }
 * ```
 */
export function SQLWorkbenchProvider({
  config,
  children,
  onReady,
  onError
}: SQLWorkbenchProviderProps) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const initSQLWorkbench = async () => {
      try {
        // Dynamically import sql-workbench-embedded
        await import('sql-workbench-embedded');

        // Wait for SQLWorkbench to be available on window
        if (!window.SQLWorkbench) {
          throw new Error('SQLWorkbench not found on window object');
        }

        // Apply global configuration if provided
        if (config) {
          window.SQLWorkbench.config({
            autoInit: false, // We'll handle initialization manually in components
            ...config
          });
        }

        // Ensure styles are injected
        window.SQLWorkbench.init();

        setIsReady(true);
        if (onReady) {
          onReady();
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        console.error('Failed to initialize SQL Workbench:', error);
        if (onError) {
          onError(error);
        }
      }
    };

    initSQLWorkbench();
  }, [config, onReady, onError]);

  return (
    <SQLWorkbenchContext.Provider value={{ isReady, error }}>
      {children}
    </SQLWorkbenchContext.Provider>
  );
}

/**
 * Hook to access SQL Workbench context
 *
 * @returns The SQL Workbench context value
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { isReady, error } = useSQLWorkbench();
 *
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (!isReady) return <div>Loading...</div>;
 *
 *   return <SQLWorkbenchEmbedded initialCode="SELECT 1;" />;
 * }
 * ```
 */
export function useSQLWorkbench(): SQLWorkbenchContextValue {
  const context = useContext(SQLWorkbenchContext);

  if (!context) {
    // Return a default context if used outside provider
    return { isReady: true, error: null };
  }

  return context;
}
