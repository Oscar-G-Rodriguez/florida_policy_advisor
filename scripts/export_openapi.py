from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402


def main() -> None:
    output_path = Path("submission_evidence") / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
