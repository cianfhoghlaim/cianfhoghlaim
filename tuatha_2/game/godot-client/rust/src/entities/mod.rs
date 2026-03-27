//! Entities module - Game characters and objects
//!
//! Provides player and NPC entity management.

mod player;
mod npc;

pub use player::PlayerController;
pub use npc::NpcController;
