//! Alba Zone
//!
//! Scottish Highlands region featuring:
//! - Highland wilderness
//! - Ancient castles
//! - Loch environments
//! - Scottish Gaelic culture

use godot::prelude::*;
use godot::classes::{Node3D, INode3D};
use super::{ZoneType, Weather, TimeOfDay};

/// Sub-regions within Alba (Scotland)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AlbaRegion {
    /// Scottish Highlands
    Highlands,
    /// Isle of Skye
    IsleOfSkye,
    /// Loch Ness area
    LochNess,
    /// Edinburgh region
    Edinburgh,
    /// Outer Hebrides
    OuterHebrides,
}

/// Alba (Scotland) zone controller
#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct AlbaZone {
    base: Base<Node3D>,

    /// Current sub-region
    region: AlbaRegion,

    /// Current weather
    weather: Weather,

    /// Current time of day
    time_of_day: TimeOfDay,

    /// Zone display name
    #[var]
    display_name: GString,

    /// Scottish Gaelic name
    #[var]
    celtic_name: GString,

    /// Ambient sound volume
    #[var]
    ambient_volume: f32,

    /// Music track name
    #[var]
    music_track: GString,

    /// Player count in zone
    #[var]
    player_count: i32,
}

#[godot_api]
impl INode3D for AlbaZone {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            region: AlbaRegion::Highlands,
            weather: Weather::Cloudy,
            time_of_day: TimeOfDay::Morning,
            display_name: "Alba".into(),
            celtic_name: "Alba".into(),
            ambient_volume: 0.8,
            music_track: "alba_theme".into(),
            player_count: 0,
        }
    }

    fn ready(&mut self) {
        godot_print!("AlbaZone ready: {}", self.celtic_name);
        self.update_zone_settings();
    }

    fn process(&mut self, _delta: f64) {
        // Zone-specific processing
    }
}

#[godot_api]
impl AlbaZone {
    /// Set the current region
    #[func]
    pub fn set_region(&mut self, region_id: i32) {
        self.region = match region_id {
            0 => AlbaRegion::Highlands,
            1 => AlbaRegion::IsleOfSkye,
            2 => AlbaRegion::LochNess,
            3 => AlbaRegion::Edinburgh,
            4 => AlbaRegion::OuterHebrides,
            _ => AlbaRegion::Highlands,
        };

        self.update_zone_settings();
        self.base_mut().emit_signal("region_changed", &[region_id.to_variant()]);
    }

    /// Get current region as integer
    #[func]
    pub fn get_region(&self) -> i32 {
        match self.region {
            AlbaRegion::Highlands => 0,
            AlbaRegion::IsleOfSkye => 1,
            AlbaRegion::LochNess => 2,
            AlbaRegion::Edinburgh => 3,
            AlbaRegion::OuterHebrides => 4,
        }
    }

    /// Update zone settings based on region
    fn update_zone_settings(&mut self) {
        match self.region {
            AlbaRegion::Highlands => {
                self.display_name = "Scottish Highlands".into();
                self.celtic_name = "A' Ghaidhealtachd".into();
                self.music_track = "highlands_theme".into();
            }
            AlbaRegion::IsleOfSkye => {
                self.display_name = "Isle of Skye".into();
                self.celtic_name = "An t-Eilean Sgitheanach".into();
                self.music_track = "skye_theme".into();
            }
            AlbaRegion::LochNess => {
                self.display_name = "Loch Ness".into();
                self.celtic_name = "Loch Nis".into();
                self.music_track = "loch_theme".into();
            }
            AlbaRegion::Edinburgh => {
                self.display_name = "Edinburgh".into();
                self.celtic_name = "Dun Eideann".into();
                self.music_track = "edinburgh_theme".into();
            }
            AlbaRegion::OuterHebrides => {
                self.display_name = "Outer Hebrides".into();
                self.celtic_name = "Na h-Eileanan Siar".into();
                self.music_track = "hebrides_theme".into();
            }
        }
    }

    /// Called when player enters zone
    #[func]
    pub fn on_player_enter(&mut self, player_id: u64) {
        self.player_count += 1;
        godot_print!("Player {} entered {}", player_id, self.celtic_name);
        self.base_mut().emit_signal("player_entered", &[player_id.to_variant()]);
    }

    /// Called when player exits zone
    #[func]
    pub fn on_player_exit(&mut self, player_id: u64) {
        self.player_count -= 1;
        godot_print!("Player {} exited {}", player_id, self.celtic_name);
        self.base_mut().emit_signal("player_exited", &[player_id.to_variant()]);
    }

    // Signals
    #[signal]
    fn region_changed(region: i32);

    #[signal]
    fn player_entered(player_id: u64);

    #[signal]
    fn player_exited(player_id: u64);
}
