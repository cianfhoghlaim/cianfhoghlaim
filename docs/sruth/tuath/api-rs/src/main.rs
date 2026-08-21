//! Tuath Celtic MMO API Server
//!
//! Rust API with x402 micropayment protection for premium game features:
//! - Premium quest access
//! - Celtic mythology knowledge search
//! - Extended AI agent conversations

use axum::Router;
use dotenvy::dotenv;
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod config;
mod routes;

use config::Config;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Load environment variables
    dotenv().ok();

    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "tuath_api=debug,tower_http=debug,x402=debug".into()),
        )
        .init();

    // Load configuration
    let config = Config::from_env()?;

    tracing::info!(
        "Starting Tuath API on {}:{}",
        config.host,
        config.port
    );
    tracing::info!("Facilitator URL: {}", config.facilitator_url);
    tracing::info!("EVM Pay-To Address: {}", config.evm_pay_to);

    // Build the application router
    let app = build_router(&config)?;

    // Start the server
    let addr: SocketAddr = format!("{}:{}", config.host, config.port).parse()?;
    tracing::info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

fn build_router(config: &Config) -> anyhow::Result<Router> {
    // CORS layer for cross-origin requests
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Build the router with all routes
    let app = Router::new()
        // Free routes (no payment required)
        .merge(routes::free::router())
        // Payment-protected routes
        .merge(routes::premium::router(config)?)
        // Middleware layers
        .layer(TraceLayer::new_for_http())
        .layer(cors);

    Ok(app)
}
