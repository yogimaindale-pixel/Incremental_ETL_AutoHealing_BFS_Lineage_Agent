from typing import Dict, List, Any
from src.lineage.graph_model import LineageGraph
from src.lineage.bfs_traversal import BFSTraversal

class ImpactAnalyzer:
    """Performs downstream impact analysis to determine blast radius of failures or changes."""

    def __init__(self, graph: LineageGraph):
        self.graph = graph

    def analyze_blast_radius(self, node_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """Calculates downstream impacted assets and organizes them by node type and depth."""
        impacted_nodes = BFSTraversal.bfs_downstream(self.graph, node_id, max_depth=max_depth)

        impact_summary = {
            "root_node_id": node_id,
            "total_impacted_count": len(impacted_nodes),
            "max_depth_reached": max([d for _, d, _ in impacted_nodes], default=0),
            "impacted_assets": [],
            "impacted_by_type": {}
        }

        for node, depth, path in impacted_nodes:
            type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
            asset_info = {
                "node_id": node.node_id,
                "name": node.name,
                "type": type_str,
                "depth": depth,
                "path": " -> ".join(path)
            }
            impact_summary["impacted_assets"].append(asset_info)

            if type_str not in impact_summary["impacted_by_type"]:
                impact_summary["impacted_by_type"][type_str] = 0
            impact_summary["impacted_by_type"][type_str] += 1

        return impact_summary
