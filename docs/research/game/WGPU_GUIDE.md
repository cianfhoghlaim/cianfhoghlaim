# WGPU Guide

Guide to graphics programming with wgpu for the Tuath Celtic MMO.

## Overview

wgpu is a cross-platform graphics API that provides:
- WebGPU implementation for Rust
- Cross-platform support (Windows, macOS, Linux, Web, iOS, Android)
- Modern GPU programming paradigm
- Safe Rust bindings

### Reference Materials

| Resource | Path |
|----------|------|
| wgpu Library | `taighde/game/wgpu/` |
| Shader Examples | `crates/wgpu/celtic-shaders/` |
| Particle System | `crates/wgpu/particle-system/` |

---

## Project Setup

### Cargo.toml

```toml
[package]
name = "tuath-renderer"
version = "0.1.0"
edition = "2021"

[dependencies]
wgpu = "0.19"
winit = "0.29"
bytemuck = { version = "1.14", features = ["derive"] }
cgmath = "0.18"
pollster = "0.3"
log = "0.4"
env_logger = "0.11"

# For texture loading
image = "0.24"

# For async
tokio = { version = "1", features = ["rt", "macros"] }
```

---

## Core Concepts

### Initialization

```rust
// src/renderer.rs

use wgpu::{
    Adapter, Device, Queue, Surface, SurfaceConfiguration,
    Instance, InstanceDescriptor, PowerPreference, RequestAdapterOptions,
};
use winit::window::Window;

pub struct Renderer {
    surface: Surface,
    device: Device,
    queue: Queue,
    config: SurfaceConfiguration,
    size: winit::dpi::PhysicalSize<u32>,
}

impl Renderer {
    pub async fn new(window: &Window) -> Self {
        let size = window.inner_size();

        // Create instance
        let instance = Instance::new(InstanceDescriptor {
            backends: wgpu::Backends::all(),
            dx12_shader_compiler: Default::default(),
            flags: wgpu::InstanceFlags::default(),
            gles_minor_version: wgpu::Gles3MinorVersion::default(),
        });

        // Create surface
        let surface = unsafe { instance.create_surface(window) }.unwrap();

        // Request adapter
        let adapter = instance
            .request_adapter(&RequestAdapterOptions {
                power_preference: PowerPreference::HighPerformance,
                compatible_surface: Some(&surface),
                force_fallback_adapter: false,
            })
            .await
            .expect("Failed to find adapter");

        // Request device and queue
        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    label: Some("Tuath Device"),
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                },
                None,
            )
            .await
            .expect("Failed to create device");

        // Configure surface
        let surface_caps = surface.get_capabilities(&adapter);
        let surface_format = surface_caps
            .formats
            .iter()
            .copied()
            .find(|f| f.is_srgb())
            .unwrap_or(surface_caps.formats[0]);

        let config = SurfaceConfiguration {
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
            format: surface_format,
            width: size.width,
            height: size.height,
            present_mode: wgpu::PresentMode::Fifo,
            alpha_mode: surface_caps.alpha_modes[0],
            view_formats: vec![],
            desired_maximum_frame_latency: 2,
        };

        surface.configure(&device, &config);

        Self {
            surface,
            device,
            queue,
            config,
            size,
        }
    }

    pub fn resize(&mut self, new_size: winit::dpi::PhysicalSize<u32>) {
        if new_size.width > 0 && new_size.height > 0 {
            self.size = new_size;
            self.config.width = new_size.width;
            self.config.height = new_size.height;
            self.surface.configure(&self.device, &self.config);
        }
    }
}
```

### Shaders

```wgsl
// shaders/terrain.wgsl

struct VertexInput {
    @location(0) position: vec3<f32>,
    @location(1) normal: vec3<f32>,
    @location(2) tex_coords: vec2<f32>,
}

struct VertexOutput {
    @builtin(position) clip_position: vec4<f32>,
    @location(0) world_position: vec3<f32>,
    @location(1) world_normal: vec3<f32>,
    @location(2) tex_coords: vec2<f32>,
}

struct Camera {
    view_proj: mat4x4<f32>,
    position: vec3<f32>,
}

struct Light {
    direction: vec3<f32>,
    color: vec3<f32>,
    ambient: vec3<f32>,
}

@group(0) @binding(0)
var<uniform> camera: Camera;

@group(0) @binding(1)
var<uniform> light: Light;

@group(1) @binding(0)
var terrain_texture: texture_2d<f32>;

@group(1) @binding(1)
var terrain_sampler: sampler;

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var out: VertexOutput;

    out.clip_position = camera.view_proj * vec4<f32>(in.position, 1.0);
    out.world_position = in.position;
    out.world_normal = in.normal;
    out.tex_coords = in.tex_coords;

    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let normal = normalize(in.world_normal);

    // Diffuse lighting
    let light_dir = normalize(-light.direction);
    let diffuse = max(dot(normal, light_dir), 0.0);

    // Sample texture
    let tex_color = textureSample(terrain_texture, terrain_sampler, in.tex_coords);

    // Combine lighting
    let ambient = light.ambient * tex_color.rgb;
    let lit_color = ambient + diffuse * light.color * tex_color.rgb;

    return vec4<f32>(lit_color, tex_color.a);
}
```

### Render Pipeline

```rust
// src/pipeline.rs

use wgpu::{Device, RenderPipeline, ShaderModule, TextureFormat};

pub fn create_terrain_pipeline(
    device: &Device,
    format: TextureFormat,
) -> RenderPipeline {
    // Load shader
    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("Terrain Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("../shaders/terrain.wgsl").into()),
    });

    // Vertex buffer layout
    let vertex_layout = wgpu::VertexBufferLayout {
        array_stride: std::mem::size_of::<Vertex>() as wgpu::BufferAddress,
        step_mode: wgpu::VertexStepMode::Vertex,
        attributes: &[
            // Position
            wgpu::VertexAttribute {
                offset: 0,
                shader_location: 0,
                format: wgpu::VertexFormat::Float32x3,
            },
            // Normal
            wgpu::VertexAttribute {
                offset: 12,
                shader_location: 1,
                format: wgpu::VertexFormat::Float32x3,
            },
            // Texture coordinates
            wgpu::VertexAttribute {
                offset: 24,
                shader_location: 2,
                format: wgpu::VertexFormat::Float32x2,
            },
        ],
    };

    // Bind group layouts
    let camera_bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        label: Some("Camera Bind Group Layout"),
        entries: &[
            // Camera uniform
            wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::VERTEX | wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Buffer {
                    ty: wgpu::BufferBindingType::Uniform,
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            },
            // Light uniform
            wgpu::BindGroupLayoutEntry {
                binding: 1,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Buffer {
                    ty: wgpu::BufferBindingType::Uniform,
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            },
        ],
    });

    let texture_bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        label: Some("Texture Bind Group Layout"),
        entries: &[
            wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Texture {
                    sample_type: wgpu::TextureSampleType::Float { filterable: true },
                    view_dimension: wgpu::TextureViewDimension::D2,
                    multisampled: false,
                },
                count: None,
            },
            wgpu::BindGroupLayoutEntry {
                binding: 1,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                count: None,
            },
        ],
    });

    let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: Some("Terrain Pipeline Layout"),
        bind_group_layouts: &[&camera_bind_group_layout, &texture_bind_group_layout],
        push_constant_ranges: &[],
    });

    device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Terrain Pipeline"),
        layout: Some(&pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[vertex_layout],
        },
        fragment: Some(wgpu::FragmentState {
            module: &shader,
            entry_point: "fs_main",
            targets: &[Some(wgpu::ColorTargetState {
                format,
                blend: Some(wgpu::BlendState::REPLACE),
                write_mask: wgpu::ColorWrites::ALL,
            })],
        }),
        primitive: wgpu::PrimitiveState {
            topology: wgpu::PrimitiveTopology::TriangleList,
            strip_index_format: None,
            front_face: wgpu::FrontFace::Ccw,
            cull_mode: Some(wgpu::Face::Back),
            polygon_mode: wgpu::PolygonMode::Fill,
            unclipped_depth: false,
            conservative: false,
        },
        depth_stencil: Some(wgpu::DepthStencilState {
            format: wgpu::TextureFormat::Depth32Float,
            depth_write_enabled: true,
            depth_compare: wgpu::CompareFunction::Less,
            stencil: wgpu::StencilState::default(),
            bias: wgpu::DepthBiasState::default(),
        }),
        multisample: wgpu::MultisampleState {
            count: 1,
            mask: !0,
            alpha_to_coverage_enabled: false,
        },
        multiview: None,
    })
}
```

---

## Celtic Shaders

### Fog Effect

```wgsl
// shaders/celtic_fog.wgsl

struct FogParams {
    color: vec3<f32>,
    density: f32,
    start: f32,
    end: f32,
}

@group(2) @binding(0)
var<uniform> fog: FogParams;

fn apply_fog(color: vec3<f32>, world_pos: vec3<f32>, camera_pos: vec3<f32>) -> vec3<f32> {
    let distance = length(world_pos - camera_pos);

    // Exponential fog
    let fog_factor = 1.0 - exp(-fog.density * distance);

    // Clamp to range
    let clamped_factor = clamp((distance - fog.start) / (fog.end - fog.start), 0.0, 1.0);

    return mix(color, fog.color, fog_factor * clamped_factor);
}
```

### Water Shader

```wgsl
// shaders/celtic_water.wgsl

struct WaterParams {
    time: f32,
    wave_speed: f32,
    wave_height: f32,
    wave_frequency: f32,
    color_shallow: vec3<f32>,
    color_deep: vec3<f32>,
    foam_threshold: f32,
}

@group(2) @binding(0)
var<uniform> water: WaterParams;

fn wave_height(position: vec2<f32>) -> f32 {
    let t = water.time * water.wave_speed;

    // Combine multiple wave frequencies
    let wave1 = sin(position.x * water.wave_frequency + t) * 0.5;
    let wave2 = sin(position.y * water.wave_frequency * 0.7 + t * 1.3) * 0.3;
    let wave3 = sin((position.x + position.y) * water.wave_frequency * 0.5 + t * 0.8) * 0.2;

    return (wave1 + wave2 + wave3) * water.wave_height;
}

fn water_normal(position: vec2<f32>) -> vec3<f32> {
    let epsilon = 0.1;

    let h_center = wave_height(position);
    let h_right = wave_height(position + vec2<f32>(epsilon, 0.0));
    let h_up = wave_height(position + vec2<f32>(0.0, epsilon));

    let dx = (h_right - h_center) / epsilon;
    let dy = (h_up - h_center) / epsilon;

    return normalize(vec3<f32>(-dx, 1.0, -dy));
}

@fragment
fn fs_water(in: VertexOutput) -> @location(0) vec4<f32> {
    let normal = water_normal(in.world_position.xz);

    // Fresnel effect
    let view_dir = normalize(camera.position - in.world_position);
    let fresnel = pow(1.0 - max(dot(view_dir, normal), 0.0), 3.0);

    // Depth-based color
    let depth = in.world_position.y;
    let color = mix(water.color_deep, water.color_shallow, clamp(depth * 0.1, 0.0, 1.0));

    // Reflection
    let reflect_dir = reflect(-view_dir, normal);
    let sky_color = vec3<f32>(0.6, 0.7, 0.9);

    let final_color = mix(color, sky_color, fresnel * 0.5);

    return vec4<f32>(final_color, 0.8);
}
```

### Particle System

```rust
// src/particles.rs

use wgpu::{Buffer, Device, Queue};
use bytemuck::{Pod, Zeroable};

#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct Particle {
    pub position: [f32; 3],
    pub velocity: [f32; 3],
    pub color: [f32; 4],
    pub size: f32,
    pub life: f32,
    pub max_life: f32,
    _padding: f32,
}

pub struct ParticleSystem {
    particles: Vec<Particle>,
    vertex_buffer: Buffer,
    max_particles: usize,
    spawn_rate: f32,
    spawn_timer: f32,
}

impl ParticleSystem {
    pub fn new(device: &Device, max_particles: usize) -> Self {
        let particles = Vec::with_capacity(max_particles);

        let vertex_buffer = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Particle Buffer"),
            size: (max_particles * std::mem::size_of::<Particle>()) as u64,
            usage: wgpu::BufferUsages::VERTEX | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        Self {
            particles,
            vertex_buffer,
            max_particles,
            spawn_rate: 100.0,  // particles per second
            spawn_timer: 0.0,
        }
    }

    pub fn update(&mut self, delta_time: f32, queue: &Queue) {
        // Update existing particles
        self.particles.retain_mut(|p| {
            p.life -= delta_time;

            if p.life > 0.0 {
                // Apply physics
                p.position[0] += p.velocity[0] * delta_time;
                p.position[1] += p.velocity[1] * delta_time;
                p.position[2] += p.velocity[2] * delta_time;

                // Gravity
                p.velocity[1] -= 9.8 * delta_time;

                // Fade out
                p.color[3] = p.life / p.max_life;

                true
            } else {
                false
            }
        });

        // Spawn new particles
        self.spawn_timer += delta_time;
        let spawn_interval = 1.0 / self.spawn_rate;

        while self.spawn_timer >= spawn_interval && self.particles.len() < self.max_particles {
            self.spawn_timer -= spawn_interval;
            self.spawn_particle();
        }

        // Update GPU buffer
        queue.write_buffer(
            &self.vertex_buffer,
            0,
            bytemuck::cast_slice(&self.particles),
        );
    }

    fn spawn_particle(&mut self) {
        let life = 2.0 + rand::random::<f32>() * 2.0;

        self.particles.push(Particle {
            position: [0.0, 0.0, 0.0],
            velocity: [
                (rand::random::<f32>() - 0.5) * 5.0,
                rand::random::<f32>() * 10.0,
                (rand::random::<f32>() - 0.5) * 5.0,
            ],
            color: [1.0, 0.8, 0.2, 1.0],  // Orange/gold
            size: 0.1 + rand::random::<f32>() * 0.1,
            life,
            max_life: life,
            _padding: 0.0,
        });
    }

    pub fn particle_count(&self) -> usize {
        self.particles.len()
    }
}
```

---

## Render Loop

```rust
// src/main.rs

use winit::{
    event::*,
    event_loop::{ControlFlow, EventLoop},
    window::WindowBuilder,
};

fn main() {
    env_logger::init();

    let event_loop = EventLoop::new().unwrap();
    let window = WindowBuilder::new()
        .with_title("Tuath Celtic MMO")
        .with_inner_size(winit::dpi::PhysicalSize::new(1280, 720))
        .build(&event_loop)
        .unwrap();

    let mut renderer = pollster::block_on(Renderer::new(&window));

    event_loop.run(move |event, _, control_flow| {
        match event {
            Event::WindowEvent { event, window_id }
                if window_id == window.id() =>
            {
                match event {
                    WindowEvent::CloseRequested => {
                        *control_flow = ControlFlow::Exit;
                    }
                    WindowEvent::Resized(physical_size) => {
                        renderer.resize(physical_size);
                    }
                    WindowEvent::RedrawRequested => {
                        match renderer.render() {
                            Ok(_) => {}
                            Err(wgpu::SurfaceError::Lost) => {
                                renderer.resize(renderer.size);
                            }
                            Err(wgpu::SurfaceError::OutOfMemory) => {
                                *control_flow = ControlFlow::Exit;
                            }
                            Err(e) => eprintln!("Render error: {:?}", e),
                        }
                    }
                    _ => {}
                }
            }
            Event::MainEventsCleared => {
                window.request_redraw();
            }
            _ => {}
        }
    }).unwrap();
}

impl Renderer {
    pub fn render(&mut self) -> Result<(), wgpu::SurfaceError> {
        let output = self.surface.get_current_texture()?;
        let view = output.texture.create_view(&wgpu::TextureViewDescriptor::default());

        let mut encoder = self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("Render Encoder"),
        });

        {
            let mut render_pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("Render Pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color {
                            r: 0.1,
                            g: 0.2,
                            b: 0.3,
                            a: 1.0,
                        }),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: Some(wgpu::RenderPassDepthStencilAttachment {
                    view: &self.depth_texture_view,
                    depth_ops: Some(wgpu::Operations {
                        load: wgpu::LoadOp::Clear(1.0),
                        store: wgpu::StoreOp::Store,
                    }),
                    stencil_ops: None,
                }),
                timestamp_writes: None,
                occlusion_query_set: None,
            });

            // Render terrain
            render_pass.set_pipeline(&self.terrain_pipeline);
            render_pass.set_bind_group(0, &self.camera_bind_group, &[]);
            render_pass.set_bind_group(1, &self.terrain_texture_bind_group, &[]);
            render_pass.set_vertex_buffer(0, self.terrain_vertex_buffer.slice(..));
            render_pass.set_index_buffer(self.terrain_index_buffer.slice(..), wgpu::IndexFormat::Uint32);
            render_pass.draw_indexed(0..self.terrain_index_count, 0, 0..1);

            // Render water
            // Render particles
            // etc.
        }

        self.queue.submit(std::iter::once(encoder.finish()));
        output.present();

        Ok(())
    }
}
```

---

## Related Documentation

- [Godot + Rust Guide](./GODOT_RUST_GUIDE.md) - Game engine integration
- [SpacetimeDB Guide](./SPACETIMEDB_GUIDE.md) - Multiplayer
- [Particle System](../../crates/wgpu/particle-system/) - Particle effects
