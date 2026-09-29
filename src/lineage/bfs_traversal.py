# Import double-ended queue (deque) for fast O(1) FIFO queue operations during BFS traversal
from collections import deque
# Import typing hints for dictionaries, lists, sets, optional types, any values, and tuple structures
from typing import Dict, List, Set, Optional, Any, Tuple
# Import LineageGraph container class wrapping NetworkX Directed Graph
from src.lineage.graph_model import LineageGraph
# Import LineageNode Pydantic model for node metadata checks
from src.common.models import LineageNode

# Class implementing Breadth-First Search (BFS) graph traversal algorithms for lineage exploration
class BFSTraversal:
    """Cycle-safe BFS traversal algorithms for data lineage graphs."""

    # Static method to traverse upstream dependencies (in-edges) from a starting node
    @staticmethod
    def bfs_upstream(
        graph: LineageGraph, # Target lineage graph instance
        start_id: str, # Starting node identifier to begin upstream traversal from
        max_depth: int = 10, # Maximum depth limit to prevent infinite depth traversal
        filters: Optional[Dict[str, Any]] = None # Optional node property filter criteria
    ) -> List[Tuple[LineageNode, int, List[str]]]: # Returns list of tuples: (LineageNode, depth, path)
        # Check if the start node exists in the graph; if not, return empty list immediately
        if not graph.graph.has_node(start_id):
            return []

        # Initialize visited set containing start_id to prevent infinite loops in cyclic graphs
        visited: Set[str] = {start_id}
        # Initialize FIFO queue storing tuples of (current_node_id, current_depth, traversal_path)
        queue = deque([(start_id, 0, [start_id])])
        # Initialize results list to collect matching upstream nodes
        results = []

        # Loop until the BFS queue becomes empty
        while queue:
            # Dequeue the oldest item from the left of the queue (FIFO ordering)
            curr_id, depth, path = queue.popleft()
            # Fetch node object from graph store using node identifier
            curr_node = graph.get_node(curr_id)

            # Process node if valid node exists and it is not the starting seed node
            if curr_node and curr_id != start_id:
                # Apply property filter checks (environment, node_type, active status)
                if BFSTraversal._matches_filters(curr_node, filters):
                    # Append matching node, depth integer, and path list to results
                    results.append((curr_node, depth, path))

            # If current depth reaches max_depth limit, do not explore deeper predecessors
            if depth >= max_depth:
                continue

            # Deterministic sort of upstream predecessors (incoming edges in directed graph)
            predecessors = sorted(list(graph.graph.predecessors(curr_id)))
            # Iterate through each upstream predecessor node identifier
            for pred_id in predecessors:
                # Check if predecessor has not been visited yet (cycle safety check)
                if pred_id not in visited:
                    # Mark predecessor as visited
                    visited.add(pred_id)
                    # Enqueue predecessor with incremented depth and appended path
                    queue.append((pred_id, depth + 1, path + [pred_id]))

        # Return final accumulated list of upstream lineage nodes
        return results

    # Static method to traverse downstream dependents (out-edges) from a starting node
    @staticmethod
    def bfs_downstream(
        graph: LineageGraph, # Target lineage graph instance
        start_id: str, # Starting node identifier to begin downstream impact traversal from
        max_depth: int = 15, # Maximum depth limit for downstream impact radius
        filters: Optional[Dict[str, Any]] = None # Optional property filters
    ) -> List[Tuple[LineageNode, int, List[str]]]: # Returns list of (LineageNode, depth, path)
        # Check if start node exists; return empty if missing
        if not graph.graph.has_node(start_id):
            return []

        # Initialize visited set with start_id to prevent infinite cycles
        visited: Set[str] = {start_id}
        # Initialize queue with initial start node state tuple
        queue = deque([(start_id, 0, [start_id])])
        # Initialize results list
        results = []

        # Loop until queue is empty
        while queue:
            # Pop next node from queue
            curr_id, depth, path = queue.popleft()
            # Retrieve node metadata object
            curr_node = graph.get_node(curr_id)

            # Process non-seed node if present
            if curr_node and curr_id != start_id:
                # Evaluate filter matching criteria
                if BFSTraversal._matches_filters(curr_node, filters):
                    # Record node, depth, and traversal path
                    results.append((curr_node, depth, path))

            # Stop expanding edges if maximum depth limit reached
            if depth >= max_depth:
                continue

            # Deterministic sort of downstream successors (outgoing edges)
            successors = sorted(list(graph.graph.successors(curr_id)))
            # Iterate through each downstream successor node identifier
            for succ_id in successors:
                # Check if successor has not been visited yet
                if succ_id not in visited:
                    # Mark successor as visited
                    visited.add(succ_id)
                    # Enqueue successor with incremented depth and extended path
                    queue.append((succ_id, depth + 1, path + [succ_id]))

        # Return final downstream impact results list
        return results

    # Static method to compute shortest dependency path between source and target nodes
    @staticmethod
    def shortest_dependency_path(
        graph: LineageGraph, # Target lineage graph instance
        source_id: str, # Origin source node identifier
        target_id: str # Target destination node identifier
    ) -> Optional[List[str]]: # Returns list of node IDs forming shortest path or None
        # Verify both source and target nodes exist in graph
        if not graph.graph.has_node(source_id) or not graph.graph.has_node(target_id):
            return None

        # Initialize visited tracking set
        visited: Set[str] = {source_id}
        # Initialize queue with source node and initial single-node path list
        queue = deque([(source_id, [source_id])])

        # Execute BFS search loop
        while queue:
            # Dequeue current node and current path list
            curr_id, path = queue.popleft()
            # If current node matches target_id, shortest path is found!
            if curr_id == target_id:
                return path

            # Sort successors deterministically
            successors = sorted(list(graph.graph.successors(curr_id)))
            # Explore outgoing neighbor nodes
            for succ_id in successors:
                # Check cycle safety
                if succ_id not in visited:
                    # Mark neighbor visited
                    visited.add(succ_id)
                    # Enqueue neighbor with path extension
                    queue.append((succ_id, path + [succ_id]))

        # Return None if no connecting path exists between source and target
        return None

    # Helper method to evaluate if a node satisfies optional filter criteria
    @staticmethod
    def _matches_filters(node: LineageNode, filters: Optional[Dict[str, Any]]) -> bool:
        # If no filters provided, all nodes match (return True)
        if not filters:
            return True
        # Check environment filter string match
        if "environment" in filters and node.environment != filters["environment"]:
            return False
        # Check node type filter string match
        if "node_type" in filters:
            # Extract string value from Enum or object
            node_type_val = node.type.value if hasattr(node.type, "value") else str(node.type)
            if node_type_val != filters["node_type"]:
                return False
        # Check active status Boolean match
        if "active" in filters and node.active != filters["active"]:
            return False
        # Return True if node passed all specified filters
        return True

