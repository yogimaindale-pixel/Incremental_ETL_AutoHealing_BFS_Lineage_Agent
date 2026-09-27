# BFS Data Lineage Model

## Graph Schema
- **Nodes**: `system`, `table`, `pipeline`, `report`, `API`, `column`, `schema`, `database`.
- **Edges**: `READS_FROM`, `WRITES_TO`, `TRANSFORMS`, `TRIGGERS`, `DEPENDS_ON`, `PRODUCES`, `CONSUMES`, `DERIVES_FROM`.

## BFS Traversal Properties
- **Cycle Safety**: Maintained via `visited` node set.
- **Deterministic Neighbor Sorting**: Neighbors sorted alphabetically by `node_id`.
- **Upstream RCA Search**: Traverses in-edges to find root cause candidates.
- **Downstream Impact Analysis**: Traverses out-edges to calculate blast radius.
