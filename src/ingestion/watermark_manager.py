import sqlite3
from datetime import datetime
from typing import Optional
from src.common.exceptions import WatermarkError
from src.common.logging import get_logger

logger = get_logger("watermark_manager")

class WatermarkManager:
    """Manages pipeline watermark state in SQLite control plane."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_watermark(self, pipeline_id: str) -> datetime:
        """Retrieves the last committed watermark for a pipeline."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT last_watermark FROM watermark_state WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            row = cursor.fetchone()
            if row and row[0]:
                if isinstance(row[0], str):
                    return datetime.fromisoformat(row[0])
                return row[0]
            # Default fallback epoch
            return datetime(1970, 1, 1, 0, 0, 0)
        except Exception as e:
            raise WatermarkError(f"Failed to fetch watermark for {pipeline_id}: {str(e)}")
        finally:
            conn.close()

    def commit_watermark(self, pipeline_id: str, new_watermark: datetime, batch_id: str) -> None:
        """Commits updated watermark ONLY after successful validation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            iso_wm = new_watermark.isoformat()
            cursor.execute(
                """
                INSERT INTO watermark_state (pipeline_id, last_watermark, high_watermark, batch_id, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(pipeline_id) DO UPDATE SET
                    last_watermark = excluded.last_watermark,
                    high_watermark = excluded.high_watermark,
                    batch_id = excluded.batch_id,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (pipeline_id, iso_wm, iso_wm, batch_id)
            )
            conn.commit()
            logger.info(f"Committed new watermark for {pipeline_id}: {iso_wm} (Batch: {batch_id})")
        except Exception as e:
            conn.rollback()
            raise WatermarkError(f"Failed to commit watermark for {pipeline_id}: {str(e)}")
        finally:
            conn.close()

    def reset_watermark(self, pipeline_id: str, reset_to: datetime) -> None:
        """Resets a stale or corrupt watermark (requires prior authorization/approval)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            iso_wm = reset_to.isoformat()
            cursor.execute(
                """
                UPDATE watermark_state
                SET last_watermark = ?, updated_at = CURRENT_TIMESTAMP
                WHERE pipeline_id = ?
                """,
                (iso_wm, pipeline_id)
            )
            conn.commit()
            logger.info(f"Reset watermark for {pipeline_id} to: {iso_wm}")
        except Exception as e:
            conn.rollback()
            raise WatermarkError(f"Failed to reset watermark for {pipeline_id}: {str(e)}")
        finally:
            conn.close()
