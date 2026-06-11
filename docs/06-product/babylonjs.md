---
title: 'Babylon.js — 3D Web Rendering Engine'
domain: 'product'
status: 'stable'
description: 'Babylon.js is an open-source 3D rendering engine for the web, built on WebGL and WebGPU. It provides a complete toolkit for building interactive 3D experiences in the browser — physics, particles, animations, spatial audio, and VR/AR support. Maintained by Microsoft, it is one of'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/babylonjs.md
ccc_query_hints:
  - babylon.js — 3d web rendering engine
---

# Babylon.js — 3D Web Rendering Engine

## Overview

Babylon.js is an open-source 3D rendering engine for the web, built on WebGL and WebGPU. It provides a complete toolkit for building interactive 3D experiences in the browser — physics, particles, animations, spatial audio, and VR/AR support. Maintained by Microsoft, it is one of the leading WebGL frameworks alongside Three.js.

## Why This Matters for Kings' College Galway

The `tuatha/` educational MMO frontend uses Babylon.js for rendering interactive 3D learning environments: a virtual classroom where students explore mathematical concepts spatially, a 3D graph of the Celtic language family tree, and gamified study environments where correct answers unlock new areas. Babylon.js's physics engine enables realistic simulations for applied mathematics concepts (projectile motion, force diagrams), and the particle system creates engaging visual feedback for correct/incorrect answers. The WebGPU backend provides hardware-accelerated rendering on modern devices.

## Key Features

- **WebGL + WebGPU** — Hardware-accelerated 3D rendering
- **Physics engine** — Built-in Havok and Cannon.js physics
- **Particle system** — GPU-accelerated particle effects
- **Animation system** — Skeletal, morph target, and property animations
- **VR/AR support** — WebXR integration for immersive experiences

## Installation

```bash
bun add @babylonjs/core
```

## Integration with Our Stack

Babylon.js powers the `tuatha/ui/` 3D educational MMO frontend. It interacts with Convex for real-time game state, Dagster for educational content pipelines, and the LiteLLM gateway for AI-driven NPC dialogue. The BAML extraction pipeline feeds structured curriculum data into interactive 3D visualisations.

## Upstream

- **Repository**: <https://github.com/BabylonJS/Babylon.js>
- **Documentation**: <https://doc.babylonjs.com>
- **Latest**: v7.x (2025) — WebGPU support, performance improvements, new material system, glTF 2.0 enhancements

## Screenshot

Babylon.js's playground at `playground.babylonjs.com` provides a live code editor with 3D scene preview. The inspector tool overlays scene graph, material properties, and performance metrics. The documentation site features interactive 3D demos for each API feature. In the `tuatha/` app, Babylon.js renders the educational 3D environment with camera controls and scene navigation.
