//! Cymru Zone
//!
//! Wales region featuring:
//! - Snowdonia mountains
//! - Welsh castles
//! - Coastal areas
//! - Welsh language and culture

use godot::prelude::*;
use godot::classes::{Node3D, INode3D};
use super::{ZoneType, Weather, TimeOfDay};

/// Sub-regions within Cymru (Wales)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CymruRegion {
    /// Snowdonia National Park
    Snowdonia,
    /// Pembrokeshire coast
    Pembrokeshire,
    /// Anglesey island
    Anglesey,
    /// Cardiff region
    Cardiff,
    /// Brecon Beacons
    BreconBeacons,
}

/// Cymru (Wales) zone controller
#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct CymruZone {
    base: Base<Node3D>,

    /// Current sub-region
    region: CymruRegion,

    /// Current weather
    weather: Weather,

    /// Current time of day
    time_of_day: TimeOfDay,

    /// Zone display name
    #[var]
    display_name: GString,

    /// Welsh name
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
impl INode3D for CymruZone {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            region: CymruRegion::Snowdonia,
            weather: Weather::Cloudy,
            time_of_day: TimeOfDay::Morning,
            display_name: "Cymru".into(),
            celtic_name: "Cymru".into(),
            ambient_volume: 0.8,
            music_track: "cymru_theme".into(),
            player_count: 0,
        }
    }

    fn ready(&mut self) {
        godot_print!("CymruZone ready: {}", self.celtic_name);
        self.update_zone_settings();
    }

    fn process(&mut self, _delta: f64) {
        // Zone-specific processing
    }
}

#[godot_api]
impl CymruZone {
    /// Set the current region
    #[func]
    pub fn set_region(&mut self, region_id: i32) {
        self.region = match region_id {
            0 => CymruRegion::Snowdonia,
            1 => CymruRegion::Pembrokeshire,
            2 => CymruRegion::Anglesey,
            3 => CymruRegion::Cardiff,
            4 => CymruRegion::BreconBeacons,
            _ => CymruRegion::Snowdonia,
        };

        self.update_zone_settings();
        self.base_mut().emit_signal("region_changed", &[region_id.to_variant()]);
    }

    /// Get current region as integer
    #[func]
    pub fn get_region(&self) -> i32 {
        match self.region {
            CymruRegion::Snowdonia => 0,
            CymruRegion::Pembrokeshire => 1,
            CymruRegion::Anglesey => 2,
            CymruRegion::Cardiff => 3,
            CymruRegion::BreconBeacons => 4,
        }
    }

    /// Update zone settings based on region
    fn update_zone_settings(&mut self) {
        match self.region {
            CymruRegion::Snowdonia => {
                self.display_name = "Snowdonia".into();
                self.celtic_name = "Eryri".into();
                self.music_track = "snowdonia_theme".into();
            }
            CymruRegion::Pembrokeshire => {
                self.display_name = "Pembrokeshire".into();
                self.celtic_name = "Sir Benfro".into();
                self.music_track = "pembrokeshire_theme".into();
            }
            CymruRegion::Anglesey => {
                self.display_name = "Anglesey".into();
                self.celtic_name = "Ynys Mon".into();
                self.music_track = "anglesey_theme".into();
            }
            CymruRegion::Cardiff => {
                self.display_name = "Cardiff".into();
                self.celtic_name = "Caerdydd".into();
                self.music_track = "cardiff_theme".into();
            }
            CymruRegion::BreconBeacons => {
                self.display_name = "Brecon Beacons".into();
                self.celtic_name = "Bannau Brycheiniog".into();
                self.music_track = "brecon_theme".into();
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
