//! NPC Controller
//!
//! Manages non-player characters including Celtic mythological figures,
//! quest givers, merchants, and ambient characters.

use godot::prelude::*;
use godot::classes::{CharacterBody3D, ICharacterBody3D, NavigationAgent3D};

/// NPC behavior type
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NpcType {
    /// Quest giver NPC
    QuestGiver,
    /// Merchant/shop keeper
    Merchant,
    /// Ambient wandering NPC
    Ambient,
    /// Celtic deity or mythological figure
    MythologicalFigure,
    /// Combat enemy
    Enemy,
    /// Friendly ally
    Ally,
}

/// NPC state
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NpcState {
    Idle,
    Walking,
    Talking,
    Trading,
    Combat,
    Fleeing,
    Dead,
}

/// NPC Controller for game NPCs
#[derive(GodotClass)]
#[class(base=CharacterBody3D)]
pub struct NpcController {
    base: Base<CharacterBody3D>,

    /// NPC unique ID (from SpacetimeDB)
    #[var]
    npc_id: u64,

    /// NPC display name
    #[var]
    display_name: GString,

    /// NPC type
    npc_type: NpcType,

    /// Current state
    state: NpcState,

    /// Movement speed
    #[var]
    walk_speed: f32,

    /// Interaction radius
    #[var]
    interaction_radius: f32,

    /// Current dialogue node (if in conversation)
    #[var]
    current_dialogue_node: GString,

    /// Whether player is nearby
    player_nearby: bool,

    /// Path to patrol waypoints (for ambient NPCs)
    patrol_points: Vec<Vector3>,

    /// Current patrol index
    patrol_index: usize,
}

#[godot_api]
impl ICharacterBody3D for NpcController {
    fn init(base: Base<CharacterBody3D>) -> Self {
        Self {
            base,
            npc_id: 0,
            display_name: "NPC".into(),
            npc_type: NpcType::Ambient,
            state: NpcState::Idle,
            walk_speed: 2.0,
            interaction_radius: 3.0,
            current_dialogue_node: "".into(),
            player_nearby: false,
            patrol_points: Vec::new(),
            patrol_index: 0,
        }
    }

    fn ready(&mut self) {
        godot_print!("NPC {} ready: {}", self.npc_id, self.display_name);
    }

    fn physics_process(&mut self, delta: f64) {
        let delta = delta as f32;

        match self.state {
            NpcState::Idle => self.process_idle(delta),
            NpcState::Walking => self.process_walking(delta),
            NpcState::Talking => {} // Stand still during dialogue
            NpcState::Trading => {} // Stand still during trading
            NpcState::Combat => self.process_combat(delta),
            NpcState::Fleeing => self.process_fleeing(delta),
            NpcState::Dead => {} // No processing when dead
        }
    }
}

#[godot_api]
impl NpcController {
    /// Process idle behavior
    fn process_idle(&mut self, _delta: f32) {
        // Check for player interaction
        if self.player_nearby && !self.patrol_points.is_empty() {
            // Start patrolling if not interacting
            self.state = NpcState::Walking;
        }
    }

    /// Process walking/patrol behavior
    fn process_walking(&mut self, _delta: f32) {
        if self.patrol_points.is_empty() {
            self.state = NpcState::Idle;
            return;
        }

        let target = self.patrol_points[self.patrol_index];
        let current_pos = self.base().get_global_position();
        let distance = current_pos.distance_to(target);

        if distance < 0.5 {
            // Reached waypoint, move to next
            self.patrol_index = (self.patrol_index + 1) % self.patrol_points.len();
        } else {
            // Move toward waypoint
            let direction = (target - current_pos).normalized();
            let velocity = direction * self.walk_speed;
            self.base_mut().set_velocity(velocity);
            self.base_mut().move_and_slide();

            // Face movement direction
            if direction.length() > 0.01 {
                let angle = direction.x.atan2(direction.z);
                let mut rot = self.base().get_global_rotation();
                rot.y = angle;
                self.base_mut().set_global_rotation(rot);
            }
        }
    }

    /// Process combat behavior
    fn process_combat(&mut self, _delta: f32) {
        // TODO: Combat AI
    }

    /// Process fleeing behavior
    fn process_fleeing(&mut self, _delta: f32) {
        // TODO: Flee AI
    }

    /// Initialize NPC from SpacetimeDB data
    #[func]
    pub fn init_from_data(
        &mut self,
        npc_id: u64,
        name: GString,
        npc_type: i32,
        position: Vector3,
    ) {
        self.npc_id = npc_id;
        self.display_name = name;
        self.npc_type = match npc_type {
            0 => NpcType::QuestGiver,
            1 => NpcType::Merchant,
            2 => NpcType::Ambient,
            3 => NpcType::MythologicalFigure,
            4 => NpcType::Enemy,
            5 => NpcType::Ally,
            _ => NpcType::Ambient,
        };

        self.base_mut().set_global_position(position);
    }

    /// Set patrol waypoints
    #[func]
    pub fn set_patrol_points(&mut self, points: Array<Vector3>) {
        self.patrol_points = points.iter_shared().collect();
        self.patrol_index = 0;
    }

    /// Start dialogue with this NPC
    #[func]
    pub fn start_dialogue(&mut self, initial_node: GString) {
        self.state = NpcState::Talking;
        self.current_dialogue_node = initial_node.clone();

        self.base_mut().emit_signal(
            "dialogue_started",
            &[self.npc_id.to_variant(), initial_node.to_variant()],
        );
    }

    /// Advance to next dialogue node
    #[func]
    pub fn set_dialogue_node(&mut self, node: GString) {
        self.current_dialogue_node = node.clone();

        self.base_mut().emit_signal(
            "dialogue_changed",
            &[self.npc_id.to_variant(), node.to_variant()],
        );
    }

    /// End dialogue
    #[func]
    pub fn end_dialogue(&mut self) {
        self.state = NpcState::Idle;
        self.current_dialogue_node = "".into();

        self.base_mut().emit_signal("dialogue_ended", &[self.npc_id.to_variant()]);
    }

    /// Start trading with this NPC (for merchants)
    #[func]
    pub fn start_trading(&mut self) {
        if self.npc_type == NpcType::Merchant {
            self.state = NpcState::Trading;
            self.base_mut().emit_signal("trading_started", &[self.npc_id.to_variant()]);
        }
    }

    /// End trading
    #[func]
    pub fn end_trading(&mut self) {
        self.state = NpcState::Idle;
        self.base_mut().emit_signal("trading_ended", &[self.npc_id.to_variant()]);
    }

    /// Called when player enters interaction range
    #[func]
    pub fn on_player_entered(&mut self) {
        self.player_nearby = true;
        self.base_mut().emit_signal("player_in_range", &[self.npc_id.to_variant()]);
    }

    /// Called when player exits interaction range
    #[func]
    pub fn on_player_exited(&mut self) {
        self.player_nearby = false;
        self.base_mut().emit_signal("player_out_of_range", &[self.npc_id.to_variant()]);
    }

    /// Get NPC type as integer
    #[func]
    pub fn get_npc_type(&self) -> i32 {
        match self.npc_type {
            NpcType::QuestGiver => 0,
            NpcType::Merchant => 1,
            NpcType::Ambient => 2,
            NpcType::MythologicalFigure => 3,
            NpcType::Enemy => 4,
            NpcType::Ally => 5,
        }
    }

    /// Get current state as integer
    #[func]
    pub fn get_state(&self) -> i32 {
        match self.state {
            NpcState::Idle => 0,
            NpcState::Walking => 1,
            NpcState::Talking => 2,
            NpcState::Trading => 3,
            NpcState::Combat => 4,
            NpcState::Fleeing => 5,
            NpcState::Dead => 6,
        }
    }

    /// Check if NPC can be interacted with
    #[func]
    pub fn can_interact(&self) -> bool {
        matches!(self.state, NpcState::Idle | NpcState::Walking)
    }

    // Signals
    #[signal]
    fn dialogue_started(npc_id: u64, initial_node: GString);

    #[signal]
    fn dialogue_changed(npc_id: u64, node: GString);

    #[signal]
    fn dialogue_ended(npc_id: u64);

    #[signal]
    fn trading_started(npc_id: u64);

    #[signal]
    fn trading_ended(npc_id: u64);

    #[signal]
    fn player_in_range(npc_id: u64);

    #[signal]
    fn player_out_of_range(npc_id: u64);
}
