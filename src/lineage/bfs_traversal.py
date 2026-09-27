from collections import deque
from typing import Dict, List, Set, Optional, Any, Tuple
from src.lineage.graph_model import LineageGraph
from src.common.models import LineageNode

class BFSTraversal:
    """Cycle-safe BFS traversal algorithms for data lineage graphs."""

    @staticmethod
    def bfs_upstream(
        graph: LineageGraph,
        start_id: str,
        max_depth: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[LineageNode, int, List[str]]]:
        """Traverses upstream dependencies (in-edges). Returns list of (node, depth, path)."""
        if not graph.graph.has_node(start_id):
            return []

        visited: Set[str] = {start_id}
        queue = deque([(start_id, 0, [start_id])])
        results = []

        while queue:
            curr_id, depth, path = queue.popleft()
            curr_node = graph.get_node(curr_id)

            if curr_node and curr_id != start_id:
                # Apply optional filters
                if BFSTraversal._matches_filters(curr_node, filters):
                    results.append((curr_node, depth, path))

            if depth >= max_depth:
                continue

            # Deterministic sort of upstream predecessors (in-edges)
            predecessors = sorted(list(graph.graph.predecessors(curr_id)))
            for pred_id in predecessors:
                if pred_id not in visited:
                    visited.add(pred_id)
                    queue.append((pred_id, depth + 1, path + [pred_id]))

        return results

    @staticmethod
    def bfs_downstream(
        graph: LineageGraph,
        start_id: str,
        max_depth: int = 15,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[LineageNode, int, List[str]]]:
        """Traverses downstream dependents (out-edges). Returns list of (node, depth, path)."""
        if not graph.graph.has_node(start_id):
            return []

        visited: Set[str] = {start_id}
        queue = deque([(start_id, 0, [start_id])])
        results = []

        while queue:
            curr_id, depth, path = queue.popleft()
            curr_node = graph.get_node(curr_id)

            if curr_node and curr_id != start_id:
                if BFSTraversal._matches_filters(curr_node, filters):
                    results.append((curr_node, depth, path))

            if depth >= max_depth:
                continue

            # Deterministic sort of downstream successors (out-edges)
            successors = sorted(list(graph.graph.successors(curr_id)))
            for succ_id in successors:
                if succ_id not in visited:
                    visited.add(succ_id)
                    queue.append((succ_id, depth + 1, path + [succ_id]))

        return results

    @staticmethod
    def shortest_dependency_path(
        graph: LineageGraph,
        source_id: str,
        target_id: str
    ) -> Optional[List[str]]:
        """Finds shortest dependency path in edge count between source and target."""
        if not graph.graph.has_node(source_id) or not graph.graph.has_node(target_id):
            return None

        visited: Set[str] = {source_id}
        queue = deque([(source_id, [source_id])])

        while queue:
            curr_id, path = queue.popleft()
            if curr_id == target_id:
                return path

            successors = sorted(list(graph.graph.successors(curr_id)))
            for succ_id in successors:
                if succ_id not in visited:
                    visited.add(succ_id)
                    queue.append((succ_id, path + [succ_id]))

        return None

    @staticmethod
    def _matches_filters(node: LineageNode, filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        if "environment" in filters and node.environment != filters["environment"]:
            return False
        if "node_type" in filters:
            node_type_val = node.type.value if hasattr(node.type, "value") else str(node.type)
            if node_type_val != filters["node_type"]:
                return False
        if "active" in filters and node.active != filters["active"]:
            return False
        return True
