import { afterEach, vi, beforeEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Mock sql-workbench-embedded module
vi.mock('sql-workbench-embedded', () => ({
  default: {}
}));

// Mock window.SQLWorkbench globally
beforeEach(() => {
  // Create a proper mock class for Embedded
  class MockEmbedded {
    destroy = vi.fn();
    isDestroyed = vi.fn().mockReturnValue(false);
    getContainer = vi.fn().mockReturnValue(null);

    constructor(_element: HTMLElement, options?: any) {
      // Mock constructor - simulate async initialization
      setTimeout(() => {
        // This simulates the library calling onReady after initialization
        if (options?.onReady) {
          options.onReady(this);
        }
      }, 0);
    }
  }

  // Mock window.SQLWorkbench
  Object.defineProperty(window, 'SQLWorkbench', {
    value: {
      config: vi.fn(),
      init: vi.fn(),
      destroy: vi.fn(),
      getConfig: vi.fn().mockReturnValue({}),
      Embedded: MockEmbedded as any
    },
    writable: true,
    configurable: true
  });
});

// Cleanup after each test case
afterEach(() => {
  cleanup();
});
