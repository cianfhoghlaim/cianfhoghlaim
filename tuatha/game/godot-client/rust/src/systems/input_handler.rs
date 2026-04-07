//! Input Handler
//!
//! Centralized input management for the game.
//! Handles keybindings, gamepad support, and input contexts.

use godot::prelude::*;
use godot::classes::{Node, INode, Input};

/// Input context - determines which inputs are active
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum InputContext {
    /// Normal gameplay
    Gameplay,
    /// In UI/menu
    Menu,
    /// In dialogue with NPC
    Dialogue,
    /// In trading screen
    Trading,
    /// Map view
    Map,
    /// Inventory screen
    Inventory,
    /// Cutscene (input disabled)
    Cutscene,
}

/// Centralized input handler
#[derive(GodotClass)]
#[class(base=Node)]
pub struct InputHandler {
    base: Base<Node>,

    /// Current input context
    context: InputContext,

    /// Whether input is globally enabled
    #[var]
    enabled: bool,

    /// Gamepad deadzone
    #[var]
    deadzone: f32,
}

#[godot_api]
impl INode for InputHandler {
    fn init(base: Base<Node>) -> Self {
        Self {
            base,
            context: InputContext::Gameplay,
            enabled: true,
            deadzone: 0.2,
        }
    }

    fn ready(&mut self) {
        godot_print!("InputHandler ready");
        self.setup_default_actions();
    }

    fn process(&mut self, _delta: f64) {
        if !self.enabled {
            return;
        }

        // Handle context-specific input
        match self.context {
            InputContext::Gameplay => self.process_gameplay_input(),
            InputContext::Menu => self.process_menu_input(),
            InputContext::Dialogue => self.process_dialogue_input(),
            _ => {}
        }
    }
}

#[godot_api]
impl InputHandler {
    /// Setup default input actions if not already defined
    fn setup_default_actions(&self) {
        // Note: In production, these would be defined in Godot's Input Map
        // This just documents the expected actions
        godot_print!("Expected input actions:");
        godot_print!("  - move_forward/back/left/right: WASD or left stick");
        godot_print!("  - jump: Space or A button");
        godot_print!("  - sprint: Shift or LB");
        godot_print!("  - interact: E or X button");
        godot_print!("  - menu: Escape or Start");
        godot_print!("  - inventory: I or Y button");
        godot_print!("  - map: M or Back button");
    }

    /// Process gameplay input
    fn process_gameplay_input(&mut self) {
        let input = Input::singleton();

        // Check for menu toggle
        if input.is_action_just_pressed("menu") {
            self.set_context(InputContext::Menu);
            self.base_mut().emit_signal("menu_requested", &[]);
        }

        // Check for inventory toggle
        if input.is_action_just_pressed("inventory") {
            self.set_context(InputContext::Inventory);
            self.base_mut().emit_signal("inventory_requested", &[]);
        }

        // Check for map toggle
        if input.is_action_just_pressed("map") {
            self.set_context(InputContext::Map);
            self.base_mut().emit_signal("map_requested", &[]);
        }

        // Check for interact
        if input.is_action_just_pressed("interact") {
            self.base_mut().emit_signal("interact_requested", &[]);
        }
    }

    /// Process menu input
    fn process_menu_input(&mut self) {
        let input = Input::singleton();

        // Check for menu close
        if input.is_action_just_pressed("menu") || input.is_action_just_pressed("ui_cancel") {
            self.set_context(InputContext::Gameplay);
            self.base_mut().emit_signal("menu_closed", &[]);
        }
    }

    /// Process dialogue input
    fn process_dialogue_input(&mut self) {
        let input = Input::singleton();

        // Check for dialogue advance
        if input.is_action_just_pressed("interact") || input.is_action_just_pressed("ui_accept") {
            self.base_mut().emit_signal("dialogue_advance", &[]);
        }

        // Check for dialogue cancel
        if input.is_action_just_pressed("ui_cancel") {
            self.base_mut().emit_signal("dialogue_cancel", &[]);
        }

        // Check for dialogue option selection (1-4)
        for i in 1..=4 {
            let action = format!("dialogue_option_{}", i);
            if input.is_action_just_pressed(&action) {
                self.base_mut().emit_signal("dialogue_option_selected", &[(i as i32).to_variant()]);
            }
        }
    }

    /// Set the current input context
    #[func]
    pub fn set_context(&mut self, context_id: i32) {
        let new_context = match context_id {
            0 => InputContext::Gameplay,
            1 => InputContext::Menu,
            2 => InputContext::Dialogue,
            3 => InputContext::Trading,
            4 => InputContext::Map,
            5 => InputContext::Inventory,
            6 => InputContext::Cutscene,
            _ => InputContext::Gameplay,
        };

        self.context = new_context;
        self.update_mouse_mode();

        self.base_mut().emit_signal("context_changed", &[context_id.to_variant()]);
    }

    /// Get current context as integer
    #[func]
    pub fn get_context(&self) -> i32 {
        match self.context {
            InputContext::Gameplay => 0,
            InputContext::Menu => 1,
            InputContext::Dialogue => 2,
            InputContext::Trading => 3,
            InputContext::Map => 4,
            InputContext::Inventory => 5,
            InputContext::Cutscene => 6,
        }
    }

    /// Update mouse mode based on context
    fn update_mouse_mode(&self) {
        let input = Input::singleton();

        match self.context {
            InputContext::Gameplay => {
                input.set_mouse_mode(godot::classes::input::MouseMode::CAPTURED);
            }
            InputContext::Cutscene => {
                input.set_mouse_mode(godot::classes::input::MouseMode::HIDDEN);
            }
            _ => {
                input.set_mouse_mode(godot::classes::input::MouseMode::VISIBLE);
            }
        }
    }

    /// Get movement input as Vector2
    #[func]
    pub fn get_movement_input(&self) -> Vector2 {
        if self.context != InputContext::Gameplay {
            return Vector2::ZERO;
        }

        let input = Input::singleton();
        let mut movement = Vector2::ZERO;

        // Keyboard input
        if input.is_action_pressed("move_forward") {
            movement.y -= 1.0;
        }
        if input.is_action_pressed("move_back") {
            movement.y += 1.0;
        }
        if input.is_action_pressed("move_left") {
            movement.x -= 1.0;
        }
        if input.is_action_pressed("move_right") {
            movement.x += 1.0;
        }

        // Apply deadzone and normalize
        if movement.length() < self.deadzone {
            Vector2::ZERO
        } else {
            movement.normalized()
        }
    }

    /// Check if sprint is pressed
    #[func]
    pub fn is_sprinting(&self) -> bool {
        self.context == InputContext::Gameplay
            && Input::singleton().is_action_pressed("sprint")
    }

    /// Check if jump was just pressed
    #[func]
    pub fn is_jump_pressed(&self) -> bool {
        self.context == InputContext::Gameplay
            && Input::singleton().is_action_just_pressed("jump")
    }

    // Signals
    #[signal]
    fn context_changed(context: i32);

    #[signal]
    fn menu_requested();

    #[signal]
    fn menu_closed();

    #[signal]
    fn inventory_requested();

    #[signal]
    fn map_requested();

    #[signal]
    fn interact_requested();

    #[signal]
    fn dialogue_advance();

    #[signal]
    fn dialogue_cancel();

    #[signal]
    fn dialogue_option_selected(option: i32);
}
