import { describe, it, expect, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { SQLWorkbenchProvider, useSQLWorkbench } from '../SQLWorkbenchProvider';

describe('SQLWorkbenchProvider', () => {

  it('renders children', () => {
    render(
      <SQLWorkbenchProvider>
        <div>Test Child</div>
      </SQLWorkbenchProvider>
    );

    expect(screen.getByText('Test Child')).toBeDefined();
  });

  it('calls window.SQLWorkbench.init() on mount', async () => {
    const initMock = vi.fn();
    window.SQLWorkbench!.init = initMock;

    render(
      <SQLWorkbenchProvider>
        <div>Content</div>
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(initMock).toHaveBeenCalled();
  });

  it('applies global configuration', async () => {
    const configMock = vi.fn();
    window.SQLWorkbench!.config = configMock;

    const config = {
      theme: 'dark',
      editable: false,
      initQueries: ['SELECT 1;']
    };

    render(
      <SQLWorkbenchProvider config={config}>
        <div>Content</div>
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(configMock).toHaveBeenCalledWith(
      expect.objectContaining({
        autoInit: false,
        theme: 'dark',
        editable: false,
        initQueries: ['SELECT 1;']
      })
    );
  });

  it('calls onReady callback when initialized', async () => {
    const onReady = vi.fn();

    render(
      <SQLWorkbenchProvider onReady={onReady}>
        <div>Content</div>
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(onReady).toHaveBeenCalled();
  });

  it('handles initialization errors', async () => {
    const onError = vi.fn();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Force an error by removing SQLWorkbench
    delete (window as any).SQLWorkbench;

    render(
      <SQLWorkbenchProvider onError={onError}>
        <div>Content</div>
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({
        message: expect.stringContaining('SQLWorkbench not found')
      })
    );

    consoleSpy.mockRestore();
  });

  it('provides context to children', async () => {
    let contextValue: any;

    function TestComponent() {
      contextValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    render(
      <SQLWorkbenchProvider>
        <TestComponent />
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(contextValue).toBeDefined();
    expect(contextValue.isReady).toBe(true);
    expect(contextValue.error).toBe(null);
  });

  it('sets error state on initialization failure', async () => {
    let contextValue: any;
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    function TestComponent() {
      contextValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    // Force an error
    delete (window as any).SQLWorkbench;

    render(
      <SQLWorkbenchProvider>
        <TestComponent />
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(contextValue).toBeDefined();
    expect(contextValue.isReady).toBe(false);
    expect(contextValue.error).not.toBe(null);

    consoleSpy.mockRestore();
  });

  it('does not call config if no config prop provided', async () => {
    const configMock = vi.fn();
    window.SQLWorkbench!.config = configMock;

    render(
      <SQLWorkbenchProvider>
        <div>Content</div>
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(configMock).not.toHaveBeenCalled();
  });
});

describe('useSQLWorkbench', () => {

  it('returns default values when used outside provider', () => {
    let hookValue: any;

    function TestComponent() {
      hookValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    render(<TestComponent />);

    expect(hookValue).toBeDefined();
    expect(hookValue.isReady).toBe(true);
    expect(hookValue.error).toBe(null);
  });

  it('returns context values when used inside provider', async () => {
    let hookValue: any;

    function TestComponent() {
      hookValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    render(
      <SQLWorkbenchProvider>
        <TestComponent />
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(hookValue).toBeDefined();
    expect(hookValue.isReady).toBe(true);
    expect(hookValue.error).toBe(null);
  });

  it('reflects loading state during initialization', () => {
    let hookValue: any;

    function TestComponent() {
      hookValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    render(
      <SQLWorkbenchProvider>
        <TestComponent />
      </SQLWorkbenchProvider>
    );

    // Should have initial state before async initialization completes
    expect(hookValue).toBeDefined();
    expect(hookValue.isReady).toBe(false);
    expect(hookValue.error).toBe(null);
  });

  it('provides error information when initialization fails', async () => {
    let hookValue: any;
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    function TestComponent() {
      hookValue = useSQLWorkbench();
      return <div>Test</div>;
    }

    // Force an error
    delete (window as any).SQLWorkbench;

    render(
      <SQLWorkbenchProvider>
        <TestComponent />
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(hookValue).toBeDefined();
    expect(hookValue.isReady).toBe(false);
    expect(hookValue.error).not.toBe(null);
    expect(hookValue.error?.message).toContain('SQLWorkbench not found');

    consoleSpy.mockRestore();
  });

  it('can be used by multiple components', async () => {
    let hookValue1: any;
    let hookValue2: any;

    function TestComponent1() {
      hookValue1 = useSQLWorkbench();
      return <div>Component 1</div>;
    }

    function TestComponent2() {
      hookValue2 = useSQLWorkbench();
      return <div>Component 2</div>;
    }

    render(
      <SQLWorkbenchProvider>
        <TestComponent1 />
        <TestComponent2 />
      </SQLWorkbenchProvider>
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(hookValue1).toBeDefined();
    expect(hookValue2).toBeDefined();
    expect(hookValue1.isReady).toBe(true);
    expect(hookValue2.isReady).toBe(true);
    // Both should have the same state
    expect(hookValue1.isReady).toBe(hookValue2.isReady);
    expect(hookValue1.error).toBe(hookValue2.error);
  });
});
