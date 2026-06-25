//! SpacetimeDB Game Client
//!
//! Manages the connection to SpacetimeDB for real-time game state synchronization.
//! Handles player positions, clan updates, chat, and game events.

use godot::prelude::*;
use std::sync::{Arc, Mutex};

/// Connection status for the SpacetimeDB client
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ConnectionStatus {
    Disconnected,
    Connecting,
    Connected,
    Reconnecting,
    Error,
}

impl GodotConvert for ConnectionStatus {
    type Via = i32;
}

impl ToGodot for ConnectionStatus {
    type ToVia<'v> = i32;

    fn to_godot(&self) -> Self::ToVia<'_> {
        match self {
            ConnectionStatus::Disconnected => 0,
            ConnectionStatus::Connecting => 1,
            ConnectionStatus::Connected => 2,
            ConnectionStatus::Reconnecting => 3,
            ConnectionStatus::Error => 4,
        }
    }
}

impl FromGodot for ConnectionStatus {
    fn try_from_godot(via: Self::Via) -> Result<Self, godot::meta::error::ConvertError> {
        match via {
            0 => Ok(ConnectionStatus::Disconnected),
            1 => Ok(ConnectionStatus::Connecting),
            2 => Ok(ConnectionStatus::Connected),
            3 => Ok(ConnectionStatus::Reconnecting),
            4 => Ok(ConnectionStatus::Error),
            _ => Ok(ConnectionStatus::Disconnected),
        }
    }
}

/// SpacetimeDB game client - singleton for managing game state
#[derive(GodotClass)]
#[class(base=Node)]
pub struct SpacetimeGameClient {
    base: Base<Node>,

    /// SpacetimeDB server URL
    #[var]
    server_url: GString,

    /// Module name/address
    #[var]
    module_name: GString,

    /// Current connection status
    status: ConnectionStatus,

    /// Player's identity token (stored securely)
    identity_token: Option<String>,

    /// Local player ID (assigned by SpacetimeDB)
    #[var]
    local_player_id: u64,

    /// Cached player positions (entity_id -> position)
    player_positions: Arc<Mutex<std::collections::HashMap<u64, Vector3>>>,
}

#[godot_api]
impl INode for SpacetimeGameClient {
    fn init(base: Base<Node>) -> Self {
        Self {
            base,
            server_url: "ws://localhost:3000".into(),
            module_name: "tuath-game".into(),
            status: ConnectionStatus::Disconnected,
            identity_token: None,
            local_player_id: 0,
            player_positions: Arc::new(Mutex::new(std::collections::HashMap::new())),
        }
    }

    fn ready(&mut self) {
        godot_print!("SpacetimeGameClient ready");
    }

    fn process(&mut self, _delta: f64) {
        // Poll SpacetimeDB for updates
        // In production, this would process incoming table updates
        self.poll_updates();
    }
}

#[godot_api]
impl SpacetimeGameClient {
    /// Connect to SpacetimeDB server
    #[func]
    pub fn connect_to_server(&mut self) {
        godot_print!(
            "Connecting to SpacetimeDB: {} module: {}",
            self.server_url,
            self.module_name
        );

        self.status = ConnectionStatus::Connecting;
        self.base_mut().emit_signal("connection_status_changed", &[self.status.to_variant()]);

        // TODO: Actual SpacetimeDB connection
        // spacetimedb_sdk::connect(url, module, on_connect, on_disconnect)?;

        // Simulate successful connection for scaffold
        self.status = ConnectionStatus::Connected;
        self.base_mut().emit_signal("connection_status_changed", &[self.status.to_variant()]);
        self.base_mut().emit_signal("connected", &[]);
    }

    /// Disconnect from server
    #[func]
    pub fn disconnect_from_server(&mut self) {
        godot_print!("Disconnecting from SpacetimeDB");

        self.status = ConnectionStatus::Disconnected;
        self.base_mut().emit_signal("connection_status_changed", &[self.status.to_variant()]);
        self.base_mut().emit_signal("disconnected", &[]);
    }

    /// Get current connection status
    #[func]
    pub fn get_status(&self) -> i32 {
        self.status.to_godot()
    }

    /// Check if connected
    #[func]
    pub fn is_connected(&self) -> bool {
        self.status == ConnectionStatus::Connected
    }

    /// Update local player position (sends to SpacetimeDB)
    #[func]
    pub fn update_position(&mut self, position: Vector3, rotation: f32) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("update_position", position.x, position.y, position.z, rotation);

        // Update local cache
        if let Ok(mut positions) = self.player_positions.lock() {
            positions.insert(self.local_player_id, position);
        }
    }

    /// Get position of another player
    #[func]
    pub fn get_player_position(&self, player_id: u64) -> Vector3 {
        if let Ok(positions) = self.player_positions.lock() {
            positions.get(&player_id).copied().unwrap_or(Vector3::ZERO)
        } else {
            Vector3::ZERO
        }
    }

    /// Send chat message
    #[func]
    pub fn send_chat_message(&mut self, message: GString, channel: GString) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        godot_print!("Sending chat to {}: {}", channel, message);

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("send_chat_message", message, channel);
    }

    /// Join a clan
    #[func]
    pub fn join_clan(&mut self, clan_id: u64) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        godot_print!("Joining clan: {}", clan_id);

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("join_clan", clan_id);
    }

    /// Leave current clan
    #[func]
    pub fn leave_clan(&mut self) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        godot_print!("Leaving clan");

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("leave_clan");
    }

    /// Start a quest
    #[func]
    pub fn start_quest(&mut self, quest_id: u64) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        godot_print!("Starting quest: {}", quest_id);

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("start_quest", quest_id);
    }

    /// Interact with NPC
    #[func]
    pub fn interact_with_npc(&mut self, npc_id: u64) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        godot_print!("Interacting with NPC: {}", npc_id);

        // TODO: Call SpacetimeDB reducer
        // spacetimedb_sdk::call_reducer("interact_with_npc", npc_id);
    }

    /// Poll for SpacetimeDB updates (called each frame)
    fn poll_updates(&mut self) {
        if self.status != ConnectionStatus::Connected {
            return;
        }

        // TODO: Process SpacetimeDB subscription updates
        // This would handle:
        // - Player position updates
        // - Chat messages
        // - Quest updates
        // - NPC state changes
        // - Clan updates
    }

    // Signals
    #[signal]
    fn connected();

    #[signal]
    fn disconnected();

    #[signal]
    fn connection_status_changed(status: i32);

    #[signal]
    fn player_joined(player_id: u64, player_name: GString);

    #[signal]
    fn player_left(player_id: u64);

    #[signal]
    fn player_position_updated(player_id: u64, position: Vector3, rotation: f32);

    #[signal]
    fn chat_message_received(sender_id: u64, sender_name: GString, message: GString, channel: GString);

    #[signal]
    fn quest_started(quest_id: u64, quest_name: GString);

    #[signal]
    fn quest_completed(quest_id: u64);

    #[signal]
    fn npc_dialogue(npc_id: u64, dialogue_text: GString, options: Array<GString>);
}
