"""
Tuath API Routes.

Provides endpoints for authentication, payments, agents, and game content.
"""

from . import auth, copilotkit, curriculum, game_state, geospatial, mythology, payments

__all__ = [
    "auth",
    "copilotkit",
    "curriculum",
    "game_state",
    "geospatial",
    "mythology",
    "payments",
]
