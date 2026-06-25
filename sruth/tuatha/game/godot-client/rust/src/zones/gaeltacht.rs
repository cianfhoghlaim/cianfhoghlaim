//! Gaeltacht Zone
//!
//! Irish-speaking regions of Ireland:
//! - Conamara (Connacht)
//! - Corca Dhuibhne (Kerry/Munster)
//! - Gaoth Dobhair (Donegal/Ulster)
//! - Aran Islands

use godot::prelude::*;
use godot::classes::{Node3D, INode3D};
use super::{ZoneType, Weather, TimeOfDay};

/// Sub-regions within Gaeltacht
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GaeltachtRegion {
    /// Conamara, County Galway
    Conamara,
    /// Corca Dhuibhne, County Kerry
    CorcaDhuibhne,
    /// Gaoth Dobhair, County Donegal
    GaothDobhair,
    /// Aran Islands
    AranIslands,
    /// Ring of Kerry
    RingOfKerry,
}

/// Gaeltacht zone controller
#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct GaeltachtZone {
    base: Base<Node3D>,

    /// Current sub-region
    region: GaeltachtRegion,

    /// Current weather
    weather: Weather,

    /// Current time of day
    time_of_day: TimeOfDay,

    /// Zone display name
    #[var]
    display_name: GString,

    /// Irish name
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

    /// Weather cycle timer
    weather_timer: f32,

    /// Day/night cycle timer
    day_cycle_timer: f32,
}

#[godot_api]
impl INode3D for GaeltachtZone {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            region: GaeltachtRegion::Conamara,
            weather: Weather::Cloudy,
            time_of_day: TimeOfDay::Morning,
            display_name: "Gaeltacht".into(),
            celtic_name: "An Ghaeltacht".into(),
            ambient_volume: 0.8,
            music_track: "gaeltacht_theme".into(),
            player_count: 0,
            weather_timer: 0.0,
            day_cycle_timer: 0.0,
        }
    }

    fn ready(&mut self) {
        godot_print!("GaeltachtZone ready: {}", self.celtic_name);
        self.update_zone_settings();
    }

    fn process(&mut self, delta: f64) {
        let delta = delta as f32;

        self.update_weather_cycle(delta);
        self.update_day_cycle(delta);
    }
}

#[godot_api]
impl GaeltachtZone {
    /// Set the current region
    #[func]
    pub fn set_region(&mut self, region_id: i32) {
        self.region = match region_id {
            0 => GaeltachtRegion::Conamara,
            1 => GaeltachtRegion::CorcaDhuibhne,
            2 => GaeltachtRegion::GaothDobhair,
            3 => GaeltachtRegion::AranIslands,
            4 => GaeltachtRegion::RingOfKerry,
            _ => GaeltachtRegion::Conamara,
        };

        self.update_zone_settings();
        self.base_mut().emit_signal("region_changed", &[region_id.to_variant()]);
    }

    /// Get current region as integer
    #[func]
    pub fn get_region(&self) -> i32 {
        match self.region {
            GaeltachtRegion::Conamara => 0,
            GaeltachtRegion::CorcaDhuibhne => 1,
            GaeltachtRegion::GaothDobhair => 2,
            GaeltachtRegion::AranIslands => 3,
            GaeltachtRegion::RingOfKerry => 4,
        }
    }

    /// Update zone settings based on region
    fn update_zone_settings(&mut self) {
        match self.region {
            GaeltachtRegion::Conamara => {
                self.display_name = "Conamara".into();
                self.celtic_name = "Conamara".into();
                self.music_track = "conamara_theme".into();
            }
            GaeltachtRegion::CorcaDhuibhne => {
                self.display_name = "Corca Dhuibhne".into();
                self.celtic_name = "Corca Dhuibhne".into();
                self.music_track = "kerry_theme".into();
            }
            GaeltachtRegion::GaothDobhair => {
                self.display_name = "Gaoth Dobhair".into();
                self.celtic_name = "Gaoth Dobhair".into();
                self.music_track = "donegal_theme".into();
            }
            GaeltachtRegion::AranIslands => {
                self.display_name = "Aran Islands".into();
                self.celtic_name = "Oileain Arann".into();
                self.music_track = "aran_theme".into();
            }
            GaeltachtRegion::RingOfKerry => {
                self.display_name = "Ring of Kerry".into();
                self.celtic_name = "Morthimpeall Chiarrai".into();
                self.music_track = "kerry_theme".into();
            }
        }
    }

    /// Update weather cycle
    fn update_weather_cycle(&mut self, delta: f32) {
        self.weather_timer += delta;

        // Weather changes every 5 minutes (300 seconds) of game time
        if self.weather_timer >= 300.0 {
            self.weather_timer = 0.0;
            self.change_weather();
        }
    }

    /// Change weather randomly (but weighted for Irish climate)
    fn change_weather(&mut self) {
        // Ireland has lots of rain and clouds!
        let roll = godot::global::randf();
        self.weather = if roll < 0.3 {
            Weather::Rain
        } else if roll < 0.6 {
            Weather::Cloudy
        } else if roll < 0.75 {
            Weather::Fog
        } else if roll < 0.9 {
            Weather::Clear
        } else {
            Weather::Storm
        };

        self.base_mut().emit_signal("weather_changed", &[self.get_weather().to_variant()]);
    }

    /// Get current weather as integer
    #[func]
    pub fn get_weather(&self) -> i32 {
        match self.weather {
            Weather::Clear => 0,
            Weather::Cloudy => 1,
            Weather::Rain => 2,
            Weather::Storm => 3,
            Weather::Fog => 4,
            Weather::Snow => 5,
        }
    }

    /// Set weather directly
    #[func]
    pub fn set_weather(&mut self, weather_id: i32) {
        self.weather = match weather_id {
            0 => Weather::Clear,
            1 => Weather::Cloudy,
            2 => Weather::Rain,
            3 => Weather::Storm,
            4 => Weather::Fog,
            5 => Weather::Snow,
            _ => Weather::Cloudy,
        };

        self.base_mut().emit_signal("weather_changed", &[weather_id.to_variant()]);
    }

    /// Update day/night cycle
    fn update_day_cycle(&mut self, delta: f32) {
        self.day_cycle_timer += delta;

        // Full day cycle every 24 minutes (1 minute = 1 hour)
        let cycle_duration = 24.0 * 60.0;
        if self.day_cycle_timer >= cycle_duration {
            self.day_cycle_timer = 0.0;
        }

        // Determine time of day based on timer
        let hour = (self.day_cycle_timer / 60.0) as i32;
        let new_time = match hour {
            5..=7 => TimeOfDay::Dawn,
            8..=11 => TimeOfDay::Morning,
            12..=13 => TimeOfDay::Noon,
            14..=17 => TimeOfDay::Afternoon,
            18..=20 => TimeOfDay::Dusk,
            _ => TimeOfDay::Night,
        };

        if new_time != self.time_of_day {
            self.time_of_day = new_time;
            self.base_mut().emit_signal("time_changed", &[self.get_time_of_day().to_variant()]);
        }
    }

    /// Get current time of day as integer
    #[func]
    pub fn get_time_of_day(&self) -> i32 {
        match self.time_of_day {
            TimeOfDay::Dawn => 0,
            TimeOfDay::Morning => 1,
            TimeOfDay::Noon => 2,
            TimeOfDay::Afternoon => 3,
            TimeOfDay::Dusk => 4,
            TimeOfDay::Night => 5,
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
    fn weather_changed(weather: i32);

    #[signal]
    fn time_changed(time_of_day: i32);

    #[signal]
    fn player_entered(player_id: u64);

    #[signal]
    fn player_exited(player_id: u64);
}
