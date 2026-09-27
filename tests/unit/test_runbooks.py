import pytest
from src.healing.runbook_registry import RunbookRegistry
from scripts.seed_demo_data import seed

def test_runbook_registry_execution():
    seed()
    registry = RunbookRegistry()

    res_retry = registry.execute_runbook("RB-RETRY-001", {})
    assert res_retry is True

    res_add_schema = registry.execute_runbook("RB-ADD-SCHEMA-001", {"target_table": "fact_orders", "new_column": "unit_test_col"})
    assert res_add_schema is True
