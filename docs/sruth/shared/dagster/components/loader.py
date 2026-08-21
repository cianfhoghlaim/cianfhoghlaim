"""YAML Component Loader for Dagster.

Provides utilities for loading Dagster components from YAML files.

Usage:
    from sruth.shared.dagster.components.loader import load_components_from_yaml

    defs = load_components_from_yaml("path/to/component.yaml")

    # Or load multiple
    defs = load_components_from_yaml([
        "yaml/iceberg_io.yaml",
        "yaml/curriculum_asset.yaml",
    ])
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dagster as dg
import yaml


@dataclass
class ComponentSpec:
    """Specification for a component loaded from YAML."""

    component: str  # Python path to component class
    id: str | None = None
    attributes: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComponentSpec:
        """Create from YAML dict."""
        return cls(
            component=data.get("component", ""),
            id=data.get("id"),
            attributes=data.get("attributes", {}),
        )


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""

    name: str
    values: dict[str, Any]

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> EnvironmentConfig:
        """Create from YAML dict."""
        return cls(
            name=name,
            values=data,
        )


def _substitute_env_vars(value: Any) -> Any:
    """Recursively substitute environment variables in values."""
    if isinstance(value, str):
        # Handle ${VAR:-default} pattern
        if "${" in value and "}" in value:
            try:
                var_part = value.split("${", 1)[1].split("}", 1)[0]
                if ":-" in var_part:
                    var_name, default = var_part.split(":-", 1)
                    return os.getenv(var_name, default)
                else:
                    return os.getenv(var_part, value)
            except Exception:
                return value
        return value
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(v) for v in value]
    return value


def _load_component_class(component_path: str) -> type[dg.Component]:
    """Import and return component class from path."""
    module_path, class_name = component_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def load_component_from_yaml(
    file_path: str | Path,
    environment: str | None = None,
) -> dg.Definitions:
    """
    Load a single Dagster component from YAML file.

    Args:
        file_path: Path to YAML file
        environment: Environment name to use (for overrides)

    Returns:
        Dagster Definitions from the component
    """
    file_path = Path(file_path)

    with open(file_path) as f:
        data = yaml.safe_load(f)

    # Substitute environment variables
    data = _substitute_env_vars(data)

    # Apply environment overrides if specified
    if environment and "environments" in data:
        env_config = data["environments"].get(environment, {})
        # Merge environment config into attributes
        if "attributes" in data and env_config:
            data["attributes"] = {**data["attributes"], **env_config}

    spec = ComponentSpec.from_dict(data)
    component_class = _load_component_class(spec.component)

    # Create component instance with attributes
    component = component_class(**(spec.attributes or {}))

    # Build definitions
    return component.build_defs(dg.ComponentLoadContext.for_module(module_name="__main__"))


def load_components_from_yaml(
    files: str | Path | list[str | Path],
    environment: str | None = None,
) -> dg.Definitions:
    """
    Load multiple Dagster components from YAML files.

    Args:
        files: Single file path or list of paths
        environment: Environment name for overrides

    Returns:
        Combined Dagster Definitions from all components
    """
    if isinstance(files, (str, Path)):
        files = [files]

    all_defs = []

    for file_path in files:
        try:
            defs = load_component_from_yaml(file_path, environment=environment)
            all_defs.append(defs)
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")

    # Merge all definitions
    return dg.Definitions.merge(*all_defs)


def load_components_from_directory(
    directory: str | Path,
    pattern: str = "*.yaml",
    environment: str | None = None,
) -> dg.Definitions:
    """
    Load all YAML components from a directory.

    Args:
        directory: Directory containing YAML files
        pattern: Glob pattern for files (default: *.yaml)
        environment: Environment name for overrides

    Returns:
        Combined Dagster Definitions from all files
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))

    return load_components_from_yaml(files, environment=environment)


def get_current_environment() -> str:
    """Get current environment from variable or default."""
    return os.getenv("SRUTH_ENV", os.getenv("ENV", "local"))


# Convenience functions


def load_dev_definitions(directory: str | Path) -> dg.Definitions:
    """Load components for development environment."""
    return load_components_from_directory(directory, environment="local")


def load_staging_definitions(directory: str | Path) -> dg.Definitions:
    """Load components for staging environment."""
    return load_components_from_directory(directory, environment="staging")


def load_prod_definitions(directory: str | Path) -> dg.Definitions:
    """Load components for production environment."""
    return load_components_from_directory(directory, environment="production")


def load_auto_definitions(directory: str | Path) -> dg.Definitions:
    """Load components with auto-detected environment."""
    env = get_current_environment()
    return load_components_from_directory(directory, environment=env)
