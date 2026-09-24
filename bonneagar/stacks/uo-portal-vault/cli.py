"""uo_portal_vault — the per-user credential vault CLI for the UoA portal.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The 1-time M365 unlock procedure that drives the Patchright browser
to log in to login.microsoftonline.com for regexam.nuigalway.ie +
canvas.universityofgalway.ie + captures the AppProxy cookies + writes
them encrypted to /stedding/user_profiles/<user_id>/{regexam,canvas}/.

Subcommands:
  - unlock    : 1-time M365 login per user (manual: true)
  - adduser   : provision the 4 per-user Infisical secrets
  - whoami    : print the active user (from UO_PORTAL_USER env)

Phase 1: stub CLI that documents the procedure.
Phase 2: Patchright-driven unlock (the actual implementation).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


USER_PROFILE_DIR = Path(
    os.environ.get(
        "UO_PORTAL_VAULT_DIR",
        "/stedding/user_profiles",
    )
)


def cmd_unlock(args: argparse.Namespace) -> int:
    """The 1-time M365 login per user.

    Phase 1 stub: documents the procedure.
    Phase 2: drive Patchright to:
      1. Read the username + password from Infisical (via Locket)
      2. Open Chromium via Patchright stealth mode
      3. Navigate to https://regexam.nuigalway.ie/regexam/paper_index_search_main_menu.asp
      4. Wait for the M365 OAuth redirect to login.microsoftonline.com
      5. Fill the email field (uid: 1_7)
      6. Click Next
      7. Fill the password field (uid varies)
      8. Click Sign in
      9. Handle the MFA prompt (operator approves on phone)
      10. Wait for the AppProxy redirect back to regexam.nuigalway.ie
      11. Capture the AppProxy state cookie + the regexam session JWT
      12. Encrypt + write to /stedding/user_profiles/<user_id>/regexam/cookies.json
      13. Repeat for canvas.universityofgalway.ie (optional PAT path)
    """
    user_id = args.user
    service = args.service
    profile_dir = USER_PROFILE_DIR / user_id / service
    profile_dir.mkdir(parents=True, exist_ok=True)

    cookies_path = profile_dir / "cookies.json"
    placeholder = {
        "user_id": user_id,
        "service": service,
        "scraped_at": "2026-09-23T00:00:00Z",
        "cookies": [],
        "notes": "Phase 1 stub — Phase 2 Patchright will populate this file",
    }
    cookies_path.write_text(json.dumps(placeholder, indent=2))
    logger.info("unlock.placeholder_written", path=str(cookies_path))
    print(f"Wrote placeholder cookies to {cookies_path}")
    print("Phase 2: implement Patchright unlock procedure")
    return 0


def cmd_adduser(args: argparse.Namespace) -> int:
    """Provision the 4 per-user Infisical secrets."""
    user_id = args.user
    print(f"Phase 2: provision the 4 Infisical secrets for user {user_id}")
    print(f"  infisical://dev-baile/cianfhoghlaim/regexam-nuig/{user_id}/username")
    print(f"  infisical://dev-baile/cianfhoghlaim/regexam-nuig/{user_id}/password")
    print(f"  infisical://dev-baile/cianfhoghlaim/canvas-nuig/{user_id}/username")
    print(f"  infisical://dev-baile/cianfhoghlaim/canvas-nuig/{user_id}/password")
    print(f"  infisical://dev-baile/cianfhoghlaim/canvas-nuig/{user_id}/pat")
    return 0


def cmd_whoami(args: argparse.Namespace) -> int:
    user_id = os.environ.get("UO_PORTAL_USER", "default")
    print(user_id)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uo-portal-vault",
        description="The per-user credential vault CLI for the UoA portal pipeline",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_unlock = subparsers.add_parser("unlock", help="1-time M365 login per user")
    p_unlock.add_argument("--user", required=True, help="the user_id (e.g. a.oconnor1)")
    p_unlock.add_argument("--service", choices=["regexam", "canvas", "both"], default="both")
    p_unlock.set_defaults(func=cmd_unlock)

    p_adduser = subparsers.add_parser("adduser", help="provision per-user Infisical secrets")
    p_adduser.add_argument("--user", required=True)
    p_adduser.set_defaults(func=cmd_adduser)

    p_whoami = subparsers.add_parser("whoami", help="print the active user")
    p_whoami.set_defaults(func=cmd_whoami)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
