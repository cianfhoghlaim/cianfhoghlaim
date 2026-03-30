//! Third Person Camera
//!
//! Provides smooth third-person camera following and orbiting.
//! Handles collision avoidance with terrain and objects.

use godot::prelude::*;
use godot::classes::{Node3D, INode3D, Camera3D, SpringArm3D};

/// Third-person camera controller
#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct ThirdPersonCamera {
    base: Base<Node3D>,

    /// Target to follow (usually the player)
    target: Option<Gd<Node3D>>,

    /// Camera distance from target
    #[var]
    distance: f32,

    /// Minimum distance
    #[var]
    min_distance: f32,

    /// Maximum distance
    #[var]
    max_distance: f32,

    /// Current rotation (yaw, pitch)
    rotation: Vector2,

    /// Minimum pitch angle (looking up)
    #[var]
    min_pitch: f32,

    /// Maximum pitch angle (looking down)
    #[var]
    max_pitch: f32,

    /// Mouse sensitivity
    #[var]
    mouse_sensitivity: f32,

    /// Camera smoothing factor
    #[var]
    smoothing: f32,

    /// Zoom sensitivity (scroll wheel)
    #[var]
    zoom_sensitivity: f32,

    /// Height offset from target
    #[var]
    height_offset: f32,

    /// Whether camera control is enabled
    #[var]
    enabled: bool,
}

#[godot_api]
impl INode3D for ThirdPersonCamera {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            target: None,
            distance: 5.0,
            min_distance: 2.0,
            max_distance: 15.0,
            rotation: Vector2::ZERO,
            min_pitch: -1.2,  // ~-70 degrees
            max_pitch: 0.8,   // ~45 degrees
            mouse_sensitivity: 0.003,
            smoothing: 0.1,
            zoom_sensitivity: 0.5,
            height_offset: 1.5,
            enabled: true,
        }
    }

    fn ready(&mut self) {
        godot_print!("ThirdPersonCamera ready");
    }

    fn process(&mut self, delta: f64) {
        if !self.enabled {
            return;
        }

        self.update_camera_position(delta as f32);
    }

    fn input(&mut self, event: Gd<godot::classes::InputEvent>) {
        if !self.enabled {
            return;
        }

        // Handle mouse motion for camera rotation
        if let Ok(motion) = event.try_cast::<godot::classes::InputEventMouseMotion>() {
            let relative = motion.get_relative();

            self.rotation.x -= relative.x * self.mouse_sensitivity;
            self.rotation.y -= relative.y * self.mouse_sensitivity;

            // Clamp pitch
            self.rotation.y = self.rotation.y.clamp(self.min_pitch, self.max_pitch);
        }

        // Handle scroll wheel for zoom
        if let Ok(button) = event.try_cast::<godot::classes::InputEventMouseButton>() {
            if button.is_pressed() {
                match button.get_button_index() {
                    godot::classes::global::MouseButton::WHEEL_UP => {
                        self.distance = (self.distance - self.zoom_sensitivity)
                            .clamp(self.min_distance, self.max_distance);
                    }
                    godot::classes::global::MouseButton::WHEEL_DOWN => {
                        self.distance = (self.distance + self.zoom_sensitivity)
                            .clamp(self.min_distance, self.max_distance);
                    }
                    _ => {}
                }
            }
        }
    }
}

#[godot_api]
impl ThirdPersonCamera {
    /// Update camera position to follow target
    fn update_camera_position(&mut self, _delta: f32) {
        let target = match &self.target {
            Some(t) => t.clone(),
            None => return,
        };

        // Get target position with height offset
        let mut target_pos = target.get_global_position();
        target_pos.y += self.height_offset;

        // Calculate camera offset based on rotation
        let offset = Vector3::new(
            self.distance * self.rotation.y.cos() * self.rotation.x.sin(),
            self.distance * self.rotation.y.sin(),
            self.distance * self.rotation.y.cos() * self.rotation.x.cos(),
        );

        let desired_pos = target_pos + offset;

        // Smooth movement (lerp)
        let current_pos = self.base().get_global_position();
        let new_pos = current_pos.lerp(desired_pos, self.smoothing);

        self.base_mut().set_global_position(new_pos);

        // Look at target
        self.base_mut().look_at(target_pos);
    }

    /// Set the target to follow
    #[func]
    pub fn set_target(&mut self, target: Gd<Node3D>) {
        self.target = Some(target);
    }

    /// Clear the target
    #[func]
    pub fn clear_target(&mut self) {
        self.target = None;
    }

    /// Set camera rotation directly
    #[func]
    pub fn set_rotation_angles(&mut self, yaw: f32, pitch: f32) {
        self.rotation.x = yaw;
        self.rotation.y = pitch.clamp(self.min_pitch, self.max_pitch);
    }

    /// Get current yaw angle
    #[func]
    pub fn get_yaw(&self) -> f32 {
        self.rotation.x
    }

    /// Get current pitch angle
    #[func]
    pub fn get_pitch(&self) -> f32 {
        self.rotation.y
    }

    /// Reset camera to default position behind target
    #[func]
    pub fn reset_position(&mut self) {
        self.rotation = Vector2::ZERO;
        self.distance = 5.0;
    }

    /// Shake camera (for impacts/explosions)
    #[func]
    pub fn shake(&mut self, _intensity: f32, _duration: f32) {
        // TODO: Implement camera shake
    }
}
