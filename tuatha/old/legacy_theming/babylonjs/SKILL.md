---
name: babylonjs
description: Babylon.js 3D rendering engine for WebGL + WebGPU. Use for the agents/tuatha/game/ MMO client (interactive 3D learning environments, mathematical visualisations, Celtic language family tree, gamified study areas), physics simulations, particle VFX, and VR/AR experiences.
---

# Babylon.js — 3D Web Rendering Engine

## When to use this skill

Use when you need to:

- "Render a 3D classroom / mathematical scene for the Tuatha
  MMO"
- "Build an interactive 3D visualisation of the Celtic
  language family tree"
- "Add physics-based interactions (projectile motion, force
  diagrams) to a study environment"
- "Add particle VFX for correct/incorrect answer feedback"
- "Enable WebGPU on modern devices for hardware-accelerated
  rendering"
- "Import .glb / .gltf 3D models into a web app"

## Overview

[Babylon.js](https://www.babylonjs.com/) is an open-source 3D
rendering engine for the web, maintained by Microsoft. It
provides a complete toolkit for building interactive 3D
experiences in the browser:

- **WebGL + WebGPU** — automatic fallback; WebGPU when
  available, WebGL otherwise
- **Havok physics** — production-grade physics engine
  (Microsoft-owned, fast, stable)
- **GLTF 2.0** — `.glb` / `.gltf` 3D models with PBR materials,
  skinning, and animation
- **Particle systems** — GPU-accelerated particle VFX for
  sparks, smoke, fire, etc.
- **Spatial audio** — 3D-positioned audio
- **VR / AR** — WebXR support for VR and AR experiences
- **Babylon.js Inspector** — in-browser scene inspector (F12)

## When NOT to use this skill

- The project needs 2D only (use HTML canvas + DOM, or
  PixiJS for canvas-based 2D)
- The project is React Native / native mobile (use
  React Native Skia or Three.js for native)
- The project is server-side rendering (use a Node canvas
  library)

## KCG integration

The `agents/tuatha/game/` MMO client uses Babylon.js to render
interactive 3D learning environments:

- **Virtual classroom** — students explore mathematical concepts
  spatially (e.g. 3D function graph, parametric surface,
  geometric solid)
- **Celtic language family tree** — 3D graph of the
  Brythonic / Goidelic / Pictish branches, with click-to-explore
- **Gamified study areas** — correct answers unlock new 3D
  regions; particle VFX on success

The Babylon.js client integrates with:

- **Convex** — real-time state sync (NPC positions, dialogue,
  asset updates)
- **Dagster** — the asset pipeline that ingests 3D models
  (`.glb`) and embeds metadata (BAML extraction of the
  scene's pedagogical content)
- **LiteLLM** — NPC dialogue via the LLM gateway
- **BAML** — typed extraction of pedagogical content from
  scene assets

## Core patterns

### Minimal scene

```typescript
import {
  Engine, Scene, ArcRotateCamera, HemisphericLight, Vector3, MeshBuilder
} from "@babylonjs/core";

const canvas = document.getElementById("renderCanvas") as HTMLCanvasElement;
const engine = new Engine(canvas, true);

const scene = new Scene(engine);
scene.clearColor = new Color4(0.1, 0.1, 0.2, 1);

const camera = new ArcRotateCamera(
  "camera",
  -Math.PI / 2,  // alpha
  Math.PI / 3,   // beta
  10,            // radius
  new Vector3(0, 0, 0),  // target
  scene
);
camera.attachControl(canvas, true);

const light = new HemisphericLight("light", new Vector3(0, 1, 0), scene);
light.intensity = 0.7;

const box = MeshBuilder.CreateBox("box", { size: 2 }, scene);
box.position.y = 1;

engine.runRenderLoop(() => {
  scene.render();
});

window.addEventListener("resize", () => engine.resize());
```

### GLTF 2.0 model loading

```typescript
import { SceneLoader } from "@babylonjs/core";
import "@babylonjs/loaders/glTF";

SceneLoader.ImportMeshAsync(
  ["", "scene.gltf"],  // model URL
  "/assets/models/",   // root
  scene,
  (meshes) => {
    // The scene's root mesh
    const root = meshes[0];
    root.position.x = 5;
  },
);
```

### Havok physics

```typescript
import HavokPhysics from "@babylonjs/havok";

const havok = await HavokPhysics();
const physicsPlugin = new HavokPlugin(true, scene, havok);
scene.enablePhysics(new Vector3(0, -9.81, 0), physicsPlugin);

const ball = MeshBuilder.CreateSphere("ball", { diameter: 1 }, scene);
ball.position.y = 5;

const ballAggregate = new PhysicsAggregate(
  ball,
  PhysicsShapeType.SPHERE,
  { mass: 1, restitution: 0.6 },
  scene
);
// ball falls and bounces (gravity = -9.81 m/s²)
```

### Particle systems

```typescript
import { ParticleSystem, Texture } from "@babylonjs/core";

const particles = new ParticleSystem("particles", 2000, scene);
particles.particleTexture = new Texture("textures/flare.png", scene);
particles.emitter = new Vector3(0, 1, 0);
particles.minEmitBox = new Vector3(-1, 0, 0);
particles.maxEmitBox = new Vector3(1, 0, 0);
particles.color1 = new Color4(1, 0.5, 0, 1);
particles.color2 = new Color4(1, 0, 0, 1);
particles.colorDead = new Color4(0, 0, 0, 0);
particles.minSize = 0.1;
particles.maxSize = 0.3;
particles.minLifeTime = 0.5;
particles.maxLifeTime = 1.5;
particles.emitRate = 500;
particles.start();
```

### WebGPU enablement

```typescript
import { EngineFactory } from "@babylonjs/core/Engines/engineFactory";

const engine = await EngineFactory.CreateAsync(canvas, {
  engineOptions: {
    // enable WebGPU
    adaptToDeviceRatio: true,
    antialias: true,
  },
});

if (engine.webGLVersion === 0) {
  // WebGL 1 — fallback
  // ...
} else if (engine.webGLVersion === 2) {
  // WebGL 2
  // ...
}

// Babylon.js v7+ auto-detects WebGPU support;
// the engine uses WebGPU when available, WebGL 2 otherwise.
```

## Performance

| Technique | Use case |
|:--|:--|:--|
| **Instancing** | Render thousands of identical objects (NPCs, grass blades) with 1 draw call |
| **LOD (level of detail)** | Swap high-poly meshes for low-poly at distance |
| **Frustum culling** | Don't draw objects outside the camera view (default) |
| **Occlusion culling** | Don't draw objects hidden behind other objects (advanced) |
| **Texture compression (KTX2 / Basis)** | 10× smaller textures, GPU-native decompression |
| **Mesh LOD + automatic** | Babylon.js v7+ auto-generates LODs from a single mesh |
| **Freeze materials / worlds** | Pre-bake lighting for static scenes |

## Asset pipeline

For loading 3D models into the Tuatha game:

1. **Source** — `.blend` (Blender), `.fbx` (Maya), or
   `.glb`/`.gltf` (recommended for web)
2. **Compression** — convert textures to KTX2 / Basis for
   smaller payloads
3. **Optimization** — Draco mesh compression (built into
   GLTF 2.0)
4. **Storage** — `agents/tuatha/game/assets/models/` (committed) or
   S3 (for large assets)
5. **Loading** — `SceneLoader.ImportMeshAsync` in the client
6. **Metadata** — BAML extraction of pedagogical content
   (mathematical concept, language family, etc.) stored
   alongside the asset

## Tooling

- **Babylon.js Playground** — <https://playground.babylonjs.com/>
  (in-browser scene editor)
- **Babylon.js Inspector** — F12 in the game, click "Inspector"
  tab to inspect the scene
- **Babylon.js Sandbox** — <https://sandbox.babylonjs.com/>
  (full playground + asset import)
- **glTF Viewer** — <https://gltf-viewer.donmccurdy.com/> (test
  your GLTF assets in isolation)

## Project structure (KCG `agents/tuatha/game/`)

```
agents/tuatha/game/
├── src/
│   ├── main.ts              # entry point; bootstraps the Engine
│   ├── scenes/              # one file per scene (classroom, etc.)
│   │   ├── ClassroomScene.ts
│   │   ├── FamilyTreeScene.ts
│   │   └── StudyAreaScene.ts
│   ├── components/          # reusable 3D components
│   ├── physics/             # Havok setup
│   ├── particles/           # particle VFX
│   ├── state/               # Convex real-time sync
│   ├── llm/                 # LiteLLM NPC dialogue
│   ├── baml/                # BAML extraction of scene content
│   └── audio/               # spatial audio
├── assets/
│   ├── models/              # .glb / .gltf
│   ├── textures/            # .png / .ktx2
│   └── audio/               # .mp3 / .ogg
├── public/                  # static files
└── index.html
```

## Best practices

1. **Use `ArcRotateCamera` for most use cases** — first-person
   cameras are harder to control and less intuitive for
   students
2. **Enable WebGPU via `EngineFactory.CreateAsync`** — Babylon.js
   v7+ auto-detects WebGPU support
3. **Compress textures to KTX2** — 10× smaller files, GPU-native
   decompression
4. **Use Havok for physics** — it's the most stable + performant
   option; Cannon.js is the older alternative
5. **Use GLTF 2.0 for 3D models** — `.glb` (binary, single file)
   is the most common format
6. **Cap draw calls** — use instancing for repeated objects
7. **Profile with the Babylon.js Inspector** — F12, "Inspector"
   tab — shows draw call count, GPU memory, frame budget
8. **Lazy-load scenes** — only the current scene is loaded;
   unload other scenes to free GPU memory

## Common pitfalls

- **Z-fighting** — two meshes at the same depth. Fix with
  `mesh.position.z += 0.001` or render order
- **Texture bleeding** — UV coordinates that span multiple
  textures. Fix with proper UV mapping
- **Performance drop on mobile** — Havok physics is
  GPU-accelerated; disable physics for low-end devices
- **WebGPU not available** — Babylon.js auto-falls-back to
  WebGL 2; test both
- **GLTF import errors** — usually a missing texture or a
  malformed .gltf file; use gltf-viewer to debug

## Cross-references

- `.agents/skills/tuatha-platform/SKILL.md` — the parent
  Tuatha MMO skill
- `.agents/skills/copilotkit/SKILL.md` — for in-game chat /
  NPC dialogue
- `.agents/skills/baml/SKILL.md` — for BAML extraction of
  scene content
- `.agents/skills/dagster/SKILL.md` — for the asset pipeline
  that ingests 3D models
- Related: `.agents/skills/threejs/SKILL.md` (if it exists in
  your project) for the Three.js alternative

## Resources

- Babylon.js docs: <https://doc.babylonjs.com/>
- Babylon.js Playground: <https://playground.babylonjs.com/>
- GLTF spec: <https://github.com/KhronosGroup/glTF>
- Havok: <https://www.havok.com/>
- KCG `agents/tuatha/game/`: the canonical Babylon.js client
