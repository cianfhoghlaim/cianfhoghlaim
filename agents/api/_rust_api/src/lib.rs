//! Tuath Celtic MMO API Library
//!
//! This crate provides the HTTP API for the Tuath Celtic MMO game,
//! including x402 micropayment-protected premium routes.
//!
//! ## Features
//!
//! - **Free Routes**: Basic game data, health checks, zone/clan/language info
//! - **Premium Routes**: Payment-protected with x402 micropayments
//!   - Premium quest content ($0.05)
//!   - Celtic knowledge search ($0.02)
//!   - Extended AI agent conversations ($0.10)
//!   - Daily XP boost ($0.25)
//!   - Premium clan treasury features ($0.15)
//!
//! ## Supported Payment Networks
//!
//! - Base (Coinbase L2) - USDC
//! - Polygon - USDC
//! - Base Sepolia (testnet) - USDC
//! - Polygon Amoy (testnet) - USDC
//!
//! ## Usage
//!
//! ```bash
//! # Set required environment variables
//! export EVM_PAY_TO="0xYourAddress"
//! export FACILITATOR_URL="https://facilitator.x402.rs"
//!
//! # Run the API
//! cargo run --release
//! ```

pub mod config;
pub mod routes;

pub use config::Config;
