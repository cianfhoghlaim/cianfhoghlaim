//! Configuration for Tuath API
//!
//! Loads configuration from environment variables with sensible defaults.

use std::env;

/// API Configuration
#[derive(Debug, Clone)]
pub struct Config {
    /// Server host (default: 0.0.0.0)
    pub host: String,
    /// Server port (default: 3000)
    pub port: u16,
    /// x402 Facilitator URL
    pub facilitator_url: String,
    /// Base URL for this API (for x402 resource URLs)
    pub base_url: String,
    /// EVM address for receiving payments (Base/Polygon USDC)
    pub evm_pay_to: String,
    /// Solana address for receiving payments
    pub solana_pay_to: Option<String>,
}

impl Config {
    /// Load configuration from environment variables
    pub fn from_env() -> anyhow::Result<Self> {
        Ok(Self {
            host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            port: env::var("PORT")
                .unwrap_or_else(|_| "3000".to_string())
                .parse()?,
            facilitator_url: env::var("FACILITATOR_URL")
                .unwrap_or_else(|_| "https://facilitator.x402.rs".to_string()),
            base_url: env::var("BASE_URL")
                .unwrap_or_else(|_| "http://localhost:3000".to_string()),
            evm_pay_to: env::var("EVM_PAY_TO")
                .map_err(|_| anyhow::anyhow!("EVM_PAY_TO environment variable is required"))?,
            solana_pay_to: env::var("SOLANA_PAY_TO").ok(),
        })
    }
}

/// Price configuration for premium routes (in USD)
pub mod prices {
    /// Premium quest access
    pub const PREMIUM_QUEST: f64 = 0.05;
    /// Celtic mythology knowledge search
    pub const KNOWLEDGE_SEARCH: f64 = 0.02;
    /// Extended AI agent conversation
    pub const AGENT_EXTENDED: f64 = 0.10;
    /// Daily XP boost
    pub const XP_BOOST_DAILY: f64 = 0.25;
    /// Premium clan treasury features
    pub const CLAN_TREASURY: f64 = 0.15;
}
