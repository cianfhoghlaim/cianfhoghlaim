"""
Tuath API - Celtic Educational MMO Backend.

FastAPI backend with:
- SIWE (Sign-In With Ethereum) authentication
- x402 micropayment integration
- AG-UI/CopilotKit agent streaming
- Celtic curriculum and mythology APIs
- Game state management
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    auth,
    copilotkit,
    curriculum,
    game_state,
    geospatial,
    mythology,
    payments,
    search,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    print("🏰 Tuath API starting...")
    print("🌿 Celtic Educational MMO Backend")
    yield
    # Shutdown
    print("🌙 Tuath API shutting down...")


app = FastAPI(
    title="Tuath API",
    description="Celtic Educational MMO - Language Learning Through Mythology",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Payment-Required", "X-Payment-Amount", "X-Payment-Address"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(copilotkit.router, prefix="/copilotkit", tags=["Agent"])
app.include_router(curriculum.router, prefix="/curriculum", tags=["Curriculum"])
app.include_router(mythology.router, prefix="/mythology", tags=["Mythology"])
app.include_router(geospatial.router, prefix="/geospatial", tags=["Geospatial"])
app.include_router(game_state.router, prefix="/game", tags=["Game State"])
app.include_router(search.router, prefix="/search", tags=["Hybrid Search"])


@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Fáilte go Tuath! Welcome to Tuath!",
        "description": "Celtic Educational MMO API",
        "languages": ["Irish (Gaeilge)", "Scottish Gaelic (Gàidhlig)", "Welsh (Cymraeg)"],
        "endpoints": {
            "docs": "/docs",
            "auth": "/auth",
            "payments": "/payments",
            "agent": "/copilotkit",
            "curriculum": "/curriculum",
            "mythology": "/mythology",
            "geospatial": "/geospatial",
            "game": "/game",
            "search": "/search",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "tuath-api",
        "celtic_greeting": "Dia duit!",
    }


# Payment pricing configuration
PAYMENT_CONFIG = {
    "chat_message": {
        "price_usd": 0.01,
        "free_daily_limit": 5,
    },
    "knowledge_search": {
        "price_usd": 0.02,
        "free_daily_limit": 3,
    },
    "premium_quest": {
        "price_usd": 0.05,
        "free_daily_limit": 0,
    },
    "analytics": {
        "price_usd": 0.05,
        "free_daily_limit": 0,
    },
}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tuath.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
