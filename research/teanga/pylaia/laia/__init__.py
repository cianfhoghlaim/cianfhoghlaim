import subprocess
import sys
from importlib.metadata import requires, version
from pathlib import Path
from shutil import which
from typing import List

from packaging.requirements import Requirement

import laia.callbacks
import laia.data
import laia.decoders
import laia.engine
import laia.loggers
import laia.losses
import laia.nn
import laia.utils

__all__ = ["__version__", "__root__", "get_installed_versions"]
__lib__ = Path(__file__).parent
__root__ = __lib__.parent
__version__ = version("pylaia")

try:
    branch = subprocess.check_output(
        [which("git"), "-C", str(__root__), "branch", "--show-current"],
        stderr=subprocess.DEVNULL,
    )
    branch = branch.decode().strip()
    node = subprocess.check_output(
        [which("git"), "-C", str(__root__), "describe", "--always", "--dirty"],
        stderr=subprocess.DEVNULL,
    )
    node = node.decode().strip()
    __version__ += f"-{branch}-{node}"
except subprocess.CalledProcessError:
    pass


def get_installed_versions() -> List[str]:
    # Get all dependencies
    requirements: set[str] = {
        req.name
        for req in filter(
            # Only keep direct dependencies
            lambda x: x.marker is None,
            # Parse lines
            map(Requirement, requires("pylaia")),
        )
    }
    freeze = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze", "--exclude-editable"]
    )
    freeze = freeze.decode().strip().split("\n")
    versions = list(
        # Only keep PyLaia dependencies
        filter(lambda package: Requirement(package).name in requirements, freeze)
    )
    versions.append(f"laia=={__version__}")
    return versions
