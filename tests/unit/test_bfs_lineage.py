import pytest
from src.lineage.graph_builder import GraphBuilder
from src.lineage.bfs_traversal import BFSTraversal
from scripts.seed_demo_data import seed

def test_bfs_traversal_upstream_downstream_and_shortest_path():
    seed()
    graph = GraphBuilder("data/control_plane.db").build_from_yaml()

    # Upstream from fact_orders
    upstream = BFSTraversal.bfs_upstream(graph, "fact_orders")
    upstream_ids = [n.node_id for n, _, _ in upstream]
    assert "pipe_orders_incremental" in upstream_ids
    assert "source_orders" in upstream_ids

    # Downstream from source_orders
    downstream = BFSTraversal.bfs_downstream(graph, "source_orders")
    downstream_ids = [n.node_id for n, _, _ in downstream]
    assert "pipe_orders_incremental" in downstream_ids
    assert "fact_orders" in downstream_ids

    # Shortest path from source_orders to rpt_sales_executive
    path = BFSTraversal.shortest_dependency_path(graph, "source_orders", "rpt_sales_executive")
    assert path is not None
    assert path[0] == "source_orders"
    assert path[-1] == "rpt_sales_executive"
