from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def stdio_command(script_relative: str) -> list[str]:
    return [sys.executable, str(project_root() / script_relative)]
