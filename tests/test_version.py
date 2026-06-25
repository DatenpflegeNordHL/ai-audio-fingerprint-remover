from __future__ import annotations

import re

import pytest

from audio_quality_humanizer.__version__ import __version__
from audio_quality_humanizer.cli import main


def test_version_string_is_semanticish():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_cli_version_flag_outputs_package_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.out.strip() == f"audio-quality-humanizer {__version__}"
