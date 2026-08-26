#!/usr/bin/env python3
"""Validate a Pangolin blueprint against live org state before applying it.

Pangolin's own errors are terse ("No valid sites found for private private
resource X in org Y") and, worse, it *silently ignores* users and machines that
do not resolve — producing a resource that exists, looks correct in every table,
and that nobody can reach. Both failure modes have bitten this deployment.

This catches them locally and, when a name is wrong, prints the valid ones.

Usage:
    preflight-blueprint.py <blueprint.yaml> <sites.json> <clients.json> <users.json>

Exit: 0 clean (warnings allowed), 1 errors found.
"""
import json
import sys

import yaml

VALID_MODES = {"host", "cidr", "http", "ssh"}


def rows(raw, *keys):
    """Pull a list out of a Pangolin API response, tolerating shape changes."""
    try:
        data = json.loads(raw).get("data") or {}
    except (ValueError, AttributeError):
        return []
    if isinstance(data, list):
        return data
    for key in keys:
        if isinstance(data.get(key), list):
            return data[key]
    return []


def main():
    if len(sys.argv) < 5:
        print(__doc__, file=sys.stderr)
        return 2

    blueprint_path, sites_raw, clients_raw, users_raw = sys.argv[1:5]

    doc = yaml.safe_load(open(blueprint_path)) or {}
    resources = doc.get("private-resources") or doc.get("client-resources") or {}
    if not resources:
        print("  WARN  blueprint declares no private-resources")
        return 0

    sites = rows(sites_raw, "sites")
    clients = rows(clients_raw, "clients")
    users = rows(users_raw, "users")

    site_ids = {s["niceId"] for s in sites if s.get("niceId")}
    online_ids = {s["niceId"] for s in sites if s.get("niceId") and s.get("online")}
    client_ids = {c["niceId"] for c in clients if c.get("niceId")}
    emails = {u["email"] for u in users if u.get("email")}

    def site_menu():
        lines = []
        for s in sorted(sites, key=lambda x: x.get("name", "")):
            state = "online" if s.get("online") else "OFFLINE"
            lines.append(f"          {s.get('niceId')}  ({s.get('name')}, {state})")
        return "\n".join(lines) or "          (none found)"

    errors, warnings = [], []

    for name, spec in resources.items():
        if not isinstance(spec, dict):
            errors.append(f"{name}: entry is not a mapping")
            continue

        mode = spec.get("mode")
        if mode not in VALID_MODES:
            errors.append(f"{name}: mode {mode!r} must be one of {sorted(VALID_MODES)}")

        # --- sites: the single most common failure -----------------------
        refs = list(spec.get("sites") or [])
        if spec.get("site"):
            refs.append(spec["site"])
        if not refs:
            errors.append(f"{name}: no sites declared (blueprint will fail with 'No valid sites found')")
        for ref in refs:
            if ref not in site_ids:
                errors.append(
                    f"{name}: site {ref!r} is not a site niceId.\n"
                    f"        Blueprints match sites.niceId, not the display name. Valid:\n"
                    f"{site_menu()}"
                )
            elif ref not in online_ids:
                warnings.append(f"{name}: site {ref!r} is OFFLINE — resource will not be reachable")

        # --- roles -------------------------------------------------------
        if "Admin" in (spec.get("roles") or []):
            errors.append(
                f"{name}: roles must not contain 'Admin' — admin access is implicit "
                f"and Pangolin rejects the blueprint outright"
            )

        # --- grants that resolve to nothing ------------------------------
        for user in spec.get("users") or []:
            if user not in emails:
                warnings.append(
                    f"{name}: user {user!r} does not resolve to an account — "
                    f"grant will be SILENTLY IGNORED"
                )
        for machine in spec.get("machines") or []:
            if machine not in client_ids:
                warnings.append(
                    f"{name}: machine {machine!r} is not a client niceId — "
                    f"grant will be SILENTLY IGNORED"
                )
        if not (spec.get("users") or spec.get("roles") or spec.get("machines")):
            warnings.append(f"{name}: no grants — only org admins will reach it")

        # --- destination -------------------------------------------------
        if not spec.get("destination") and mode != "ssh":
            errors.append(f"{name}: destination is required for mode {mode!r}")
        if mode == "http" and not spec.get("destination-port"):
            warnings.append(f"{name}: mode http without destination-port")
        if spec.get("destination") == "localhost":
            warnings.append(
                f"{name}: destination 'localhost' resolves to the NEWT CONTAINER, "
                f"not the host — use host.docker.internal or a container name"
            )

    for warning in warnings:
        print(f"  WARN  {warning}")
    for error in errors:
        print(f"  ERROR {error}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
