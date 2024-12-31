import logging
import os
import platform
from pathlib import Path

DEFAULT_MB_PATH = Path("node_modules") / ".bin"

logger = logging.getLogger(__name__)


def find_mountebank_executable() -> Path:
    default_mb_name = Path("mb.cmd" if platform.system() == "Windows" else "mb")
    home_path = Path.home() / "node_modules" / ".bin"

    # Try all paths in the users PATH env
    paths = [home_path] + [Path(p) for p in (os.environ.get("PATH", "").split(os.pathsep)) if p]
    for path in paths:
        usr_bin = path / default_mb_name
        if usr_bin.is_file() or usr_bin.is_symlink():
            return usr_bin
    mountebank_executable = DEFAULT_MB_PATH / default_mb_name
    logger.info("Using mountebank executable %s", mountebank_executable)
    return mountebank_executable
