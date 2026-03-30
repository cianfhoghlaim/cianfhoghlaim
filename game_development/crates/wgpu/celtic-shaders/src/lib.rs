//! Celtic Shaders - WebGPU Visual Effects
//!
//! WGSL shaders for Celtic-themed visual effects:
//! - Knotwork patterns (procedural)
//! - Spiral and La Tène decorations
//! - Particle effects (fire, magic, nature)
//! - Terrain rendering with Celtic landmarks
//!
//! Designed for integration with Babylon.js via WebGPU backend.

use bytemuck::{Pod, Zeroable};
use glam::{Vec2, Vec3, Vec4, Mat4};
use thiserror::Error;

// ============================================================================
// Shader Sources (WGSL)
// ============================================================================

/// Celtic knotwork pattern shader
pub const KNOTWORK_SHADER: &str = r#"
// Celtic Knotwork Pattern Shader
// Generates procedural interlacing patterns

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) world_pos: vec3<f32>,
};

struct Uniforms {
    view_proj: mat4x4<f32>,
    model: mat4x4<f32>,
    time: f32,
    complexity: f32,
    color_primary: vec4<f32>,
    color_secondary: vec4<f32>,
};

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

@vertex
fn vs_main(
    @location(0) position: vec3<f32>,
    @location(1) uv: vec2<f32>,
) -> VertexOutput {
    var output: VertexOutput;
    let world_pos = uniforms.model * vec4<f32>(position, 1.0);
    output.position = uniforms.view_proj * world_pos;
    output.uv = uv;
    output.world_pos = world_pos.xyz;
    return output;
}

// Signed distance function for rounded line segment
fn sd_segment(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>, r: f32) -> f32 {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

// Celtic knot cell pattern
fn knot_cell(uv: vec2<f32>, cell: vec2<f32>, time: f32) -> f32 {
    let local_uv = fract(uv * 4.0) - 0.5;

    // Generate crossing pattern based on cell position
    let cell_hash = fract(sin(dot(cell, vec2<f32>(12.9898, 78.233))) * 43758.5453);

    var d = 999.0;
    let r = 0.05;

    // Horizontal strand
    d = min(d, sd_segment(local_uv, vec2<f32>(-0.5, 0.0), vec2<f32>(0.5, 0.0), r));

    // Vertical strand (with over/under based on hash)
    let v_offset = select(-0.02, 0.02, cell_hash > 0.5);
    d = min(d, sd_segment(local_uv, vec2<f32>(0.0, -0.5), vec2<f32>(0.0, 0.5), r));

    return d;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
    let uv = input.uv;
    let time = uniforms.time;
    let complexity = uniforms.complexity;

    // Calculate knot pattern
    let cell = floor(uv * 4.0);
    let d = knot_cell(uv, cell, time);

    // Anti-aliased edge
    let aa = fwidth(d) * 1.5;
    let alpha = 1.0 - smoothstep(-aa, aa, d);

    // Animate color along strands
    let color_mix = sin(uv.x * 6.28 + time) * 0.5 + 0.5;
    let color = mix(uniforms.color_primary, uniforms.color_secondary, color_mix);

    return vec4<f32>(color.rgb, color.a * alpha);
}
"#;

/// Spiral pattern shader (triskele, etc.)
pub const SPIRAL_SHADER: &str = r#"
// Celtic Spiral Pattern Shader
// Generates triskele and multi-arm spirals

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

struct Uniforms {
    view_proj: mat4x4<f32>,
    model: mat4x4<f32>,
    time: f32,
    arms: f32,
    turns: f32,
    thickness: f32,
    color: vec4<f32>,
};

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

@vertex
fn vs_main(
    @location(0) position: vec3<f32>,
    @location(1) uv: vec2<f32>,
) -> VertexOutput {
    var output: VertexOutput;
    let world_pos = uniforms.model * vec4<f32>(position, 1.0);
    output.position = uniforms.view_proj * world_pos;
    output.uv = uv;
    return output;
}

// Signed distance to Archimedean spiral
fn sd_spiral(p: vec2<f32>, turns: f32, thickness: f32) -> f32 {
    let r = length(p);
    let theta = atan2(p.y, p.x);

    // Find nearest point on spiral
    let a = 1.0 / (6.28 * turns);
    let spiral_r = a * (theta + 6.28 * floor((r / a - theta) / 6.28 + 0.5));

    return abs(r - spiral_r) - thickness;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
    let uv = input.uv * 2.0 - 1.0;
    let time = uniforms.time;
    let arms = i32(uniforms.arms);

    var d = 999.0;

    // Generate multiple spiral arms
    for (var i = 0; i < arms; i++) {
        let angle = f32(i) * 6.28 / f32(arms) + time * 0.5;
        let rot = mat2x2<f32>(
            cos(angle), -sin(angle),
            sin(angle), cos(angle)
        );
        let rotated_uv = rot * uv;
        d = min(d, sd_spiral(rotated_uv, uniforms.turns, uniforms.thickness));
    }

    let aa = fwidth(d) * 1.5;
    let alpha = 1.0 - smoothstep(-aa, aa, d);

    // Gradient based on distance from center
    let r = length(uv);
    let glow = exp(-r * 2.0) * 0.5;

    var color = uniforms.color;
    color.rgb += glow;

    return vec4<f32>(color.rgb, color.a * alpha);
}
"#;

/// Fire/magic particle shader
pub const PARTICLE_SHADER: &str = r#"
// Celtic Magic Particle Shader
// GPU-accelerated particle rendering

struct Particle {
    position: vec3<f32>,
    velocity: vec3<f32>,
    color: vec4<f32>,
    size: f32,
    life: f32,
    max_life: f32,
    _padding: f32,
};

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) color: vec4<f32>,
    @location(2) life_ratio: f32,
};

struct Uniforms {
    view_proj: mat4x4<f32>,
    camera_right: vec3<f32>,
    _p0: f32,
    camera_up: vec3<f32>,
    time: f32,
};

@group(0) @binding(0) var<uniform> uniforms: Uniforms;
@group(0) @binding(1) var<storage, read> particles: array<Particle>;

@vertex
fn vs_main(
    @builtin(vertex_index) vertex_idx: u32,
    @builtin(instance_index) instance_idx: u32,
) -> VertexOutput {
    let particle = particles[instance_idx];

    // Billboard quad vertices
    let offsets = array<vec2<f32>, 6>(
        vec2<f32>(-1.0, -1.0),
        vec2<f32>(1.0, -1.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(-1.0, -1.0),
        vec2<f32>(1.0, 1.0),
        vec2<f32>(-1.0, 1.0),
    );

    let offset = offsets[vertex_idx];
    let size = particle.size * (particle.life / particle.max_life);

    // Billboard in camera space
    let world_pos = particle.position
        + uniforms.camera_right * offset.x * size
        + uniforms.camera_up * offset.y * size;

    var output: VertexOutput;
    output.position = uniforms.view_proj * vec4<f32>(world_pos, 1.0);
    output.uv = offset * 0.5 + 0.5;
    output.color = particle.color;
    output.life_ratio = particle.life / particle.max_life;

    return output;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
    let uv = input.uv * 2.0 - 1.0;
    let r = length(uv);

    // Soft circular particle
    let alpha = 1.0 - smoothstep(0.0, 1.0, r);

    // Fade out as particle dies
    let life_alpha = input.life_ratio * input.life_ratio;

    // Glow effect
    let glow = exp(-r * 3.0);

    var color = input.color;
    color.rgb += glow * 0.5;
    color.a *= alpha * life_alpha;

    return color;
}
"#;

/// Particle compute shader for GPU simulation
pub const PARTICLE_COMPUTE_SHADER: &str = r#"
// Celtic Particle Compute Shader
// GPU-based particle physics simulation

struct Particle {
    position: vec3<f32>,
    velocity: vec3<f32>,
    color: vec4<f32>,
    size: f32,
    life: f32,
    max_life: f32,
    _padding: f32,
};

struct SimParams {
    delta_time: f32,
    gravity: f32,
    damping: f32,
    wind_strength: f32,
    wind_direction: vec3<f32>,
    time: f32,
    emitter_position: vec3<f32>,
    emit_rate: f32,
};

@group(0) @binding(0) var<uniform> params: SimParams;
@group(0) @binding(1) var<storage, read_write> particles: array<Particle>;

// Simple hash for pseudo-random numbers
fn hash(n: f32) -> f32 {
    return fract(sin(n) * 43758.5453);
}

fn hash3(p: vec3<f32>) -> f32 {
    return fract(sin(dot(p, vec3<f32>(12.9898, 78.233, 45.164))) * 43758.5453);
}

@compute @workgroup_size(256)
fn cs_main(@builtin(global_invocation_id) id: vec3<u32>) {
    let idx = id.x;
    if (idx >= arrayLength(&particles)) {
        return;
    }

    var p = particles[idx];
    let dt = params.delta_time;

    // Update life
    p.life -= dt;

    if (p.life <= 0.0) {
        // Respawn particle
        let seed = f32(idx) + params.time * 0.1;
        let rand1 = hash(seed);
        let rand2 = hash(seed + 1.0);
        let rand3 = hash(seed + 2.0);

        // Random position around emitter
        let angle = rand1 * 6.28;
        let radius = rand2 * 0.5;
        p.position = params.emitter_position + vec3<f32>(
            cos(angle) * radius,
            0.0,
            sin(angle) * radius
        );

        // Upward velocity with spread
        p.velocity = vec3<f32>(
            (rand1 - 0.5) * 2.0,
            2.0 + rand2 * 2.0,
            (rand3 - 0.5) * 2.0
        );

        p.life = p.max_life;
        p.size = 0.1 + rand1 * 0.1;
    } else {
        // Physics simulation
        // Gravity
        p.velocity.y -= params.gravity * dt;

        // Wind
        p.velocity += params.wind_direction * params.wind_strength * dt;

        // Damping
        p.velocity *= 1.0 - params.damping * dt;

        // Turbulence (Celtic swirling motion)
        let turb_strength = 0.5;
        let turb_freq = 2.0;
        let turb = vec3<f32>(
            sin(p.position.y * turb_freq + params.time),
            0.0,
            cos(p.position.y * turb_freq + params.time)
        ) * turb_strength;
        p.velocity += turb * dt;

        // Update position
        p.position += p.velocity * dt;

        // Color fade (orange to red for fire)
        let life_ratio = p.life / p.max_life;
        p.color = vec4<f32>(
            1.0,
            0.3 + life_ratio * 0.5,
            life_ratio * 0.3,
            life_ratio
        );
    }

    particles[idx] = p;
}
"#;

/// Terrain shader with Celtic landmarks
pub const TERRAIN_SHADER: &str = r#"
// Celtic Terrain Shader
// Procedural terrain with standing stones and dolmens

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) world_pos: vec3<f32>,
    @location(2) normal: vec3<f32>,
};

struct Uniforms {
    view_proj: mat4x4<f32>,
    model: mat4x4<f32>,
    camera_pos: vec3<f32>,
    time: f32,
    fog_color: vec4<f32>,
    fog_density: f32,
    sun_direction: vec3<f32>,
    _padding: f32,
};

@group(0) @binding(0) var<uniform> uniforms: Uniforms;
@group(0) @binding(1) var terrain_texture: texture_2d<f32>;
@group(0) @binding(2) var terrain_sampler: sampler;

@vertex
fn vs_main(
    @location(0) position: vec3<f32>,
    @location(1) normal: vec3<f32>,
    @location(2) uv: vec2<f32>,
) -> VertexOutput {
    var output: VertexOutput;
    let world_pos = uniforms.model * vec4<f32>(position, 1.0);
    output.position = uniforms.view_proj * world_pos;
    output.uv = uv;
    output.world_pos = world_pos.xyz;
    output.normal = normalize((uniforms.model * vec4<f32>(normal, 0.0)).xyz);
    return output;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
    // Base terrain color
    let base_color = textureSample(terrain_texture, terrain_sampler, input.uv);

    // Lighting
    let n = normalize(input.normal);
    let l = normalize(uniforms.sun_direction);
    let ndotl = max(dot(n, l), 0.0);
    let ambient = 0.3;
    let diffuse = ndotl * 0.7;

    var color = base_color.rgb * (ambient + diffuse);

    // Fog
    let dist = length(input.world_pos - uniforms.camera_pos);
    let fog_factor = 1.0 - exp(-dist * uniforms.fog_density);
    color = mix(color, uniforms.fog_color.rgb, fog_factor);

    return vec4<f32>(color, 1.0);
}
"#;

// ============================================================================
// Uniform Structures
// ============================================================================

/// Common render uniforms
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct RenderUniforms {
    pub view_proj: [[f32; 4]; 4],
    pub model: [[f32; 4]; 4],
    pub camera_pos: [f32; 3],
    pub time: f32,
}

impl Default for RenderUniforms {
    fn default() -> Self {
        Self {
            view_proj: Mat4::IDENTITY.to_cols_array_2d(),
            model: Mat4::IDENTITY.to_cols_array_2d(),
            camera_pos: [0.0, 0.0, 0.0],
            time: 0.0,
        }
    }
}

/// Knotwork shader uniforms
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct KnotworkUniforms {
    pub view_proj: [[f32; 4]; 4],
    pub model: [[f32; 4]; 4],
    pub time: f32,
    pub complexity: f32,
    pub _padding: [f32; 2],
    pub color_primary: [f32; 4],
    pub color_secondary: [f32; 4],
}

impl Default for KnotworkUniforms {
    fn default() -> Self {
        Self {
            view_proj: Mat4::IDENTITY.to_cols_array_2d(),
            model: Mat4::IDENTITY.to_cols_array_2d(),
            time: 0.0,
            complexity: 4.0,
            _padding: [0.0; 2],
            color_primary: [0.8, 0.6, 0.2, 1.0], // Gold
            color_secondary: [0.2, 0.5, 0.3, 1.0], // Forest green
        }
    }
}

/// Particle system uniforms
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct ParticleUniforms {
    pub view_proj: [[f32; 4]; 4],
    pub camera_right: [f32; 3],
    pub _p0: f32,
    pub camera_up: [f32; 3],
    pub time: f32,
}

/// Particle simulation parameters
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct ParticleSimParams {
    pub delta_time: f32,
    pub gravity: f32,
    pub damping: f32,
    pub wind_strength: f32,
    pub wind_direction: [f32; 3],
    pub time: f32,
    pub emitter_position: [f32; 3],
    pub emit_rate: f32,
}

impl Default for ParticleSimParams {
    fn default() -> Self {
        Self {
            delta_time: 1.0 / 60.0,
            gravity: 9.8,
            damping: 0.1,
            wind_strength: 0.0,
            wind_direction: [1.0, 0.0, 0.0],
            time: 0.0,
            emitter_position: [0.0, 0.0, 0.0],
            emit_rate: 100.0,
        }
    }
}

/// Single particle data
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct Particle {
    pub position: [f32; 3],
    pub velocity: [f32; 3],
    pub color: [f32; 4],
    pub size: f32,
    pub life: f32,
    pub max_life: f32,
    pub _padding: f32,
}

impl Default for Particle {
    fn default() -> Self {
        Self {
            position: [0.0; 3],
            velocity: [0.0, 1.0, 0.0],
            color: [1.0, 0.5, 0.0, 1.0],
            size: 0.1,
            life: 2.0,
            max_life: 2.0,
            _padding: 0.0,
        }
    }
}

// ============================================================================
// Shader Loading Utilities
// ============================================================================

#[derive(Error, Debug)]
pub enum ShaderError {
    #[error("Failed to create shader module: {0}")]
    CreationFailed(String),

    #[error("Shader compilation error")]
    CompilationError,
}

/// Get shader source by name
pub fn get_shader_source(name: &str) -> Option<&'static str> {
    match name {
        "knotwork" => Some(KNOTWORK_SHADER),
        "spiral" => Some(SPIRAL_SHADER),
        "particle" | "particle_render" => Some(PARTICLE_SHADER),
        "particle_compute" => Some(PARTICLE_COMPUTE_SHADER),
        "terrain" => Some(TERRAIN_SHADER),
        _ => None,
    }
}

/// List all available shaders
pub fn list_shaders() -> &'static [&'static str] {
    &["knotwork", "spiral", "particle", "particle_compute", "terrain"]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_shader_sources_valid() {
        for name in list_shaders() {
            assert!(get_shader_source(name).is_some());
        }
    }

    #[test]
    fn test_uniforms_size() {
        assert_eq!(std::mem::size_of::<RenderUniforms>(), 144);
        assert_eq!(std::mem::size_of::<Particle>() % 16, 0);
    }

    #[test]
    fn test_knotwork_uniforms_default() {
        let uniforms = KnotworkUniforms::default();
        assert_eq!(uniforms.complexity, 4.0);
    }
}
