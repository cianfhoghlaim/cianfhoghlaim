//! Zones module - Celtic regions of the game world
//!
//! Each zone represents a Celtic cultural region:
//! - Gaeltacht: Irish-speaking regions (Connacht, Munster, Ulster)
//! - Alba: Scottish Highlands
//! - Cymru: Wales

mod gaeltacht;
mod alba;
mod cymru;

pub use gaeltacht::GaeltachtZone;
pub use alba::AlbaZone;
pub use cymru::CymruZone;

use godot::prelude::*;

/// Zone type enumeration
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ZoneType {
    Gaeltacht,
    Alba,
    Cymru,
}

/// Weather types for zones
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Weather {
    Clear,
    Cloudy,
    Rain,
    Storm,
    Fog,
    Snow,
}

/// Time of day
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TimeOfDay {
    Dawn,
    Morning,
    Noon,
    Afternoon,
    Dusk,
    Night,
}

/// Base trait for zone-specific behavior
pub trait ZoneBehavior {
    /// Get the zone type
    fn zone_type(&self) -> ZoneType;

    /// Get the display name
    fn display_name(&self) -> &str;

    /// Get the Irish/Celtic name
    fn celtic_name(&self) -> &str;

    /// Update zone-specific logic
    fn update(&mut self, delta: f32);

    /// Called when player enters the zone
    fn on_player_enter(&mut self);

    /// Called when player exits the zone
    fn on_player_exit(&mut self);
}
