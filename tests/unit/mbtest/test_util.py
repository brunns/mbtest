import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from mbtest.util import find_mountebank_executable

logger = logging.getLogger(__name__)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires Python 3.9")
def test_find_mountebank_install(monkeypatch):
    linux_mb_name = "mb"
    windows_mb_name = "mb.cmd"
    user_home = Path("home")
    user_bin = Path("node_modules") / ".bin"

    with (
        patch("platform.system", return_value="Linux"),
        patch("pathlib.Path.is_file", return_value=False),
        patch("pathlib.Path.is_symlink", return_value=False),
    ):
        assert find_mountebank_executable() == user_bin / linux_mb_name

    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.Path.is_file", return_value=False),
        patch("pathlib.Path.is_symlink", return_value=False),
    ):
        assert find_mountebank_executable() == user_bin / windows_mb_name

    monkeypatch.setenv("HOME", str(user_home))
    monkeypatch.setenv("USERPROFILE", str(user_home))

    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        assert find_mountebank_executable() == user_home / user_bin / windows_mb_name

    with (
        patch("platform.system", return_value="Linux"),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        assert find_mountebank_executable() == user_home / user_bin / linux_mb_name
