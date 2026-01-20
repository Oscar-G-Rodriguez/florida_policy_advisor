from __future__ import annotations

import sys
from pathlib import Path


def get_static_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "app" / "static"
    return Path(__file__).resolve().parents[1] / "static"
