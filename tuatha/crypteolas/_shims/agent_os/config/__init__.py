"""Shim for `sruth.shared.agent_os.config` — see tuatha/crypteolas/STATUS.md."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentOSConfig:
    """Stub AgentOS configuration."""

    service_name: str = "crypteolas"
    service_port: int = 7771
    auth_token_header: str = "X-Auth-Token"
    enable_a2a: bool = True
    enable_x402: bool = True
    extra: dict = field(default_factory=dict)


def init_config(
    service_name: str = "crypteolas",
    service_port: int = 7771,
    **kwargs,
) -> AgentOSConfig:
    """Build an AgentOS config from kwargs + sensible defaults."""
    return AgentOSConfig(
        service_name=service_name,
        service_port=service_port,
        **kwargs,
    )


__all__ = ["AgentOSConfig", "init_config"]
