import os
import pytest
from datetime import datetime
from src.ingestion.watermark_manager import WatermarkManager
from scripts.seed_demo_data import seed

def test_watermark_manager_commit_and_get():
    seed()
    wm_mgr = WatermarkManager("data/control_plane.db")
    pipe_id = "pipe_orders_incremental"

    wm_before = wm_mgr.get_watermark(pipe_id)
    assert isinstance(wm_before, datetime)

    new_wm = datetime(2026, 9, 27, 12, 0, 0)
    wm_mgr.commit_watermark(pipe_id, new_wm, "batch_test_001")

    wm_after = wm_mgr.get_watermark(pipe_id)
    assert wm_after == new_wm
