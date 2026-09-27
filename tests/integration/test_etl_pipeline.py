import pytest
from datetime import datetime, timedelta
from src.common.config import ConfigManager
from src.ingestion.extractor import IncrementalExtractor
from src.ingestion.watermark_manager import WatermarkManager
from src.ingestion.incremental_loader import IncrementalLoader
from scripts.seed_demo_data import seed

def test_full_incremental_etl_pipeline():
    seed()
    wm_mgr = WatermarkManager()
    extractor = IncrementalExtractor()
    loader = IncrementalLoader()

    pipe_id = "pipe_orders_incremental"
    last_wm = wm_mgr.get_watermark(pipe_id)
    upper = datetime.utcnow()

    df, max_wm = extractor.extract_batch("source_orders", "updated_at", last_wm, upper, lookback_minutes=60)
    valid_df, dups_df = loader.deduplicate(df, "order_id", "updated_at")
    cnt = loader.upsert_target(valid_df, "fact_orders", "order_id", "batch_integ_001")

    wm_mgr.commit_watermark(pipe_id, max_wm, "batch_integ_001")

    assert cnt >= 0
    assert wm_mgr.get_watermark(pipe_id) == max_wm
