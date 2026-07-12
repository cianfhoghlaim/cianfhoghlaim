"""Pytest configuration for the Cianfhoghlaim Educational MMO tests.

Adds `cianfhoghlaim/` to sys.path so tests can `import cianfhoghlaim.badges`.
"""
import sys
from pathlib import Path

# Add the cianfhoghlaim root to sys.path so `import cianfhoghlaim` works
CIANFHOGHLAIM_ROOT = Path(__file__).resolve().parents[2]
if str(CIANFHOGHLAIM_ROOT) not in sys.path:
    sys.path.insert(0, str(CIANFHOGHLAIM_ROOT))