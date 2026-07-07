"""Site memory for storing interaction patterns and knowledge."""

from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class NavigationPattern(BaseModel):
    """Pattern for navigating a site."""

    name: str
    description: str
    steps: list[str]
    success_rate: float = 1.0
    last_used: datetime = Field(default_factory=datetime.utcnow)


class FormPattern(BaseModel):
    """Pattern for filling forms on a site."""

    form_name: str
    fields: dict[str, str]  # label -> selector
    submit_selector: str | None = None
    success_rate: float = 1.0
    last_used: datetime = Field(default_factory=datetime.utcnow)


class SiteKnowledge(BaseModel):
    """Accumulated knowledge about a website."""

    domain: str
    last_visited: datetime = Field(default_factory=datetime.utcnow)

    # Navigation patterns
    navigation_patterns: list[NavigationPattern] = Field(default_factory=list)

    # Form patterns
    form_patterns: list[FormPattern] = Field(default_factory=list)

    # Access information
    requires_auth: bool = False
    has_captcha: bool = False
    requires_javascript: bool = True
    optimal_backend: str | None = None

    # Performance metrics
    avg_load_time_ms: float | None = None
    success_rate: float = 1.0


class SiteMemory:
    """Persistent memory for site interaction patterns.

    Stores learned patterns for:
    - Navigation paths
    - Form structures
    - Optimal backend selection
    - Access requirements
    """

    def __init__(self):
        self._sites: dict[str, SiteKnowledge] = {}

    def get_site(self, domain: str) -> SiteKnowledge | None:
        """Get knowledge about a specific site."""
        return self._sites.get(domain)

    def update_site(self, domain: str, **kwargs) -> SiteKnowledge:
        """Update site knowledge."""
        if domain not in self._sites:
            self._sites[domain] = SiteKnowledge(domain=domain)

        site = self._sites[domain]
        for key, value in kwargs.items():
            if hasattr(site, key):
                setattr(site, key, value)

        site.last_visited = datetime.utcnow()
        return site

    def add_navigation_pattern(
        self,
        domain: str,
        name: str,
        description: str,
        steps: list[str],
    ) -> None:
        """Add a navigation pattern for a site."""
        site = self.update_site(domain)

        # Check if pattern exists
        for pattern in site.navigation_patterns:
            if pattern.name == name:
                pattern.steps = steps
                pattern.last_used = datetime.utcnow()
                return

        site.navigation_patterns.append(
            NavigationPattern(
                name=name,
                description=description,
                steps=steps,
            )
        )

    def add_form_pattern(
        self,
        domain: str,
        form_name: str,
        fields: dict[str, str],
        submit_selector: str | None = None,
    ) -> None:
        """Add a form pattern for a site."""
        site = self.update_site(domain)

        # Check if pattern exists
        for pattern in site.form_patterns:
            if pattern.form_name == form_name:
                pattern.fields = fields
                pattern.submit_selector = submit_selector
                pattern.last_used = datetime.utcnow()
                return

        site.form_patterns.append(
            FormPattern(
                form_name=form_name,
                fields=fields,
                submit_selector=submit_selector,
            )
        )

    def record_access_issue(
        self,
        domain: str,
        issue_type: str,
    ) -> None:
        """Record an access issue for a site."""
        site = self.update_site(domain)

        if issue_type == "captcha":
            site.has_captcha = True
        elif issue_type == "auth":
            site.requires_auth = True

        # Reduce success rate
        site.success_rate = max(0.0, site.success_rate - 0.1)

    def record_success(
        self,
        domain: str,
        backend: str,
        load_time_ms: float,
    ) -> None:
        """Record a successful interaction."""
        site = self.update_site(domain)

        # Update optimal backend
        if site.optimal_backend is None or load_time_ms < (site.avg_load_time_ms or float("inf")):
            site.optimal_backend = backend

        # Update average load time
        if site.avg_load_time_ms is None:
            site.avg_load_time_ms = load_time_ms
        else:
            site.avg_load_time_ms = (site.avg_load_time_ms + load_time_ms) / 2

        # Improve success rate
        site.success_rate = min(1.0, site.success_rate + 0.05)

    def get_optimal_backend(self, domain: str) -> str | None:
        """Get the optimal backend for a domain."""
        site = self._sites.get(domain)
        return site.optimal_backend if site else None

    def get_navigation_pattern(
        self,
        domain: str,
        pattern_name: str,
    ) -> NavigationPattern | None:
        """Get a specific navigation pattern."""
        site = self._sites.get(domain)
        if not site:
            return None

        for pattern in site.navigation_patterns:
            if pattern.name == pattern_name:
                return pattern

        return None

    def get_form_pattern(
        self,
        domain: str,
        form_name: str,
    ) -> FormPattern | None:
        """Get a specific form pattern."""
        site = self._sites.get(domain)
        if not site:
            return None

        for pattern in site.form_patterns:
            if pattern.form_name == form_name:
                return pattern

        return None

    def export(self) -> dict[str, Any]:
        """Export all site knowledge."""
        return {
            domain: site.model_dump()
            for domain, site in self._sites.items()
        }

    def import_data(self, data: dict[str, Any]) -> None:
        """Import site knowledge from export."""
        for domain, site_data in data.items():
            self._sites[domain] = SiteKnowledge(**site_data)


# Global instance
_memory: SiteMemory | None = None


def get_site_memory() -> SiteMemory:
    """Get the global site memory instance."""
    global _memory
    if _memory is None:
        _memory = SiteMemory()
    return _memory
