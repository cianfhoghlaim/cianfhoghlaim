"""Allow `python -m cianfhoghlaim` to invoke the consolidated CLI.

This file makes the `cianfhoghlaim` package executable as a module, which
uv's `[project.scripts]` entry-point `cianfhoghlaim = "cianfhoghlaim.cli:main"`
also relies on at install time.
"""
from cianfhoghlaim.cli import main


if __name__ == "__main__":
    raise SystemExit(main())