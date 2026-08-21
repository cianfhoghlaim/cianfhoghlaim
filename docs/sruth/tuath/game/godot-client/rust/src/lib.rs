//! Tuath Celtic MMO - Godot GDExtension
//!
//! This extension provides Rust-powered game logic for the Tuath Celtic MMO:
//! - SpacetimeDB network client for real-time multiplayer
//! - Player and NPC entity management
//! - Camera and input handling systems
//! - Zone-specific game logic (Gaeltacht, Alba, Cymru)

use godot::prelude::*;

mod entities;
mod network;
mod systems;
mod zones;

/// GDExtension entry point
struct TuathExtension;

#[gdextension]
unsafe impl ExtensionLibrary for TuathExtension {
    fn min_level() -> InitLevel {
        InitLevel::Scene
    }

    fn on_level_init(level: InitLevel) {
        if level == InitLevel::Scene {
            godot_print!("Tuath Celtic MMO Extension initialized!");

            // Initialize tracing for logging
            #[cfg(debug_assertions)]
            {
                use tracing_subscriber::{fmt, EnvFilter};
                let _ = fmt()
                    .with_env_filter(EnvFilter::from_default_env())
                    .try_init();
            }
        }
    }

    fn on_level_deinit(level: InitLevel) {
        if level == InitLevel::Scene {
            godot_print!("Tuath Celtic MMO Extension shutting down...");
        }
    }
}
