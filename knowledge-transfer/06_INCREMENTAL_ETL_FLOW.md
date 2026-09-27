# 06 Incremental ETL Workflow

## 1. Step-by-Step Execution Sequence
1. **Read Watermark**: `WatermarkManager.get_watermark(pipeline_id)` retrieves the last committed timestamp (e.g. `2026-09-26T19:00:00`).
2. **Determine Bounds**: Fixed upper bound = `datetime.utcnow()`. Lower bound = `last_watermark - lookback_minutes` (e.g. 60 minute lookback window).
3. **Extract Batch**: `IncrementalExtractor.extract_batch()` executes parameterized SQL query `SELECT * FROM source_table WHERE updated_at >= ? AND updated_at <= ?`.
4. **Deduplicate**: `IncrementalLoader.deduplicate()` drops duplicate primary key rows within batch, quarantining invalid duplicates.
5. **UPSERT Target**: `IncrementalLoader.upsert_target()` executes atomic SQLite `INSERT INTO target_table VALUES (...) ON CONFLICT(key) DO UPDATE`.
6. **Commit Watermark**: `WatermarkManager.commit_watermark()` updates watermark timestamp in `watermark_state` table.
