from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.data.quality import assess_dataset  # noqa: E402
from app.data.registry import get_dataset_metadata  # noqa: E402


FILES = {
    "bls_unemployment": ROOT_DIR / "data" / "processed" / "bls_unemployment" / "unemployment.csv",
    "fred_macro": ROOT_DIR / "data" / "processed" / "fred_macro" / "fred_macro.csv",
    "census_acs_fl_county": ROOT_DIR / "data" / "processed" / "census_acs_fl_county" / "acs_county.csv",
}


def main() -> None:
    reports = []
    for dataset_id, path in FILES.items():
        frame = pd.read_csv(path) if path.exists() else pd.DataFrame()
        reports.append({
            "dataset_id": dataset_id,
            "source": get_dataset_metadata(dataset_id),
            "quality": assess_dataset(dataset_id, frame),
        })
    payload = {"assessed_at": date.today().isoformat(), "reports": reports}
    output = ROOT_DIR / "portfolio_evidence" / "data_quality_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
