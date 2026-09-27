import os
import sqlite3
from typing import Dict, Any

class TechnicalValidator:
    """Validates pipeline step completion, target reachability, and partition presence."""

    def __init__(self, target_db_path: str = "data/target.db"):
        self.target_db_path = target_db_path

    def validate_target_reachability(self) -> bool:
        """Verifies that the target database is reachable."""
        try:
            conn = sqlite3.connect(self.target_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def validate_table_exists(self, table_name: str) -> bool:
        """Verifies that the target table exists."""
        try:
            conn = sqlite3.connect(self.target_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            res = cursor.fetchone()
            conn.close()
            return res is not None
        except Exception:
            return False
