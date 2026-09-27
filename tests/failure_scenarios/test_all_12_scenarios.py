import pytest
from src.common.config import ConfigManager
from src.observability.failure_detector import FailureDetector
from src.orchestration.coordinator import IncidentCoordinator
from scripts.seed_demo_data import seed

def test_all_12_failure_scenarios():
    seed()
    config_manager = ConfigManager()
    coordinator = IncidentCoordinator(config_manager)
    detector = FailureDetector()

    scenarios = [
        ("TIMEOUT", "Database timeout", "TRANSIENT_CONNECTION"),
        ("FILE_NOT_FOUND", "File not found", "SOURCE_FILE_LATE"),
        ("DUPLICATE_KEY", "Unique key violation", "DUPLICATE_BUSINESS_KEY"),
        ("STALE_WATERMARK", "Watermark ahead of source", "STALE_CHECKPOINT"),
        ("PARTITION_NOT_FOUND", "Partition missing", "TARGET_PARTITION_MISSING"),
        ("ADDITIVE_SCHEMA_DRIFT", "New column added", "SCHEMA_ADDITIVE_DRIFT"),
        ("BREAKING_SCHEMA_DRIFT", "Column missing", "SCHEMA_BREAKING_DRIFT"),
        ("ACCESS_DENIED", "Access denied", "INSUFFICIENT_PERMISSION"),
        ("DQ_THRESHOLD_BREACH", "Null threshold breach", "DATA_QUALITY_THRESHOLD_BREACH"),
    ]

    for code, msg, expected_cls in scenarios:
        evt = detector.normalize_exception(
            Exception(msg), "run_scen", "pipe_orders_incremental", "step_ex", "corr_scen", error_code=code
        )
        incident = coordinator.handle_failure_event(evt, "pipe_orders_incremental")
        assert incident.classification == expected_cls
