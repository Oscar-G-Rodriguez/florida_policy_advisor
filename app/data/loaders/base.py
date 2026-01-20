from __future__ import annotations

from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def fixture_path(dataset_id: str, filename: str) -> Optional[Path]:
    candidate = DATA_DIR / "fixtures" / dataset_id / filename
    return candidate if candidate.exists() else None


def processed_path(dataset_id: str, filename: str) -> Path:
    return DATA_DIR / "processed" / dataset_id / filename


def raw_path(dataset_id: str, filename: str) -> Path:
    return DATA_DIR / "raw" / dataset_id / filename
