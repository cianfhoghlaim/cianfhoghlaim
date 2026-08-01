//! Player Controller
//!
//! Manages player character movement, animation, and state.
//! Syncs with SpacetimeDB for multiplayer position updates.

use godot::prelude::*;
use godot::classes::{CharacterBody3D, ICharacterBody3D, AnimationPlayer};

/// Player movement state
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PlayerState {
    Idle,
    Walking,
    Running,
    Jumping,
    Falling,
    Swimming,
    Mounted,
    InDialogue,
    InCombat,
}

/// Player controller for the local player character
#[derive(GodotClass)]
#[class(base=CharacterBody3D)]
pub struct PlayerController {
    base: Base<CharacterBody3D>,

    /// Movement speed (units per second)
    #[var]
    walk_speed: f32,

    /// Running speed multiplier
    #[var]
    run_speed: f32,

    /// Jump velocity
    #[var]
    jump_velocity: f32,

    /// Gravity force
    #[var]
    gravity: f32,

    /// Mouse sensitivity for camera rotation
    #[var]
    mouse_sensitivity: f32,

    /// Current player state
    state: PlayerState,

    /// Current velocity
    velocity: Vector3,

    /// Camera rotation (yaw/pitch)
    camera_rotation: Vector2,

    /// Is this the local player?
    #[var]
    is_local_player: bool,

    /// Network sync rate (updates per second)
    #[var]
    sync_rate: f32,

    /// Time since last network sync
    sync_timer: f32,
}

#[godot_api]
impl ICharacterBody3D for PlayerController {
    fn init(base: Base<CharacterBody3D>) -> Self {
        Self {
            base,
            walk_speed: 5.0,
            run_speed: 10.0,
            jump_velocity: 8.0,
            gravity: 20.0,
            mouse_sensitivity: 0.003,
            state: PlayerState::Idle,
            velocity: Vector3::ZERO,
            camera_rotation: Vector2::ZERO,
            is_local_player: true,
            sync_rate: 20.0,
            sync_timer: 0.0,
        }
    }

    fn ready(&mut self) {
        if self.is_local_player {
            // Capture mouse for camera control
            godot::classes::Input::singleton().set_mouse_mode(
                godot::classes::input::MouseMode::CAPTURED,
            );
        }
    }

    fn physics_process(&mut self, delta: f64) {
        let delta = delta as f32;

        if self.is_local_player {
            self.process_input(delta);
            self.process_movement(delta);
            self.update_network_sync(delta);
        } else {
            // Remote player - interpolate to target position
            self.interpolate_remote_position(delta);
        }
    }
}

#[godot_api]
impl PlayerController {
    /// Process player input
    fn process_input(&mut self, _delta: f32) {
        let input = godot::classes::Input::singleton();

        // Get movement input
        let mut input_dir = Vector2::ZERO;

        if input.is_action_pressed("move_forward") {
            input_dir.y -= 1.0;
        }
        if input.is_action_pressed("move_back") {
            input_dir.y += 1.0;
        }
        if input.is_action_pressed("move_left") {
            input_dir.x -= 1.0;
        }
        if input.is_action_pressed("move_right") {
            input_dir.x += 1.0;
        }

        input_dir = input_dir.normalized();

        // Determine speed (run vs walk)
        let speed = if input.is_action_pressed("sprint") {
            self.run_speed
        } else {
            self.walk_speed
        };

        // Convert input to world-space velocity
        let basis = self.base().get_global_transform().basis;
        let forward = -basis.col_c(); // Forward is -Z
        let right = basis.col_a();    // Right is +X

        let direction = (forward * input_dir.y + right * input_dir.x).normalized();

        self.velocity.x = direction.x * speed;
        self.velocity.z = direction.z * speed;

        // Update state based on movement
        if input_dir.length() > 0.1 {
            self.state = if input.is_action_pressed("sprint") {
                PlayerState::Running
            } else {
                PlayerState::Walking
            };
        } else {
            self.state = PlayerState::Idle;
        }

        // Jump
        if input.is_action_just_pressed("jump") && self.base().is_on_floor() {
            self.velocity.y = self.jump_velocity;
            self.state = PlayerState::Jumping;
        }
    }

    /// Process physics movement
    fn process_movement(&mut self, delta: f32) {
        // Apply gravity
        if !self.base().is_on_floor() {
            self.velocity.y -= self.gravity * delta;

            if self.velocity.y < 0.0 {
                self.state = PlayerState::Falling;
            }
        }

        // Move character
        self.base_mut().set_velocity(self.velocity);
        self.base_mut().move_and_slide();

        // Update velocity from physics
        self.velocity = self.base().get_velocity();
    }

    /// Update network synchronization
    fn update_network_sync(&mut self, delta: f32) {
        self.sync_timer += delta;

        if self.sync_timer >= 1.0 / self.sync_rate {
            self.sync_timer = 0.0;

            // Emit signal for network sync
            let position = self.base().get_global_position();
            let rotation = self.base().get_global_rotation().y;

            self.base_mut().emit_signal(
                "position_updated",
                &[position.to_variant(), rotation.to_variant()],
            );
        }
    }

    /// Interpolate remote player position (for network sync)
    fn interpolate_remote_position(&mut self, _delta: f32) {
        // TODO: Smooth interpolation to target position for remote players
    }

    /// Set target position (for remote players)
    #[func]
    pub fn set_target_position(&mut self, position: Vector3, rotation: f32) {
        if !self.is_local_player {
            self.base_mut().set_global_position(position);
            let mut rot = self.base().get_global_rotation();
            rot.y = rotation;
            self.base_mut().set_global_rotation(rot);
        }
    }

    /// Get current player state as integer
    #[func]
    pub fn get_state(&self) -> i32 {
        match self.state {
            PlayerState::Idle => 0,
            PlayerState::Walking => 1,
            PlayerState::Running => 2,
            PlayerState::Jumping => 3,
            PlayerState::Falling => 4,
            PlayerState::Swimming => 5,
            PlayerState::Mounted => 6,
            PlayerState::InDialogue => 7,
            PlayerState::InCombat => 8,
        }
    }

    /// Enter dialogue mode
    #[func]
    pub fn enter_dialogue(&mut self) {
        self.state = PlayerState::InDialogue;
        self.velocity = Vector3::ZERO;

        // Release mouse for UI interaction
        godot::classes::Input::singleton().set_mouse_mode(
            godot::classes::input::MouseMode::VISIBLE,
        );
    }

    /// Exit dialogue mode
    #[func]
    pub fn exit_dialogue(&mut self) {
        self.state = PlayerState::Idle;

        // Recapture mouse
        godot::classes::Input::singleton().set_mouse_mode(
            godot::classes::input::MouseMode::CAPTURED,
        );
    }

    // Signals
    #[signal]
    fn position_updated(position: Vector3, rotation: f32);

    #[signal]
    fn state_changed(new_state: i32);
}
