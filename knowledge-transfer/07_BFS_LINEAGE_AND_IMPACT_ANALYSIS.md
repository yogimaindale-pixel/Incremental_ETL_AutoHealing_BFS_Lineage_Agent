# 07 BFS Data Lineage and Impact Analysis

## 1. Breadth-First Search (BFS) Traversal
BFS is used for deterministic, level-by-level dependency discovery across the lineage property graph.

### Upstream Traversal (Root Cause Search)
- Traverses in-edges (`predecessors`) from a target node.
- Uses a `queue` and a `visited` set to guarantee cycle safety.
- Sorts neighbor nodes alphabetically by `node_id` to guarantee reproducible execution order.

### Downstream Traversal (Blast Radius Calculation)
- Traverses out-edges (`successors`) from a source/failed node.
- Identifies all downstream pipelines, target tables, REST APIs, and executive report dashboards that will be impacted by the failure.

## 2. Shortest Dependency Path
`BFSTraversal.shortest_dependency_path(graph, start_id, end_id)` finds the shortest directed path between two nodes in the graph.
