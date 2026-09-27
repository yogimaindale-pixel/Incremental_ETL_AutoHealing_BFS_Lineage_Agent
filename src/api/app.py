import uuid
import sqlite3
from fastapi import FastAPI, HTTPException
from src.api.schemas import FailureEventRequest, ApprovalDecisionRequest
from src.common.config import ConfigManager
from src.common.models import FailureEvent
from src.orchestration.coordinator import IncidentCoordinator
from src.lineage.bfs_traversal import BFSTraversal
from src.lineage.graph_builder import GraphBuilder
from src.observability.metrics import MetricsCalculator

app = FastAPI(
    title="Incremental ETL Auto-Healing & Lineage API",
    version="1.0.0",
    description="REST API endpoints for health, incidents, manual approvals, BFS lineage, and metrics."
)

config_manager = ConfigManager()
coordinator = IncidentCoordinator(config_manager)
metrics_calc = MetricsCalculator()

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": config_manager.env}

@app.post("/events/failures")
def receive_failure_event(req: FailureEventRequest):
    cid = req.correlation_id or f"corr_{uuid.uuid4().hex[:8]}"
    event = FailureEvent(
        event_id=f"evt_{uuid.uuid4().hex[:12]}",
        run_id=req.run_id,
        step_id=req.step_id,
        error_code=req.error_code,
        error_message=req.error_message,
        job_name=req.pipeline_id,
        correlation_id=cid
    )
    incident = coordinator.handle_failure_event(event, req.pipeline_id)
    return {"incident_id": incident.incident_id, "status": incident.status.value, "classification": incident.classification}

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    conn = sqlite3.connect("data/control_plane.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incident WHERE incident_id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "incident_id": row[0],
        "event_id": row[1],
        "pipeline_id": row[2],
        "correlation_id": row[3],
        "status": row[4],
        "classification": row[5],
        "confidence_score": row[6],
        "root_cause_node_id": row[7],
        "selected_runbook_id": row[8]
    }

@app.post("/incidents/{incident_id}/approve")
def approve_incident(incident_id: str, req: ApprovalDecisionRequest):
    try:
        incident = coordinator.process_approval(incident_id, approved=True, responder=req.responder or "operator")
        return {"incident_id": incident.incident_id, "status": incident.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/incidents/{incident_id}/reject")
def reject_incident(incident_id: str, req: ApprovalDecisionRequest):
    try:
        incident = coordinator.process_approval(incident_id, approved=False, responder=req.responder or "operator")
        return {"incident_id": incident.incident_id, "status": incident.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/lineage/{node_id}/upstream")
def get_upstream_lineage(node_id: str, max_depth: int = 10):
    nodes = BFSTraversal.bfs_upstream(coordinator.graph, node_id, max_depth=max_depth)
    return [{"node_id": n.node_id, "name": n.name, "depth": d, "path": p} for n, d, p in nodes]

@app.get("/lineage/{node_id}/downstream")
def get_downstream_lineage(node_id: str, max_depth: int = 15):
    nodes = BFSTraversal.bfs_downstream(coordinator.graph, node_id, max_depth=max_depth)
    return [{"node_id": n.node_id, "name": n.name, "depth": d, "path": p} for n, d, p in nodes]

@app.get("/metrics")
def get_metrics():
    return metrics_calc.get_summary_metrics()
