# wgpu — KCG Summary

## What It Is
wgpu is a Rust-implemented, safe and portable graphics API that maps to Vulkan, Metal, DX12, WebGPU, and OpenGL. Maintained by the gfx-rs working group, it provides both a native runtime and a browser-native WebGPU implementation. The repo includes the core `wgpu` crate, the `naga` shader translator, HAL backends, and a WebGPU CTS runner.

## Why This Matters for Kings' College Galway
The `tuatha/` educational MMO uses Babylon.js for the 3D frontend, but mesh-shader-heavy scenes (Celtic particle effects, Ogham-stone rendering, procedural terrain) benefit from wgpu's modern GPU features. wgpu is a reference implementation of the WebGPU spec — anything we ship in the browser via `tuatha/ui` Babylon.js backend can be prototyped against wgpu's API surface. The `naga` shader translator is also relevant: it lets us author WGSL/SPIR-V/GLSL once and target every backend, which matters for cross-platform MMO distribution (Mac M-series + Windows + Linux + Web).

## Key Patterns Preserved
- **README.md** — Overview of wgpu, supported backends, quick-start
- **CHANGELOG.md** — Release history including v28.0.0 (Mesh Shaders, Immediates)
- **CODE_OF_CONDUCT.md / GOVERNANCE.md / CONTRIBUTING.md** — Community norms
- **docs/testing.md** — How to run the WebGPU CTS conformance suite
- **docs/release-checklist.md** — Cutting a wgpu release
- **docs/review-checklist.md** — Code review standards
- **docs/api-specs/mesh_shading.md / ray_tracing.md** — API design notes
- **wgpu/README.md** — Core crate docs
- **wgpu-hal/README.md** — Hardware abstraction layer
- **naga/README.md / naga/CHANGELOG.md** — Shader translator
- **wgpu-info/README.md** — Hardware/driver introspection tool
- **deno_webgpu/README.md** — Deno FFI bindings
- **examples/features/src/\*/README.md** — Per-example documentation for the ~40 sample scenes

## Source Files
Full source code removed (2026-06-06). The 2,033 deleted files include `Cargo.toml` manifests, `Cargo.lock`, `build.rs` scripts, shader sources (`.wgsl`, `.glsl`, `.spv`), HTML shader playgrounds, image assets, and the full `wgpu/`, `wgpu-core/`, `wgpu-hal/`, `naga/`, `wgpu-info/`, `wgpu-types/`, `wgpu-macros/`, `naga-cli/`, `cts_runner/`, `lock-analyzer/`, `player/`, `xtask/`, `benches/`, `tests/`, `examples/` source trees. Available at <https://github.com/gfx-rs/wgpu>.

## What Was Removed
- Rust source: `*.rs`, `Cargo.toml`, `Cargo.lock`, `build.rs`
- Shaders: `*.wgsl`, `*.glsl`, `*.spv`, `*.spvasm`, `*.vert`, `*.frag`, `*.comp`
- Asset files: `*.png`, `*.jpg`, `*.svg`, `*.tga`, `*.gif`, `*.webp`
- CI / repo config: `.config/`, `*.yml` (workflow), `typos.toml`, `taplo.toml`, `rustfmt.toml`, `clippy.toml`, `renovate.json`, `codecov.yml`
- Examples directory source code (per-example READMEs preserved)
- Generated artifacts: `target/`, `Cargo.lock` lockfiles
- LICENSE files (Apache/MIT preserved in spirit via the wgpu project, but removed locally — see upstream for full text)
