"""
spaces/anam_tuatha/soulbound_local.py
Anam theme: Soulbound token badge (local Anvil sidecar mock).

Mirrors the on-chain CuchulainnNFT.sol logic from
tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol:1-231
(ERC-5192 soulbound, 3 stages, 5 elements) but operates entirely
client-side using the deterministic SVG from spaces/_common.

For the hackathon demo, NO actual on-chain transaction happens.
The Anvil sidecar is local-only (see infrastructure/stacks/
oideachais/sidecar.yaml in the archived stack), and the wallet is a
fake address "0xHACKATHON..." that the player can copy as a souvenir.

Stages (3):
  - Setanta     (juvenile, single ring + Anam center)
  - Cuchulainn  (warrior, 3 rings + spear)
  - Riastrad    (warp spasm, full triskelion + crimson core)

5 elements: Talamh (Earth), Uisce (Water), Tine (Fire), Aer (Air),
Anam (Spirit). Each stage is granted after completing a number of
"feats" in the Space (1 feat per element = 5 total).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


# Stage progression: feat count -> stage
_STAGE_THRESHOLDS: list[tuple[int, str]] = [
    (0, "setanta"),
    (2, "cuchulainn"),
    (5, "riastrad"),
]


@dataclass
class SoulboundState:
    wallet_short: str
    feats_completed: int
    current_stage: str
    elements_active: list[str]  # which of 5 elements the player has lit
    tampered: bool = False


def _derive_wallet_short(space_session: str) -> str:
    """Derive a deterministic 4-char wallet suffix from the session id.

    In production this would be the player's connected SIWE wallet.
    For the demo, the player gets a memorable deterministic address.
    """
    h = hashlib.sha256(space_session.encode()).hexdigest()
    return f"0xHACKATHON...{h[:4].upper()}"


def _next_stage(feats: int) -> str:
    for threshold, stage in _STAGE_THRESHOLDS:
        if feats >= threshold:
            current = stage
    return current


def _all_elements() -> list[str]:
    return ["talamh", "uisce", "tine", "aer", "anam"]


def create_initial_state(space_session: str) -> SoulboundState:
    """Create the initial soulbound state for a new session."""
    return SoulboundState(
        wallet_short=_derive_wallet_short(space_session),
        feats_completed=0,
        current_stage="setanta",
        elements_active=[],
        tampered=False,
    )


def record_feat(state: SoulboundState, element: str) -> SoulboundState:
    """Record that the player completed a feat in the given element.

    Stages the player up if they cross a threshold.
    """
    if element not in _all_elements():
        raise ValueError(f"Unknown element: {element}")
    state.feats_completed += 1
    if element not in state.elements_active:
        state.elements_active.append(element)
    new_stage = _next_stage(state.feats_completed)
    state.current_stage = new_stage
    return state


def render_badge_html(state: SoulboundState) -> str:
    """Render the soulbound badge as HTML for the Space UI.

    The SVG itself is computed by spaces._common.soulbound_svg.
    """
    from spaces._common.soulbound_svg import render_soulbound_html
    svg_html = render_soulbound_html(state.wallet_short, state.current_stage)

    elements_html = "".join(
        f'<span class="elem-chip elem-{e}" style="display:inline-block; '
        f'padding:0.2em 0.5em; margin:0.2em; border-radius:3px; '
        f'background:#1a1d2e; border:1px solid '
        f'{"#cc9966" if e in state.elements_active else "#2a3a3a"}; '
        f'color:{"#cc9966" if e in state.elements_active else "#bcb8b0"};">'
        f'{e}</span>'
        for e in _all_elements()
    )

    return (
        f'<div class="soulbound-panel" '
        f'style="background:#1d1d2f; padding:1.5em; '
        f'border:2px solid #cc9966; border-radius:4px;">'
        f'<h3 style="color:#cc9966; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">Anam - Soulbound Token</h3>'
        f'<div style="display:flex; align-items:center; gap:1em;">'
        f'<div style="flex:0 0 220px;">{svg_html}</div>'
        f'<div style="flex:1; color:#d8d4cc; '
        f'font-family:Inter,sans-serif;">'
        f'<div style="margin-bottom:0.4em;">'
        f'<strong style="color:#cc9966;">Wallet:</strong> '
        f'<code style="color:#28955e;">{state.wallet_short}</code></div>'
        f'<div style="margin-bottom:0.4em;">'
        f'<strong style="color:#cc9966;">Stage:</strong> '
        f'<span style="color:#d8d4cc;">{state.current_stage}</span></div>'
        f'<div style="margin-bottom:0.4em;">'
        f'<strong style="color:#cc9966;">Feats:</strong> '
        f'<span style="color:#d8d4cc;">{state.feats_completed} / 5</span></div>'
        f'<div style="margin-bottom:0.4em;">'
        f'<strong style="color:#cc9966;">Elements active:</strong></div>'
        f'<div>{elements_html}</div>'
        f'</div>'
        f'</div>'
        f'<div style="margin-top:1em; font-size:0.8em; color:#bcb8b0; '
        f'font-style:italic;">'
        f'Local Anvil sidecar (no on-chain tx, no gas). '
        f'Mirrors CuchulainnNFT.sol 3-stage progression.'
        f'</div>'
        f'</div>'
    )
