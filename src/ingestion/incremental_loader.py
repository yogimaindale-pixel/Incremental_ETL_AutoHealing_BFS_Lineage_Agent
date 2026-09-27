import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple
from src.common.exceptions import IngestionError
from src.common.logging import get_logger

logger = get_logger("incremental_loader")

class IncrementalLoader:
    """Handles key deduplication, MERGE/UPSERT into target table, and quarantining invalid rows."""

    def __init__(self, target_db_path: str = "data/target.db", quarantine_dir: str = "data/quarantine"):
        self.target_db_path = target_db_path
        self.quarantine_dir = quarantine_dir
        os.makedirs(quarantine_dir, exist_ok=True)

    def deduplicate(self, df: pd.DataFrame, key_col: str, watermark_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Deduplicates by business key, keeping latest watermark_col row. Returns (valid_df, duplicate_df)."""
        if df.empty or key_col not in df.columns:
            return df, pd.DataFrame()

        # Sort by watermark_col ascending so last item is newest
        df_sorted = df.sort_values(by=[watermark_col])
        dups = df_sorted[df_sorted.duplicated(subset=[key_col], keep="last")]
        valid = df_sorted.drop_duplicates(subset=[key_col], keep="last")

        return valid, dups

    def quarantine_rows(self, df: pd.DataFrame, reason: str, batch_id: str) -> str:
        """Quarantines invalid or duplicate rows to CSV in quarantine directory."""
        if df.empty:
            return ""
        filename = f"quarantine_{batch_id}_{int(datetime.utcnow().timestamp())}.csv"
        path = os.path.join(self.quarantine_dir, filename)
        df_copy = df.copy()
        df_copy["quarantine_reason"] = reason
        df_copy["quarantined_at"] = datetime.utcnow().isoformat()
        df_copy.to_csv(path, index=False)
        logger.warning(f"Quarantined {len(df_copy)} rows to {path} (Reason: {reason})")
        return path

    def upsert_target(
        self,
        df: pd.DataFrame,
        target_table: str,
        key_col: str,
        batch_id: str
    ) -> int:
        """Executes idempotent MERGE / UPSERT into SQLite target table."""
        if df.empty:
            return 0

        conn = sqlite3.connect(self.target_db_path)
        cursor = conn.cursor()
        loaded_count = 0
        try:
            df["batch_id"] = batch_id
            df["loaded_at"] = datetime.utcnow().isoformat()

            columns = list(df.columns)
            col_list_str = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))

            # SQLite UPSERT on conflict key_col
            update_cols = [c for c in columns if c != key_col]
            update_str = ", ".join([f"{c} = excluded.{c}" for c in update_cols])

            sql = f"""
                INSERT INTO {target_table} ({col_list_str})
                VALUES ({placeholders})
                ON CONFLICT({key_col}) DO UPDATE SET {update_str}
            """

            records = [tuple(row) for row in df.to_numpy()]
            cursor.executemany(sql, records)
            conn.commit()
            loaded_count = len(records)
            logger.info(f"Successfully upserted {loaded_count} rows into {target_table}")
            return loaded_count
        except Exception as e:
            conn.rollback()
            raise IngestionError(f"UPSERT into {target_table} failed: {str(e)}")
        finally:
            conn.close()
