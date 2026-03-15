// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import type {
  EmbeddedOptions,
  SQLWorkbenchEmbeddedInstance,
  Theme
} from '../types';

export interface SQLWorkbenchEmbeddedProps {
  /**
   * Initial SQL code to display in the workbench
   */
  initialCode?: string;

  /**
   * Theme for the workbench ('light', 'dark', 'auto', or custom theme name)
   * @default 'auto'
   */
  theme?: Theme;

  /**
   * Whether the SQL editor is editable
   * @default true
   */
  editable?: boolean;

  /**
   * Show "Open in SQL Workbench" button
   * @default true
   */
  showOpenButton?: boolean;

  /**
   * Custom className for the container element
   */
  className?: string;

  /**
   * Custom styles for the container element
   */
  style?: React.CSSProperties;

  /**
   * Callback fired when the workbench instance is ready
   */
  onReady?: (instance: SQLWorkbenchEmbeddedInstance) => void;

  /**
   * Callback fired when there's an error initializing the workbench
   */
  onError?: (error: Error) => void;
}

export interface SQLWorkbenchEmbeddedRef {
  /**
   * Get the underlying SQLWorkbench instance
   */
  getInstance: () => SQLWorkbenchEmbeddedInstance | null;

  /**
   * Get the container element
   */
  getElement: () => HTMLDivElement | null;
}

/**
 * React wrapper component for sql-workbench-embedded
 *
 * @example
 * ```tsx
 * import { SQLWorkbenchEmbedded } from 'react-sql-workbench-embedded';
 *
 * function MyComponent() {
 *   return (
 *     <SQLWorkbenchEmbedded
 *       initialCode="SELECT * FROM generate_series(1, 10);"
 *       theme="dark"
 *       editable={true}
 *     />
 *   );
 * }
 * ```
 */
export const SQLWorkbenchEmbedded = forwardRef<
  SQLWorkbenchEmbeddedRef,
  SQLWorkbenchEmbeddedProps
>(({
  initialCode = '',
  theme = 'auto',
  editable = true,
  showOpenButton = true,
  className = '',
  style,
  onReady,
  onError
}, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<SQLWorkbenchEmbeddedInstance | null>(null);
  const isInitializedRef = useRef(false);

  useImperativeHandle(ref, () => ({
    getInstance: () => instanceRef.current,
    getElement: () => containerRef.current
  }));

  useEffect(() => {
    let isMounted = true;

    const initWorkbench = async () => {
      if (!containerRef.current || isInitializedRef.current) {
        return;
      }

      try {
        // Dynamically import sql-workbench-embedded
        await import('sql-workbench-embedded');

        // Check if component was unmounted during async operation
        if (!isMounted || !containerRef.current) {
          return;
        }

        // Wait for SQLWorkbench to be available on window
        if (!window.SQLWorkbench) {
          throw new Error('SQLWorkbench not found on window object');
        }

        // Ensure styles are injected by calling init
        // This is safe to call multiple times - it checks if styles already exist
        window.SQLWorkbench.init();

        const options: Partial<EmbeddedOptions> = {
          initialCode,
          theme,
          editable,
          showOpenButton
        };

        // Create the embedded instance
        instanceRef.current = new window.SQLWorkbench.Embedded(
          containerRef.current,
          options
        );

        isInitializedRef.current = true;

        if (isMounted && onReady && instanceRef.current) {
          onReady(instanceRef.current);
        }
      } catch (error) {
        if (!isMounted) return;

        const err = error instanceof Error ? error : new Error(String(error));
        console.error('Failed to initialize SQL Workbench:', err);
        if (onError) {
          onError(err);
        }
      }
    };

    initWorkbench();

    // Cleanup function
    return () => {
      isMounted = false;

      // Don't call destroy() - it tries to remove the container from DOM
      // but React is already handling the DOM cleanup, which causes
      // "Failed to execute 'removeChild'" errors.
      // The library's destroy() just does: this.container?.remove()
      // React will clean up the DOM elements automatically.
      isInitializedRef.current = false;
      instanceRef.current = null;
    };
  }, [initialCode, theme, editable, showOpenButton, onReady, onError]);

  return (
    <div className={className} style={style}>
      <div
        ref={containerRef}
        className="sql-workbench-embedded"
        data-theme={theme}
      >
        {initialCode}
      </div>
    </div>
  );
});

SQLWorkbenchEmbedded.displayName = 'SQLWorkbenchEmbedded';
