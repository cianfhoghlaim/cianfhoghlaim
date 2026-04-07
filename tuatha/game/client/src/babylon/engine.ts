/**
 * Babylon.js Engine Setup
 *
 * WebGPU with WebGL2 fallback for the Tuath Celtic MMO web client.
 * Matches rendering capabilities with Godot client for visual parity.
 */

import {
  Engine,
  WebGPUEngine,
  Scene,
  Color4,
  type AbstractEngine,
} from '@babylonjs/core';

export interface EngineConfig {
  /** Target canvas element */
  canvas: HTMLCanvasElement;
  /** Preferred renderer - auto will try WebGPU first */
  renderer?: 'webgpu' | 'webgl2' | 'auto';
  /** Target FPS (default: 60) */
  targetFps?: number;
  /** Enable anti-aliasing (default: true) */
  antialias?: boolean;
  /** Adaptive pixel ratio for performance (default: true) */
  adaptivePixelRatio?: boolean;
  /** Enable debug inspector in dev mode */
  enableInspector?: boolean;
}

export interface GameEngine {
  engine: AbstractEngine;
  scene: Scene;
  start: () => void;
  stop: () => void;
  dispose: () => void;
  isWebGPU: boolean;
}

/**
 * Creates the Babylon.js game engine with WebGPU/WebGL2 fallback
 */
export async function createGameEngine(config: EngineConfig): Promise<GameEngine> {
  const {
    canvas,
    renderer = 'auto',
    targetFps = 60,
    antialias = true,
    adaptivePixelRatio = true,
    enableInspector = false,
  } = config;

  let engine: AbstractEngine;
  let isWebGPU = false;

  // Try WebGPU first if auto or explicitly requested
  if (renderer === 'webgpu' || renderer === 'auto') {
    const webGPUSupported = await WebGPUEngine.IsSupportedAsync;

    if (webGPUSupported) {
      try {
        engine = new WebGPUEngine(canvas, {
          antialias,
          adaptToDeviceRatio: adaptivePixelRatio,
          stencil: true,
          powerPreference: 'high-performance',
        });
        await (engine as WebGPUEngine).initAsync();
        isWebGPU = true;
        console.log('[Tuath] WebGPU engine initialized');
      } catch (error) {
        console.warn('[Tuath] WebGPU init failed, falling back to WebGL2:', error);
      }
    }
  }

  // Fallback to WebGL2
  if (!engine!) {
    engine = new Engine(canvas, antialias, {
      adaptToDeviceRatio: adaptivePixelRatio,
      stencil: true,
      preserveDrawingBuffer: true,
      powerPreference: 'high-performance',
    });
    console.log('[Tuath] WebGL2 engine initialized');
  }

  // Create the main scene with Celtic sky color
  const scene = new Scene(engine);
  scene.clearColor = new Color4(0.2, 0.3, 0.4, 1); // Celtic twilight blue

  // FPS limiting for consistent 60fps
  const frameInterval = 1000 / targetFps;
  let lastFrameTime = 0;

  // Set up the render loop with FPS limiting
  let isRunning = false;

  const renderLoop = () => {
    const currentTime = performance.now();
    const deltaTime = currentTime - lastFrameTime;

    if (deltaTime >= frameInterval) {
      lastFrameTime = currentTime - (deltaTime % frameInterval);
      scene.render();
    }
  };

  // Handle canvas resize
  const resizeObserver = new ResizeObserver(() => {
    engine.resize();
  });
  resizeObserver.observe(canvas);

  // Handle window focus/blur for performance
  const handleVisibilityChange = () => {
    if (document.hidden) {
      engine.stopRenderLoop();
    } else if (isRunning) {
      engine.runRenderLoop(renderLoop);
    }
  };
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // Enable inspector in development
  if (enableInspector && import.meta.env?.DEV) {
    import('@babylonjs/inspector').then(() => {
      scene.debugLayer.show({
        embedMode: true,
        overlay: true,
      });
    });
  }

  return {
    engine,
    scene,
    isWebGPU,

    start() {
      isRunning = true;
      engine.runRenderLoop(renderLoop);
    },

    stop() {
      isRunning = false;
      engine.stopRenderLoop();
    },

    dispose() {
      isRunning = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      resizeObserver.disconnect();
      scene.dispose();
      engine.dispose();
    },
  };
}

/**
 * Get renderer info for debugging
 */
export function getRendererInfo(engine: AbstractEngine): string {
  if (engine instanceof WebGPUEngine) {
    return `WebGPU (${(engine as WebGPUEngine).description})`;
  }

  const gl = (engine as Engine)._gl;
  const debugInfo = gl?.getExtension('WEBGL_debug_renderer_info');
  if (debugInfo) {
    const renderer = gl?.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    return `WebGL2 (${renderer})`;
  }

  return 'WebGL2';
}
