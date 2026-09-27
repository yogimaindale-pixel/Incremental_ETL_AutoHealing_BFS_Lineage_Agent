import sqlite3
from typing import Dict, Any, Tuple

class ReconciliationEngine:
    """Performs source-to-target row count and sum checksum reconciliation."""

    def __init__(self, source_db: str = "data/source.db", target_db: str = "data/target.db"):
        self.source_db = source_db
        self.target_db = target_db

    def reconcile_counts(self, source_table: str, target_table: str, tolerance_percent: float = 10.0) -> Tuple[bool, Dict[str, Any]]:
        conn_s = sqlite3.connect(self.source_db)
        conn_t = sqlite3.connect(self.target_db)

        try:
            cnt_s = conn_s.cursor().execute(f"SELECT COUNT(*) FROM {source_table}").fetchone()[0]
            cnt_t = conn_t.cursor().execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]

            diff = abs(cnt_s - cnt_t)
            allowed_diff = (cnt_s * (tolerance_percent / 100.0)) if cnt_s > 0 else 0
            passed = diff <= allowed_diff

            details = {
                "source_count": cnt_s,
                "target_count": cnt_t,
                "diff": diff,
                "tolerance_percent": tolerance_percent,
                "passed": passed
            }
            return passed, details
        finally:
            conn_s.close()
            conn_t.close()
