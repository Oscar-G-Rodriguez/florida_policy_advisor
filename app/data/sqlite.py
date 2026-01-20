from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "data" / "app.db"


def write_table(df: pd.DataFrame, table_name: str, db_path: Optional[Path] = None) -> None:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
