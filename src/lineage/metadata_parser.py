import uuid
from typing import Dict, List, Any, Tuple
from src.common.models import LineageNode, LineageEdge, NodeType, EdgeType

class MetadataParser:
    """Parses YAML and SQL configurations into LineageNode and LineageEdge objects."""

    def parse_sources_yaml(self, config: Dict[str, Any]) -> Tuple[List[LineageNode], List[LineageEdge]]:
        nodes = []
        edges = []

        for n in config.get("nodes", []):
            node = LineageNode(
                node_id=n["id"],
                name=n["name"],
                type=NodeType(n["type"]),
                environment=n.get("environment", "local"),
                active=n.get("active", True)
            )
            nodes.append(node)

        for e in config.get("edges", []):
            edge = LineageEdge(
                edge_id=f"edge_{uuid.uuid4().hex[:8]}",
                source_id=e["source"],
                target_id=e["target"],
                type=EdgeType(e["type"]),
                active=e.get("active", True)
            )
            edges.append(edge)

        return nodes, edges
