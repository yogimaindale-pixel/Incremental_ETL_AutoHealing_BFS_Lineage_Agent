import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple, Dict, Any
from src.common.exceptions import IngestionError
from src.common.logging import get_logger

logger = get_logger("extractor")

class IncrementalExtractor:
    """Extracts incremental batches based on watermark bounds and lookback window."""

    def __init__(self, source_db_path: str = "data/source.db"):
        self.source_db_path = source_db_path

    def extract_batch(
        self,
        table_name: str,
        watermark_col: str,
        last_watermark: datetime,
        upper_bound: datetime,
        lookback_minutes: int = 0
    ) -> Tuple[pd.DataFrame, datetime]:
        """Extracts records where watermark_col > (last_watermark - lookback) and <= upper_bound."""
        effective_start = last_watermark - timedelta(minutes=lookback_minutes)
        start_str = effective_start.isoformat()
        upper_str = upper_bound.isoformat()

        logger.info(f"Extracting {table_name} between {start_str} and {upper_str}")

        conn = sqlite3.connect(self.source_db_path)
        try:
            query = f"""
                SELECT * FROM {table_name}
                WHERE {watermark_col} > ? AND {watermark_col} <= ?
                ORDER BY {watermark_col} ASC
            """
            df = pd.read_sql_query(query, conn, params=(start_str, upper_str))

            max_wm = upper_bound
            if not df.empty and watermark_col in df.columns:
                max_in_batch = pd.to_datetime(df[watermark_col]).max().to_pydatetime()
                if max_in_batch > last_watermark:
                    max_wm = max_in_batch

            return df, max_wm
        except Exception as e:
            raise IngestionError(f"Extraction failed for {table_name}: {str(e)}")
        finally:
            conn.close()
