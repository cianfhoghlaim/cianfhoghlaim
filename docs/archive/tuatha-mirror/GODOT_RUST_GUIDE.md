# Godot + Rust Guide

Comprehensive guide to using gdext for Godot 4 development with Rust.

## Overview

gdext (formerly godot-rust/gdnative) provides Rust bindings for Godot 4, enabling:
- Type-safe game logic with Rust's safety guarantees
- High-performance game systems
- Shared code between server and client
- Better tooling and IDE support

### Reference Materials

| Resource | Path |
|----------|------|
| gdext Library | `taighde/game/gdext/` |
| React Native Integration | `taighde/game/react-native-godot/` |

---

## Project Setup

### Cargo.toml

```toml
[package]
name = "tuath-game"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
godot = { git = "https://github.com/godot-rust/gdext", branch = "master" }

# Optional: for SpacetimeDB integration
spacetimedb-sdk = "0.8"

# Optional: for serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

### Extension Entry Point

```rust
// src/lib.rs

use godot::prelude::*;

struct TuathExtension;

#[gdextension]
unsafe impl ExtensionLibrary for TuathExtension {}

// Register all your classes
mod player;
mod npc;
mod zone;
mod network;
```

### Godot Project Configuration

```gdextension
# tuath.gdextension

[configuration]
entry_symbol = "gdext_rust_init"
compatibility_minimum = 4.2

[libraries]
macos.debug = "res://bin/libtuath_game.dylib"
macos.release = "res://bin/libtuath_game.dylib"
windows.debug.x86_64 = "res://bin/tuath_game.dll"
windows.release.x86_64 = "res://bin/tuath_game.dll"
linux.debug.x86_64 = "res://bin/libtuath_game.so"
linux.release.x86_64 = "res://bin/libtuath_game.so"
```

---

## Core Concepts

### Creating Nodes

```rust
// src/player.rs

use godot::prelude::*;
use godot::engine::{CharacterBody3D, ICharacterBody3D, InputEvent};

#[derive(GodotClass)]
#[class(base=CharacterBody3D)]
pub struct Player {
    base: Base<CharacterBody3D>,

    #[export]
    speed: f32,

    #[export]
    jump_velocity: f32,

    velocity: Vector3,
    is_grounded: bool,
}

#[godot_api]
impl ICharacterBody3D for Player {
    fn init(base: Base<CharacterBody3D>) -> Self {
        Self {
            base,
            speed: 5.0,
            jump_velocity: 4.5,
            velocity: Vector3::ZERO,
            is_grounded: false,
        }
    }

    fn ready(&mut self) {
        godot_print!("Player ready!");
    }

    fn physics_process(&mut self, delta: f64) {
        self.handle_movement(delta as f32);
        self.apply_gravity(delta as f32);

        // Move the character
        self.base_mut().set_velocity(self.velocity);
        self.base_mut().move_and_slide();

        self.is_grounded = self.base().is_on_floor();
    }
}

#[godot_api]
impl Player {
    fn handle_movement(&mut self, delta: f32) {
        let input = Input::singleton();

        let mut direction = Vector3::ZERO;

        if input.is_action_pressed("move_forward".into()) {
            direction.z -= 1.0;
        }
        if input.is_action_pressed("move_backward".into()) {
            direction.z += 1.0;
        }
        if input.is_action_pressed("move_left".into()) {
            direction.x -= 1.0;
        }
        if input.is_action_pressed("move_right".into()) {
            direction.x += 1.0;
        }

        if direction != Vector3::ZERO {
            direction = direction.normalized();
        }

        self.velocity.x = direction.x * self.speed;
        self.velocity.z = direction.z * self.speed;
    }

    fn apply_gravity(&mut self, delta: f32) {
        if !self.is_grounded {
            self.velocity.y -= 9.8 * delta;
        }
    }

    #[func]
    pub fn jump(&mut self) {
        if self.is_grounded {
            self.velocity.y = self.jump_velocity;
        }
    }

    #[func]
    pub fn get_position(&self) -> Vector3 {
        self.base().get_global_position()
    }

    #[func]
    pub fn set_position(&mut self, pos: Vector3) {
        self.base_mut().set_global_position(pos);
    }
}
```

### Creating Resources

```rust
// src/character_stats.rs

use godot::prelude::*;
use godot::engine::Resource;

#[derive(GodotClass)]
#[class(base=Resource)]
pub struct CharacterStats {
    base: Base<Resource>,

    #[export]
    max_health: i32,

    #[export]
    max_stamina: i32,

    #[export]
    strength: i32,

    #[export]
    agility: i32,

    #[export]
    intelligence: i32,
}

#[godot_api]
impl IResource for CharacterStats {
    fn init(base: Base<Resource>) -> Self {
        Self {
            base,
            max_health: 100,
            max_stamina: 100,
            strength: 10,
            agility: 10,
            intelligence: 10,
        }
    }
}

#[godot_api]
impl CharacterStats {
    #[func]
    pub fn calculate_damage(&self) -> i32 {
        self.strength * 2 + self.agility
    }

    #[func]
    pub fn calculate_defense(&self) -> i32 {
        self.strength + self.agility / 2
    }

    #[func]
    pub fn get_xp_multiplier(&self) -> f32 {
        1.0 + (self.intelligence as f32 * 0.02)
    }
}
```

### Signals

```rust
// src/health_component.rs

use godot::prelude::*;
use godot::engine::Node;

#[derive(GodotClass)]
#[class(base=Node)]
pub struct HealthComponent {
    base: Base<Node>,

    #[export]
    max_health: i32,

    current_health: i32,
}

#[godot_api]
impl INode for HealthComponent {
    fn init(base: Base<Node>) -> Self {
        Self {
            base,
            max_health: 100,
            current_health: 100,
        }
    }

    fn ready(&mut self) {
        self.current_health = self.max_health;
    }
}

#[godot_api]
impl HealthComponent {
    // Define signals
    #[signal]
    fn health_changed(current: i32, max: i32);

    #[signal]
    fn died();

    #[func]
    pub fn take_damage(&mut self, amount: i32) {
        self.current_health = (self.current_health - amount).max(0);

        // Emit signal
        self.base_mut().emit_signal(
            "health_changed".into(),
            &[self.current_health.to_variant(), self.max_health.to_variant()],
        );

        if self.current_health <= 0 {
            self.base_mut().emit_signal("died".into(), &[]);
        }
    }

    #[func]
    pub fn heal(&mut self, amount: i32) {
        self.current_health = (self.current_health + amount).min(self.max_health);

        self.base_mut().emit_signal(
            "health_changed".into(),
            &[self.current_health.to_variant(), self.max_health.to_variant()],
        );
    }

    #[func]
    pub fn get_health_percentage(&self) -> f32 {
        self.current_health as f32 / self.max_health as f32
    }
}
```

---

## NPC System

```rust
// src/npc.rs

use godot::prelude::*;
use godot::engine::{CharacterBody3D, ICharacterBody3D, NavigationAgent3D};

#[derive(GodotClass)]
#[class(base=CharacterBody3D)]
pub struct NPC {
    base: Base<CharacterBody3D>,

    #[export]
    npc_id: GString,

    #[export]
    display_name: GString,

    #[export]
    celtic_name: GString,

    #[export]
    dialogue_id: GString,

    #[export]
    speed: f32,

    nav_agent: Option<Gd<NavigationAgent3D>>,
    state: NPCState,
}

#[derive(Clone, Copy, PartialEq)]
enum NPCState {
    Idle,
    Walking,
    Talking,
}

#[godot_api]
impl ICharacterBody3D for NPC {
    fn init(base: Base<CharacterBody3D>) -> Self {
        Self {
            base,
            npc_id: GString::new(),
            display_name: GString::new(),
            celtic_name: GString::new(),
            dialogue_id: GString::new(),
            speed: 2.0,
            nav_agent: None,
            state: NPCState::Idle,
        }
    }

    fn ready(&mut self) {
        // Get NavigationAgent3D child
        if let Some(agent) = self.base().try_get_node_as::<NavigationAgent3D>("NavigationAgent3D") {
            self.nav_agent = Some(agent);
        }
    }

    fn physics_process(&mut self, delta: f64) {
        match self.state {
            NPCState::Idle => self.process_idle(delta as f32),
            NPCState::Walking => self.process_walking(delta as f32),
            NPCState::Talking => {},
        }
    }
}

#[godot_api]
impl NPC {
    #[signal]
    fn interaction_started(npc_id: GString);

    #[signal]
    fn interaction_ended(npc_id: GString);

    fn process_idle(&mut self, _delta: f32) {
        // Random chance to start walking
        if rand::random::<f32>() < 0.001 {
            self.start_patrol();
        }
    }

    fn process_walking(&mut self, _delta: f32) {
        if let Some(ref nav_agent) = self.nav_agent {
            if nav_agent.is_navigation_finished() {
                self.state = NPCState::Idle;
                return;
            }

            let next_pos = nav_agent.get_next_path_position();
            let current_pos = self.base().get_global_position();

            let direction = (next_pos - current_pos).normalized();
            let velocity = direction * self.speed;

            self.base_mut().set_velocity(velocity);
            self.base_mut().move_and_slide();

            // Face movement direction
            if direction.length() > 0.1 {
                let look_at = current_pos + Vector3::new(direction.x, 0.0, direction.z);
                self.base_mut().look_at(look_at);
            }
        }
    }

    fn start_patrol(&mut self) {
        if let Some(ref mut nav_agent) = self.nav_agent {
            // Random patrol point within range
            let current = self.base().get_global_position();
            let offset = Vector3::new(
                rand::random::<f32>() * 10.0 - 5.0,
                0.0,
                rand::random::<f32>() * 10.0 - 5.0,
            );

            nav_agent.set_target_position(current + offset);
            self.state = NPCState::Walking;
        }
    }

    #[func]
    pub fn interact(&mut self) {
        self.state = NPCState::Talking;

        self.base_mut().emit_signal(
            "interaction_started".into(),
            &[self.npc_id.to_variant()],
        );
    }

    #[func]
    pub fn end_interaction(&mut self) {
        self.state = NPCState::Idle;

        self.base_mut().emit_signal(
            "interaction_ended".into(),
            &[self.npc_id.to_variant()],
        );
    }

    #[func]
    pub fn get_dialogue_id(&self) -> GString {
        self.dialogue_id.clone()
    }
}
```

---

## Zone System

```rust
// src/zone.rs

use godot::prelude::*;
use godot::engine::{Node3D, INode3D};
use std::collections::HashMap;

#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct Zone {
    base: Base<Node3D>,

    #[export]
    zone_id: GString,

    #[export]
    display_name: GString,

    #[export]
    celtic_name: GString,

    #[export]
    language: GString,

    players: HashMap<u64, Gd<Node3D>>,
    npcs: Vec<Gd<Node3D>>,
}

#[godot_api]
impl INode3D for Zone {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            zone_id: GString::new(),
            display_name: GString::new(),
            celtic_name: GString::new(),
            language: "ga".into(),
            players: HashMap::new(),
            npcs: Vec::new(),
        }
    }

    fn ready(&mut self) {
        godot_print!("Zone {} ready", self.zone_id);
        self.spawn_npcs();
    }
}

#[godot_api]
impl Zone {
    #[signal]
    fn player_entered(player_id: i64);

    #[signal]
    fn player_exited(player_id: i64);

    fn spawn_npcs(&mut self) {
        // Load NPC data and spawn
        // This would typically load from a resource file
    }

    #[func]
    pub fn add_player(&mut self, player_id: i64, player_node: Gd<Node3D>) {
        self.players.insert(player_id as u64, player_node.clone());

        // Add as child
        self.base_mut().add_child(player_node.upcast());

        self.base_mut().emit_signal(
            "player_entered".into(),
            &[player_id.to_variant()],
        );
    }

    #[func]
    pub fn remove_player(&mut self, player_id: i64) {
        if let Some(player) = self.players.remove(&(player_id as u64)) {
            player.queue_free();
        }

        self.base_mut().emit_signal(
            "player_exited".into(),
            &[player_id.to_variant()],
        );
    }

    #[func]
    pub fn get_player_count(&self) -> i32 {
        self.players.len() as i32
    }

    #[func]
    pub fn get_language(&self) -> GString {
        self.language.clone()
    }
}
```

---

## Network Integration

```rust
// src/network.rs

use godot::prelude::*;
use godot::engine::{Node, INode};

#[derive(GodotClass)]
#[class(base=Node)]
pub struct NetworkManager {
    base: Base<Node>,

    #[export]
    server_url: GString,

    connected: bool,
}

#[godot_api]
impl INode for NetworkManager {
    fn init(base: Base<Node>) -> Self {
        Self {
            base,
            server_url: "wss://spacetime.clockworklabs.net".into(),
            connected: false,
        }
    }

    fn ready(&mut self) {
        godot_print!("NetworkManager ready");
    }

    fn process(&mut self, _delta: f64) {
        // Poll for network updates
        if self.connected {
            self.poll_updates();
        }
    }
}

#[godot_api]
impl NetworkManager {
    #[signal]
    fn connected_to_server();

    #[signal]
    fn disconnected_from_server();

    #[signal]
    fn player_position_updated(player_id: i64, position: Vector3, rotation: f32);

    #[signal]
    fn chat_message_received(sender_id: i64, message: GString);

    fn poll_updates(&mut self) {
        // Poll SpacetimeDB for updates
        // Emit signals for received data
    }

    #[func]
    pub fn connect_to_server(&mut self) {
        // Connect to SpacetimeDB
        godot_print!("Connecting to {}", self.server_url);

        // ... connection logic ...

        self.connected = true;
        self.base_mut().emit_signal("connected_to_server".into(), &[]);
    }

    #[func]
    pub fn disconnect_from_server(&mut self) {
        self.connected = false;
        self.base_mut().emit_signal("disconnected_from_server".into(), &[]);
    }

    #[func]
    pub fn send_position(&self, x: f32, y: f32, z: f32, rot: f32) {
        if !self.connected {
            return;
        }

        // Send to SpacetimeDB
        // update_position(x, y, z, rot)
    }

    #[func]
    pub fn send_chat(&self, message: GString) {
        if !self.connected {
            return;
        }

        // send_chat(message.to_string())
    }

    #[func]
    pub fn is_connected(&self) -> bool {
        self.connected
    }
}
```

---

## Building

### Development Build

```bash
# Build for current platform
cargo build

# Copy to Godot project
cp target/debug/libtuath_game.dylib godot_project/bin/
```

### Release Build

```bash
# Optimized release build
cargo build --release

# Copy to Godot project
cp target/release/libtuath_game.dylib godot_project/bin/
```

### Cross-Platform Build

```bash
# For Windows (from macOS/Linux with mingw)
cargo build --target x86_64-pc-windows-gnu --release

# For Linux (from macOS)
cargo build --target x86_64-unknown-linux-gnu --release

# For macOS ARM
cargo build --target aarch64-apple-darwin --release
```

---

## Testing

```rust
// src/tests.rs

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_character_stats() {
        let stats = CharacterStats {
            max_health: 100,
            max_stamina: 100,
            strength: 15,
            agility: 12,
            intelligence: 10,
        };

        assert_eq!(stats.calculate_damage(), 42); // 15*2 + 12
    }

    #[test]
    fn test_health_component() {
        // Unit tests for game logic
        // Note: Full Godot integration tests require the editor
    }
}
```

---

## Related Documentation

- [SpacetimeDB Guide](./SPACETIMEDB_GUIDE.md) - Multiplayer backend
- [WGPU Guide](./WGPU_GUIDE.md) - Graphics programming
- [React Native Godot](../react-native-godot/) - Mobile integration
