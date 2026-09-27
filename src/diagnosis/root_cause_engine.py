from typing import List, Dict, Any, Optional
from src.common.models import FailureEvent, RootCauseCandidate
from src.lineage.graph_model import LineageGraph
from src.lineage.bfs_traversal import BFSTraversal
from src.diagnosis.evidence_collector import EvidenceCollector

class RootCauseEngine:
    """Scores and ranks root cause candidates using evidence and upstream BFS lineage."""

    def __init__(self, graph: LineageGraph, db_path: str = "data/control_plane.db"):
        self.graph = graph
        self.evidence_collector = EvidenceCollector(db_path)

    def find_root_cause(self, event: FailureEvent, start_node_id: str) -> List[RootCauseCandidate]:
        candidates: List[RootCauseCandidate] = []

        # 1. Exact failed node
        start_node = self.graph.get_node(start_node_id)
        if start_node:
            candidates.append(RootCauseCandidate(
                node_id=start_node.node_id,
                node_name=start_node.name,
                score=1.0,
                reason=f"Directly failed node/dataset '{start_node.name}' (Error: {event.error_code})"
            ))

        # 2. Upstream BFS candidates
        upstream = BFSTraversal.bfs_upstream(self.graph, start_node_id, max_depth=10)
        for node, depth, path in upstream:
            # Score decays by depth
            base_score = max(0.90 - (depth * 0.1), 0.20)
            reason = f"Upstream dependency on path: {' -> '.join(path)}"
            candidates.append(RootCauseCandidate(
                node_id=node.node_id,
                node_name=node.name,
                score=round(base_score, 2),
                reason=reason
            ))

        # Sort by score descending
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates
