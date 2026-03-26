import { describe, it, expect, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { SQLWorkbenchEmbedded } from '../SQLWorkbenchEmbedded';

describe('SQLWorkbenchEmbedded', () => {

  it('renders with initial code', () => {
    const initialCode = 'SELECT 1;';
    render(<SQLWorkbenchEmbedded initialCode={initialCode} />);

    const codeElement = screen.getByText(initialCode);
    expect(codeElement).toBeDefined();
  });

  it('applies correct className to wrapper', () => {
    const { container } = render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        className="custom-class"
      />
    );

    // Outer wrapper has the custom className
    const outerDiv = container.firstChild as HTMLElement;
    expect(outerDiv?.classList.contains('custom-class')).toBe(true);

    // Inner div has sql-workbench-embedded class
    const innerDiv = container.querySelector('.sql-workbench-embedded');
    expect(innerDiv).toBeDefined();
  });

  it('sets theme data attribute on inner element', () => {
    const { container } = render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        theme="dark"
      />
    );

    const innerDiv = container.querySelector('.sql-workbench-embedded');
    expect(innerDiv?.getAttribute('data-theme')).toBe('dark');
  });

  it('calls onReady callback when initialized', async () => {
    const onReady = vi.fn();

    render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        onReady={onReady}
      />
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(onReady).toHaveBeenCalled();
  });

  it('creates SQLWorkbench.Embedded instance with correct options', async () => {
    // Track constructor calls
    const constructorSpy = vi.fn();

    class SpyEmbedded {
      destroy = vi.fn();
      isDestroyed = vi.fn().mockReturnValue(false);
      getContainer = vi.fn().mockReturnValue(null);

      constructor(element: HTMLElement, options?: any) {
        constructorSpy(element, options);
      }
    }

    window.SQLWorkbench!.Embedded = SpyEmbedded as any;

    render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        theme="dark"
        editable={false}
        showOpenButton={false}
      />
    );

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(constructorSpy).toHaveBeenCalledWith(
      expect.any(HTMLElement),
      expect.objectContaining({
        initialCode: 'SELECT 1;',
        theme: 'dark',
        editable: false,
        showOpenButton: false
      })
    );
  });

  it('calls init() to inject styles', async () => {
    const initMock = vi.fn();
    window.SQLWorkbench!.init = initMock;

    render(<SQLWorkbenchEmbedded initialCode="SELECT 1;" />);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(initMock).toHaveBeenCalled();
  });

  it('uses wrapper pattern (outer div + inner div)', () => {
    const { container } = render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        className="my-wrapper"
        style={{ padding: '10px' }}
      />
    );

    // Outer div has custom className and style
    const outerDiv = container.firstChild as HTMLElement;
    expect(outerDiv.className).toBe('my-wrapper');
    expect(outerDiv.style.padding).toBe('10px');

    // Inner div is the target for library replacement
    const innerDiv = outerDiv.querySelector('.sql-workbench-embedded');
    expect(innerDiv).toBeDefined();
    expect(innerDiv?.textContent).toContain('SELECT 1;');
  });

  it('handles custom styles on wrapper', () => {
    const customStyle = { backgroundColor: 'blue', margin: '20px' };
    const { container } = render(
      <SQLWorkbenchEmbedded
        initialCode="SELECT 1;"
        style={customStyle}
      />
    );

    const outerDiv = container.firstChild as HTMLElement;
    expect(outerDiv.style.backgroundColor).toBe('blue');
    expect(outerDiv.style.margin).toBe('20px');
  });
});
