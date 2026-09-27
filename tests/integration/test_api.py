import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from scripts.seed_demo_data import seed

client = TestClient(app)

def test_api_health_metrics_lineage():
    seed()

    # Health
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # Metrics
    res_m = client.get("/metrics")
    assert res_m.status_code == 200

    # Lineage
    res_l = client.get("/lineage/source_orders/downstream")
    assert res_l.status_code == 200
    assert isinstance(res_l.json(), list)
