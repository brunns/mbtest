# encoding=utf-8
import logging
import os
import platform
from os.path import expanduser
from pathlib import Path

DEFAULT_MB_PATH = Path("node_modules") / ".bin"

logger = logging.getLogger(__name__)


def find_mountebank_executable() -> Path:
    DEFAULT_MB_NAME = Path("mb.cmd" if platform.system() == "Windows" else "mb")
    HOME_PATH = Path(expanduser("~")) / "node_modules" / ".bin"

    # Try all paths in the users PATH env
    paths = [HOME_PATH] + [Path(p) for p in (os.environ.get("PATH", "").split(os.pathsep)) if p]
    for PATH in paths:
        usr_bin = PATH / DEFAULT_MB_NAME
        if usr_bin.is_file() or usr_bin.is_symlink():
            return usr_bin
    mountebank_executable = DEFAULT_MB_PATH / DEFAULT_MB_NAME
    logger.info("Using mountebank executable %s", mountebank_executable)
    return mountebank_executable
