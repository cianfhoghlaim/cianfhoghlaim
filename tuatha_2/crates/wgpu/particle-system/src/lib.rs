//! Celtic Particle System
//!
//! GPU-accelerated particle effects:
//! - Fire and smoke
//! - Magic and spells
//! - Nature (leaves, fog, rain)
//! - Celebration effects
//!
//! Uses compute shaders for physics simulation.

use bytemuck::{Pod, Zeroable};
use celtic_shaders::{Particle, ParticleSimParams, ParticleUniforms, PARTICLE_COMPUTE_SHADER, PARTICLE_SHADER};
use glam::{Vec3, Vec4, Mat4};
use rand::Rng;
use thiserror::Error;
use wgpu::util::DeviceExt;

// ============================================================================
// Errors
// ============================================================================

#[derive(Error, Debug)]
pub enum ParticleError {
    #[error("Failed to create particle system: {0}")]
    CreationFailed(String),

    #[error("GPU buffer creation failed")]
    BufferCreationFailed,

    #[error("Shader compilation failed")]
    ShaderCompilationFailed,
}

// ============================================================================
// Particle System Configuration
// ============================================================================

/// Particle effect presets
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ParticlePreset {
    /// Orange/red fire particles
    Fire,
    /// Blue/white magic sparkles
    Magic,
    /// Gray smoke particles
    Smoke,
    /// Green nature particles (leaves, pollen)
    Nature,
    /// Gold celebration particles
    Celebration,
    /// Custom configuration
    Custom,
}

/// Particle emitter configuration
#[derive(Debug, Clone)]
pub struct EmitterConfig {
    /// Emitter position in world space
    pub position: Vec3,
    /// Emission rate (particles per second)
    pub emit_rate: f32,
    /// Maximum number of particles
    pub max_particles: u32,
    /// Particle lifetime range (min, max)
    pub lifetime: (f32, f32),
    /// Initial velocity range
    pub initial_velocity: (Vec3, Vec3),
    /// Particle size range
    pub size: (f32, f32),
    /// Gravity strength
    pub gravity: f32,
    /// Air damping
    pub damping: f32,
    /// Wind vector
    pub wind: Vec3,
    /// Color gradient (start, end)
    pub color_start: Vec4,
    pub color_end: Vec4,
    /// Effect preset
    pub preset: ParticlePreset,
}

impl Default for EmitterConfig {
    fn default() -> Self {
        Self {
            position: Vec3::ZERO,
            emit_rate: 100.0,
            max_particles: 10000,
            lifetime: (1.0, 3.0),
            initial_velocity: (Vec3::new(-1.0, 1.0, -1.0), Vec3::new(1.0, 3.0, 1.0)),
            size: (0.05, 0.15),
            gravity: 9.8,
            damping: 0.1,
            wind: Vec3::ZERO,
            color_start: Vec4::new(1.0, 0.8, 0.2, 1.0),
            color_end: Vec4::new(1.0, 0.2, 0.0, 0.0),
            preset: ParticlePreset::Fire,
        }
    }
}

impl EmitterConfig {
    /// Create fire effect configuration
    pub fn fire(position: Vec3) -> Self {
        Self {
            position,
            emit_rate: 200.0,
            max_particles: 5000,
            lifetime: (0.5, 2.0),
            initial_velocity: (Vec3::new(-0.5, 2.0, -0.5), Vec3::new(0.5, 4.0, 0.5)),
            size: (0.1, 0.3),
            gravity: -1.0, // Floats up
            damping: 0.2,
            wind: Vec3::ZERO,
            color_start: Vec4::new(1.0, 0.9, 0.3, 1.0),
            color_end: Vec4::new(1.0, 0.1, 0.0, 0.0),
            preset: ParticlePreset::Fire,
        }
    }

    /// Create magic effect configuration
    pub fn magic(position: Vec3) -> Self {
        Self {
            position,
            emit_rate: 50.0,
            max_particles: 2000,
            lifetime: (1.0, 3.0),
            initial_velocity: (Vec3::new(-2.0, 0.0, -2.0), Vec3::new(2.0, 2.0, 2.0)),
            size: (0.02, 0.08),
            gravity: 0.0,
            damping: 0.05,
            wind: Vec3::ZERO,
            color_start: Vec4::new(0.3, 0.5, 1.0, 1.0),
            color_end: Vec4::new(1.0, 1.0, 1.0, 0.0),
            preset: ParticlePreset::Magic,
        }
    }

    /// Create smoke effect configuration
    pub fn smoke(position: Vec3) -> Self {
        Self {
            position,
            emit_rate: 30.0,
            max_particles: 1000,
            lifetime: (3.0, 6.0),
            initial_velocity: (Vec3::new(-0.3, 0.5, -0.3), Vec3::new(0.3, 1.5, 0.3)),
            size: (0.2, 0.5),
            gravity: -0.5,
            damping: 0.3,
            wind: Vec3::new(1.0, 0.0, 0.0),
            color_start: Vec4::new(0.3, 0.3, 0.3, 0.8),
            color_end: Vec4::new(0.5, 0.5, 0.5, 0.0),
            preset: ParticlePreset::Smoke,
        }
    }

    /// Create nature effect (leaves/pollen)
    pub fn nature(position: Vec3) -> Self {
        Self {
            position,
            emit_rate: 20.0,
            max_particles: 500,
            lifetime: (4.0, 8.0),
            initial_velocity: (Vec3::new(-1.0, -0.5, -1.0), Vec3::new(1.0, 0.5, 1.0)),
            size: (0.05, 0.15),
            gravity: 2.0,
            damping: 0.5,
            wind: Vec3::new(2.0, 0.0, 0.5),
            color_start: Vec4::new(0.3, 0.7, 0.2, 1.0),
            color_end: Vec4::new(0.6, 0.5, 0.1, 0.5),
            preset: ParticlePreset::Nature,
        }
    }

    /// Create celebration effect (gold sparkles)
    pub fn celebration(position: Vec3) -> Self {
        Self {
            position,
            emit_rate: 100.0,
            max_particles: 3000,
            lifetime: (2.0, 4.0),
            initial_velocity: (Vec3::new(-3.0, 5.0, -3.0), Vec3::new(3.0, 10.0, 3.0)),
            size: (0.03, 0.1),
            gravity: 3.0,
            damping: 0.1,
            wind: Vec3::ZERO,
            color_start: Vec4::new(1.0, 0.85, 0.0, 1.0),
            color_end: Vec4::new(1.0, 0.7, 0.3, 0.0),
            preset: ParticlePreset::Celebration,
        }
    }
}

// ============================================================================
// Particle System
// ============================================================================

/// GPU particle system
pub struct ParticleSystem {
    config: EmitterConfig,
    particles: Vec<Particle>,
    time: f32,

    // GPU resources (optional, created when device available)
    particle_buffer: Option<wgpu::Buffer>,
    uniform_buffer: Option<wgpu::Buffer>,
    sim_params_buffer: Option<wgpu::Buffer>,
    compute_pipeline: Option<wgpu::ComputePipeline>,
    render_pipeline: Option<wgpu::RenderPipeline>,
    bind_group: Option<wgpu::BindGroup>,
}

impl ParticleSystem {
    /// Create a new particle system
    pub fn new(config: EmitterConfig) -> Self {
        let max_particles = config.max_particles as usize;
        let mut rng = rand::thread_rng();

        // Initialize particles
        let particles: Vec<Particle> = (0..max_particles)
            .map(|_| {
                let lifetime = rng.gen_range(config.lifetime.0..config.lifetime.1);
                Particle {
                    position: config.position.to_array(),
                    velocity: [
                        rng.gen_range(config.initial_velocity.0.x..config.initial_velocity.1.x),
                        rng.gen_range(config.initial_velocity.0.y..config.initial_velocity.1.y),
                        rng.gen_range(config.initial_velocity.0.z..config.initial_velocity.1.z),
                    ],
                    color: config.color_start.to_array(),
                    size: rng.gen_range(config.size.0..config.size.1),
                    life: rng.gen_range(0.0..lifetime),
                    max_life: lifetime,
                    _padding: 0.0,
                }
            })
            .collect();

        Self {
            config,
            particles,
            time: 0.0,
            particle_buffer: None,
            uniform_buffer: None,
            sim_params_buffer: None,
            compute_pipeline: None,
            render_pipeline: None,
            bind_group: None,
        }
    }

    /// Create with preset
    pub fn with_preset(preset: ParticlePreset, position: Vec3) -> Self {
        let config = match preset {
            ParticlePreset::Fire => EmitterConfig::fire(position),
            ParticlePreset::Magic => EmitterConfig::magic(position),
            ParticlePreset::Smoke => EmitterConfig::smoke(position),
            ParticlePreset::Nature => EmitterConfig::nature(position),
            ParticlePreset::Celebration => EmitterConfig::celebration(position),
            ParticlePreset::Custom => EmitterConfig::default(),
        };
        Self::new(config)
    }

    /// Initialize GPU resources
    pub fn init_gpu(&mut self, device: &wgpu::Device) -> Result<(), ParticleError> {
        // Create particle buffer
        self.particle_buffer = Some(device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Particle Buffer"),
            contents: bytemuck::cast_slice(&self.particles),
            usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::VERTEX | wgpu::BufferUsages::COPY_DST,
        }));

        // Create uniform buffer
        let uniforms = ParticleUniforms {
            view_proj: Mat4::IDENTITY.to_cols_array_2d(),
            camera_right: [1.0, 0.0, 0.0],
            _p0: 0.0,
            camera_up: [0.0, 1.0, 0.0],
            time: 0.0,
        };
        self.uniform_buffer = Some(device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Particle Uniforms"),
            contents: bytemuck::bytes_of(&uniforms),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        }));

        // Create simulation params buffer
        let sim_params = ParticleSimParams {
            delta_time: 1.0 / 60.0,
            gravity: self.config.gravity,
            damping: self.config.damping,
            wind_strength: self.config.wind.length(),
            wind_direction: self.config.wind.normalize_or_zero().to_array(),
            time: 0.0,
            emitter_position: self.config.position.to_array(),
            emit_rate: self.config.emit_rate,
        };
        self.sim_params_buffer = Some(device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Sim Params"),
            contents: bytemuck::bytes_of(&sim_params),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        }));

        Ok(())
    }

    /// Update simulation (CPU fallback)
    pub fn update_cpu(&mut self, delta_time: f32) {
        self.time += delta_time;
        let mut rng = rand::thread_rng();

        for particle in &mut self.particles {
            particle.life -= delta_time;

            if particle.life <= 0.0 {
                // Respawn
                let lifetime = rng.gen_range(self.config.lifetime.0..self.config.lifetime.1);
                particle.position = self.config.position.to_array();
                particle.velocity = [
                    rng.gen_range(self.config.initial_velocity.0.x..self.config.initial_velocity.1.x),
                    rng.gen_range(self.config.initial_velocity.0.y..self.config.initial_velocity.1.y),
                    rng.gen_range(self.config.initial_velocity.0.z..self.config.initial_velocity.1.z),
                ];
                particle.life = lifetime;
                particle.max_life = lifetime;
                particle.size = rng.gen_range(self.config.size.0..self.config.size.1);
            } else {
                // Physics
                particle.velocity[1] -= self.config.gravity * delta_time;

                // Damping
                for v in &mut particle.velocity {
                    *v *= 1.0 - self.config.damping * delta_time;
                }

                // Wind
                particle.velocity[0] += self.config.wind.x * delta_time;
                particle.velocity[1] += self.config.wind.y * delta_time;
                particle.velocity[2] += self.config.wind.z * delta_time;

                // Position
                particle.position[0] += particle.velocity[0] * delta_time;
                particle.position[1] += particle.velocity[1] * delta_time;
                particle.position[2] += particle.velocity[2] * delta_time;

                // Color interpolation
                let t = 1.0 - particle.life / particle.max_life;
                particle.color = [
                    self.config.color_start.x + (self.config.color_end.x - self.config.color_start.x) * t,
                    self.config.color_start.y + (self.config.color_end.y - self.config.color_start.y) * t,
                    self.config.color_start.z + (self.config.color_end.z - self.config.color_start.z) * t,
                    self.config.color_start.w + (self.config.color_end.w - self.config.color_start.w) * t,
                ];
            }
        }
    }

    /// Get particle count
    pub fn particle_count(&self) -> usize {
        self.particles.len()
    }

    /// Get active particle count
    pub fn active_count(&self) -> usize {
        self.particles.iter().filter(|p| p.life > 0.0).count()
    }

    /// Get particle data for rendering
    pub fn get_particles(&self) -> &[Particle] {
        &self.particles
    }

    /// Set emitter position
    pub fn set_position(&mut self, position: Vec3) {
        self.config.position = position;
    }

    /// Set emission rate
    pub fn set_emit_rate(&mut self, rate: f32) {
        self.config.emit_rate = rate;
    }

    /// Set wind
    pub fn set_wind(&mut self, wind: Vec3) {
        self.config.wind = wind;
    }

    /// Get current time
    pub fn time(&self) -> f32 {
        self.time
    }
}

// ============================================================================
// Particle Effect Manager
// ============================================================================

/// Manages multiple particle effects
pub struct ParticleEffectManager {
    effects: Vec<ParticleSystem>,
    max_effects: usize,
}

impl ParticleEffectManager {
    /// Create a new manager
    pub fn new(max_effects: usize) -> Self {
        Self {
            effects: Vec::with_capacity(max_effects),
            max_effects,
        }
    }

    /// Add a particle effect
    pub fn add_effect(&mut self, effect: ParticleSystem) -> Option<usize> {
        if self.effects.len() >= self.max_effects {
            return None;
        }
        let idx = self.effects.len();
        self.effects.push(effect);
        Some(idx)
    }

    /// Spawn effect at position with preset
    pub fn spawn(&mut self, preset: ParticlePreset, position: Vec3) -> Option<usize> {
        self.add_effect(ParticleSystem::with_preset(preset, position))
    }

    /// Update all effects
    pub fn update(&mut self, delta_time: f32) {
        for effect in &mut self.effects {
            effect.update_cpu(delta_time);
        }
    }

    /// Remove effect by index
    pub fn remove(&mut self, index: usize) {
        if index < self.effects.len() {
            self.effects.swap_remove(index);
        }
    }

    /// Get effect count
    pub fn count(&self) -> usize {
        self.effects.len()
    }

    /// Get total particle count
    pub fn total_particles(&self) -> usize {
        self.effects.iter().map(|e| e.particle_count()).sum()
    }

    /// Get all effects
    pub fn effects(&self) -> &[ParticleSystem] {
        &self.effects
    }

    /// Get mutable effects
    pub fn effects_mut(&mut self) -> &mut [ParticleSystem] {
        &mut self.effects
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_particle_system_creation() {
        let system = ParticleSystem::with_preset(ParticlePreset::Fire, Vec3::ZERO);
        assert!(system.particle_count() > 0);
    }

    #[test]
    fn test_particle_update() {
        let mut system = ParticleSystem::new(EmitterConfig {
            max_particles: 100,
            ..Default::default()
        });

        system.update_cpu(1.0 / 60.0);
        assert!(system.time() > 0.0);
    }

    #[test]
    fn test_effect_manager() {
        let mut manager = ParticleEffectManager::new(10);

        manager.spawn(ParticlePreset::Fire, Vec3::ZERO);
        manager.spawn(ParticlePreset::Magic, Vec3::new(10.0, 0.0, 0.0));

        assert_eq!(manager.count(), 2);

        manager.update(1.0 / 60.0);
        assert!(manager.total_particles() > 0);
    }

    #[test]
    fn test_presets() {
        let presets = [
            ParticlePreset::Fire,
            ParticlePreset::Magic,
            ParticlePreset::Smoke,
            ParticlePreset::Nature,
            ParticlePreset::Celebration,
        ];

        for preset in presets {
            let system = ParticleSystem::with_preset(preset, Vec3::ZERO);
            assert!(system.particle_count() > 0);
        }
    }
}
