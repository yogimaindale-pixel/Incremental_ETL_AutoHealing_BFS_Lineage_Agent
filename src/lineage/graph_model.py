import networkx as nx
from typing import Dict, List, Optional, Any
from src.common.models import LineageNode, LineageEdge, NodeType, EdgeType
from src.common.exceptions import LineageGraphError

class LineageGraph:
    """Directed property graph representing data lineage."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: LineageNode):
        self.graph.add_node(
            node.node_id,
            name=node.name,
            type=node.type.value if isinstance(node.type, NodeType) else node.type,
            environment=node.environment,
            source_adapter=node.source_adapter,
            metadata_version=node.metadata_version,
            active=node.active,
            obj=node
        )

    def add_edge(self, edge: LineageEdge):
        if not self.graph.has_node(edge.source_id):
            raise LineageGraphError(f"Source node '{edge.source_id}' does not exist in graph.")
        if not self.graph.has_node(edge.target_id):
            raise LineageGraphError(f"Target node '{edge.target_id}' does not exist in graph.")
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_id=edge.edge_id,
            type=edge.type.value if isinstance(edge.type, EdgeType) else edge.type,
            active=edge.active,
            obj=edge
        )

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id].get("obj")
        return None

    def get_nodes(self) -> List[LineageNode]:
        return [data["obj"] for _, data in self.graph.nodes(data=True) if "obj" in data]

    def get_edges(self) -> List[LineageEdge]:
        return [data["obj"] for _, _, data in self.graph.edges(data=True) if "obj" in data]
