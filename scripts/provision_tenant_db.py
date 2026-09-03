#!/usr/bin/env python3
"""
Tenant Database Provisioning Script
====================================

Creates and initializes isolated DuckDB and LanceDB databases for each tenant.
Reads tenant configuration from config/tenants/*.yaml files.

Usage:
    python scripts/provision_tenant_db.py [--tenant TENANT_ID] [--force]

Options:
    --tenant    Provision only a specific tenant (default: all tenants)
    --force     Drop and recreate existing databases
"""

import argparse
import shutil
from pathlib import Path
from typing import Optional

import duckdb
import yaml


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def load_tenant_config(tenant_id: str) -> dict:
    """Load tenant configuration from YAML file."""
    config_path = PROJECT_ROOT / "config" / "tenants" / f"{tenant_id}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Tenant config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def list_tenants() -> list[str]:
    """List all available tenant IDs from config directory."""
    config_dir = PROJECT_ROOT / "config" / "tenants"
    if not config_dir.exists():
        return []

    return [p.stem for p in config_dir.glob("*.yaml")]


def provision_duckdb(tenant_id: str, config: dict, force: bool = False) -> Path:
    """
    Create and initialize DuckDB database for a tenant.

    Args:
        tenant_id: Tenant identifier
        config: Tenant configuration dict
        force: Whether to drop existing database

    Returns:
        Path to the created database
    """
    # Get database path from config
    storage_config = config.get("storage", {})
    db_path_str = storage_config.get(
        "duckdbPath", f"./storage/data/tenants/{tenant_id}/main.duckdb"
    )

    # Resolve relative paths from project root
    if db_path_str.startswith("./"):
        db_path = PROJECT_ROOT / db_path_str[2:]
    else:
        db_path = Path(db_path_str)

    # Create parent directory
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle existing database
    if db_path.exists():
        if force:
            print(f"  Removing existing database: {db_path}")
            db_path.unlink()
        else:
            print(f"  Database already exists: {db_path}")
            return db_path

    print(f"  Creating DuckDB database: {db_path}")

    # Create database and initialize schema
    conn = duckdb.connect(str(db_path))

    tenant_type = config.get("tenant", {}).get("type", "education")

    # Create common tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            title VARCHAR,
            summary TEXT,
            contact_info JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id VARCHAR PRIMARY KEY,
            profile_id VARCHAR NOT NULL REFERENCES profiles(id),
            name VARCHAR NOT NULL,
            category VARCHAR,
            proficiency INTEGER,
            years_experience INTEGER,
            keywords JSON
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id VARCHAR PRIMARY KEY,
            profile_id VARCHAR NOT NULL REFERENCES profiles(id),
            name VARCHAR NOT NULL,
            description TEXT,
            status VARCHAR,
            url VARCHAR,
            technologies JSON,
            highlights JSON,
            start_date DATE,
            end_date DATE,
            role VARCHAR,
            category VARCHAR
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS experience (
            id VARCHAR PRIMARY KEY,
            profile_id VARCHAR NOT NULL REFERENCES profiles(id),
            company VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            location VARCHAR,
            start_date DATE,
            end_date DATE,
            is_current BOOLEAN,
            description TEXT,
            highlights JSON,
            technologies JSON
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS social_links (
            id VARCHAR PRIMARY KEY,
            profile_id VARCHAR NOT NULL REFERENCES profiles(id),
            platform VARCHAR NOT NULL,
            url VARCHAR NOT NULL,
            username VARCHAR,
            followers INTEGER
        )
    """)

    # Create tenant-specific tables based on type
    if tenant_type == "portfolio":
        # Music-related tables for aleyum
        conn.execute("""
            CREATE TABLE IF NOT EXISTS music_tracks (
                id VARCHAR PRIMARY KEY,
                profile_id VARCHAR NOT NULL REFERENCES profiles(id),
                title VARCHAR NOT NULL,
                artist VARCHAR NOT NULL,
                album VARCHAR,
                release_date DATE,
                duration_seconds INTEGER,
                genres JSON,
                streaming_urls JSON,
                play_count INTEGER,
                is_original BOOLEAN
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS music_releases (
                id VARCHAR PRIMARY KEY,
                profile_id VARCHAR NOT NULL REFERENCES profiles(id),
                title VARCHAR NOT NULL,
                artist VARCHAR NOT NULL,
                release_date DATE,
                artwork_url VARCHAR,
                label VARCHAR,
                release_type VARCHAR
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS game_projects (
                id VARCHAR PRIMARY KEY,
                profile_id VARCHAR NOT NULL REFERENCES profiles(id),
                title VARCHAR NOT NULL,
                description TEXT,
                engine VARCHAR,
                platforms JSON,
                technologies JSON,
                role VARCHAR,
                status VARCHAR,
                demo_url VARCHAR,
                repo_url VARCHAR,
                media_urls JSON,
                release_date DATE
            )
        """)

    elif tenant_type == "education":
        # Education-related tables for cianfhoghlaim
        conn.execute("""
            CREATE TABLE IF NOT EXISTS curriculum_items (
                id VARCHAR PRIMARY KEY,
                subject VARCHAR NOT NULL,
                topic VARCHAR,
                level VARCHAR,
                region VARCHAR,
                language VARCHAR,
                content TEXT,
                learning_outcomes JSON,
                keywords JSON,
                source_url VARCHAR,
                source_date DATE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id VARCHAR PRIMARY KEY,
                source_text TEXT NOT NULL,
                source_lang VARCHAR NOT NULL,
                target_text TEXT NOT NULL,
                target_lang VARCHAR NOT NULL,
                context VARCHAR,
                domain VARCHAR,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id VARCHAR PRIMARY KEY,
                word VARCHAR NOT NULL,
                language VARCHAR NOT NULL,
                part_of_speech VARCHAR,
                definition TEXT,
                examples JSON,
                synonyms JSON,
                related_words JSON,
                difficulty_level INTEGER
            )
        """)

    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_profiles_tenant ON profiles(tenant_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_profile ON skills(profile_id)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_projects_profile ON projects(profile_id)"
    )

    conn.close()

    print(f"  DuckDB initialized with {tenant_type} schema")
    return db_path


def provision_lancedb(tenant_id: str, config: dict, force: bool = False) -> Path:
    """
    Create LanceDB directory for a tenant.

    Args:
        tenant_id: Tenant identifier
        config: Tenant configuration dict
        force: Whether to remove existing directory

    Returns:
        Path to the LanceDB directory
    """
    # Get LanceDB path from config
    storage_config = config.get("storage", {})
    lance_path_str = storage_config.get(
        "lancedbPath", f"./storage/data/tenants/{tenant_id}/lancedb"
    )

    # Resolve relative paths
    if lance_path_str.startswith("./"):
        lance_path = PROJECT_ROOT / lance_path_str[2:]
    else:
        lance_path = Path(lance_path_str)

    # Handle existing directory
    if lance_path.exists():
        if force:
            print(f"  Removing existing LanceDB: {lance_path}")
            shutil.rmtree(lance_path)
        else:
            print(f"  LanceDB directory already exists: {lance_path}")
            return lance_path

    # Create directory
    lance_path.mkdir(parents=True, exist_ok=True)
    print(f"  Created LanceDB directory: {lance_path}")

    # Create a marker file to indicate this is a LanceDB directory
    marker_path = lance_path / ".lancedb"
    marker_path.touch()

    return lance_path


def provision_assets_dir(tenant_id: str, config: dict) -> Path:
    """Create assets directory for a tenant."""
    storage_config = config.get("storage", {})
    assets_path_str = storage_config.get(
        "assetsPath", f"./storage/assets/{tenant_id}"
    )

    if assets_path_str.startswith("./"):
        assets_path = PROJECT_ROOT / assets_path_str[2:]
    else:
        assets_path = Path(assets_path_str)

    if not assets_path.exists():
        assets_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created assets directory: {assets_path}")
    else:
        print(f"  Assets directory exists: {assets_path}")

    return assets_path


def provision_tenant(tenant_id: str, force: bool = False) -> None:
    """
    Provision all databases and directories for a tenant.

    Args:
        tenant_id: Tenant identifier
        force: Whether to recreate existing resources
    """
    print(f"\nProvisioning tenant: {tenant_id}")
    print("-" * 40)

    # Load configuration
    config = load_tenant_config(tenant_id)
    tenant_type = config.get("tenant", {}).get("type", "unknown")
    print(f"  Tenant type: {tenant_type}")

    # Provision DuckDB
    provision_duckdb(tenant_id, config, force)

    # Provision LanceDB
    provision_lancedb(tenant_id, config, force)

    # Provision assets directory
    provision_assets_dir(tenant_id, config)

    print(f"  Tenant {tenant_id} provisioned successfully!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Provision tenant databases and directories"
    )
    parser.add_argument(
        "--tenant",
        type=str,
        help="Specific tenant to provision (default: all tenants)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Drop and recreate existing databases",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tenants and exit",
    )

    args = parser.parse_args()

    # List tenants mode
    if args.list:
        tenants = list_tenants()
        print("Available tenants:")
        for t in tenants:
            print(f"  - {t}")
        return

    # Provision specific tenant or all tenants
    if args.tenant:
        provision_tenant(args.tenant, args.force)
    else:
        tenants = list_tenants()
        if not tenants:
            print("No tenant configurations found in config/tenants/")
            return

        print(f"Provisioning {len(tenants)} tenant(s)...")
        for tenant_id in tenants:
            provision_tenant(tenant_id, args.force)

    print("\nProvisioning complete!")


if __name__ == "__main__":
    main()
