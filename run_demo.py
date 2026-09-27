#!/usr/bin/env python3
import sys
import os
import uuid
import argparse
from datetime import datetime, timedelta
import pandas as pd

from src.common.config import ConfigManager
from src.common.models import FailureEvent, IncidentState
from src.ingestion.extractor import IncrementalExtractor
from src.ingestion.watermark_manager import WatermarkManager
from src.ingestion.incremental_loader import IncrementalLoader
from src.observability.event_collector import EventCollector
from src.observability.failure_detector import FailureDetector
from src.observability.metrics import MetricsCalculator
from src.orchestration.coordinator import IncidentCoordinator
from src.lineage.bfs_traversal import BFSTraversal
from src.lineage.impact_analyzer import ImpactAnalyzer
from src.reporting.incident_report import IncidentReportGenerator
from src.reporting.lineage_report import LineageReportGenerator
from scripts.seed_demo_data import seed

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def run_normal_etl(coordinator: IncidentCoordinator, config_manager: ConfigManager):
    print_header("Executing Normal Incremental ETL Run")
    wm_mgr = WatermarkManager()
    extractor = IncrementalExtractor()
    loader = IncrementalLoader()
    collector = EventCollector()

    pipeline_id = "pipe_orders_incremental"
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()

    collector.record_pipeline_run(run_id, pipeline_id, "STARTED", start_time)

    # 1. Read watermark
    last_wm = wm_mgr.get_watermark(pipeline_id)
    upper_bound = datetime.utcnow()
    print(f"[*] Previous Watermark: {last_wm.isoformat()}")
    print(f"[*] Upper Bound: {upper_bound.isoformat()}")

    # 2. Extract
    df, max_wm = extractor.extract_batch("source_orders", "updated_at", last_wm, upper_bound, lookback_minutes=60)
    print(f"[*] Extracted {len(df)} records from source_orders")

    # 3. Deduplicate
    valid_df, dups_df = loader.deduplicate(df, "order_id", "updated_at")
    if not dups_df.empty:
        loader.quarantine_rows(dups_df, "Duplicate order_id in batch", run_id)

    # 4. Upsert
    loaded_cnt = loader.upsert_target(valid_df, "fact_orders", "order_id", run_id)

    # 5. Commit Watermark
    wm_mgr.commit_watermark(pipeline_id, max_wm, run_id)
    collector.record_pipeline_run(run_id, pipeline_id, "SUCCESS", start_time, datetime.utcnow(), len(df), loaded_cnt)

    print(f"[+] Incremental ETL succeeded. {loaded_cnt} rows UPSERTED into fact_orders.")
    print(f"[+] Updated Watermark committed: {max_wm.isoformat()}")

def run_scenarios(coordinator: IncidentCoordinator, config_manager: ConfigManager):
    print_header("Executing All 12 Required Demonstration Scenarios")
    detector = FailureDetector()

    scenarios = [
        ("Scenario 1: Transient Connection Failure", "TIMEOUT", "Database query timed out waiting for connection socket", "source_orders"),
        ("Scenario 2: Late Source File Arrival", "FILE_NOT_FOUND", "Source file /data/input/orders_2026.csv not found", "source_orders"),
        ("Scenario 3: Duplicate Business Key", "DUPLICATE_KEY", "UNIQUE constraint failed: fact_orders.order_id", "source_orders"),
        ("Scenario 4: Stale Watermark / Checkpoint Mismatch", "STALE_WATERMARK", "Watermark state ahead of source timestamp", "source_orders"),
        ("Scenario 5: Missing Target Partition", "PARTITION_NOT_FOUND", "Missing partition 2026_09 for target table", "fact_orders"),
        ("Scenario 6: Additive Schema Drift", "ADDITIVE_SCHEMA_DRIFT", "Additive schema drift detected: column 'discount_amount' added", "source_orders"),
        ("Scenario 7: Breaking Schema Drift", "BREAKING_SCHEMA_DRIFT", "Breaking schema drift: missing non-null column 'customer_id'", "source_orders"),
        ("Scenario 8: Insufficient Permission / Credential Error", "ACCESS_DENIED", "Access denied for user 'etl_agent' on table 'control_plane'", "source_orders"),
        ("Scenario 9: Data Quality Threshold Breach", "DQ_THRESHOLD_BREACH", "Null value percentage 25% exceeded threshold 0%", "source_orders"),
        ("Scenario 10: Downstream Impact Analysis", "IMPACT_ANALYSIS", "Simulated column type alteration on source_orders", "source_orders"),
        ("Scenario 11: Circular Lineage Cycle Safety", "CYCLE_CHECK", "Proving cycle-safe BFS traversal", "source_orders"),
        ("Scenario 12: Failed Remediation & Rollback Circuit Breaker", "REMEDIATION_FAILURE", "Forced runbook failure testing rollback", "source_orders")
    ]

    for name, code, msg, node_id in scenarios:
        print(f"\n---> {name}")
        run_id = f"run_scen_{uuid.uuid4().hex[:6]}"
        cid = f"corr_{uuid.uuid4().hex[:8]}"

        if code == "IMPACT_ANALYSIS":
            analyzer = ImpactAnalyzer(coordinator.graph)
            blast = analyzer.analyze_blast_radius("source_orders")
            print(f"  [BFS Lineage] Total Downstream Impacted Assets: {blast['total_impacted_count']}")
            for asset in blast['impacted_assets']:
                print(f"    - [{asset['type']}] {asset['name']} (Path: {asset['path']})")
            rep_gen = LineageReportGenerator()
            csv_path = rep_gen.export_blast_radius_csv("source_orders", blast)
            print(f"  [Report] Exported blast radius report to {csv_path}")
            continue

        if code == "CYCLE_CHECK":
            upstream = BFSTraversal.bfs_upstream(coordinator.graph, "source_orders")
            print(f"  [BFS Cycle Safety] Traversed {len(upstream)} upstream nodes without infinite loop.")
            continue

        evt = detector.normalize_exception(Exception(msg), run_id, "pipe_orders_incremental", "step_extract", cid, error_code=code)
        incident = coordinator.handle_failure_event(evt, "pipe_orders_incremental", source_node_id=node_id)

        print(f"  [Incident ID] {incident.incident_id}")
        print(f"  [Classification] {incident.classification} (Confidence: {incident.confidence_score})")
        print(f"  [State Machine] Final Status: {incident.status.value}")
        print(f"  [Selected Runbook] {incident.selected_runbook_id or 'None'}")

        if incident.status == IncidentState.AWAITING_APPROVAL:
            print(f"  [*] Incident requires approval! Auto-approving for scenario demonstration...")
            inc_after = coordinator.process_approval(incident.incident_id, approved=True, responder="auto_demo_operator")
            print(f"  [State Machine After Approval] Status: {inc_after.status.value}")

def main():
    parser = argparse.ArgumentParser(description="Incremental ETL Auto-Healing & Lineage CLI Runner")
    parser.add_argument("--all-scenarios", action="store_true", help="Run happy path ETL and all 12 failure scenarios")
    parser.add_argument("--etl-only", action="store_true", help="Run normal incremental ETL pipeline only")
    parser.add_argument("--lineage-upstream", type=str, help="Get upstream lineage for specified node ID")
    parser.add_argument("--lineage-downstream", type=str, help="Get downstream lineage for specified node ID")

    args = parser.parse_args()

    # Ensure demo data seeded
    seed()

    config_manager = ConfigManager()
    coordinator = IncidentCoordinator(config_manager)

    if args.lineage_upstream:
        nodes = BFSTraversal.bfs_upstream(coordinator.graph, args.lineage_upstream)
        print_header(f"Upstream Lineage for '{args.lineage_upstream}'")
        for n, d, p in nodes:
            print(f"  Depth {d}: [{n.type.value}] {n.name} (Path: {' -> '.join(p)})")
        return

    if args.lineage_downstream:
        nodes = BFSTraversal.bfs_downstream(coordinator.graph, args.lineage_downstream)
        print_header(f"Downstream Lineage for '{args.lineage_downstream}'")
        for n, d, p in nodes:
            print(f"  Depth {d}: [{n.type.value}] {n.name} (Path: {' -> '.join(p)})")
        return

    if args.etl_only:
        run_normal_etl(coordinator, config_manager)
        return

    # Default to running all scenarios
    run_normal_etl(coordinator, config_manager)
    run_scenarios(coordinator, config_manager)

    # Summary Metrics
    metrics_calc = MetricsCalculator()
    summary = metrics_calc.get_summary_metrics()
    print_header("Operational Performance Summary Metrics")
    for k, v in summary.items():
        print(f"  {k:30s}: {v}")

if __name__ == "__main__":
    main()
