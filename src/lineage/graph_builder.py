import sqlite3
from typing import Dict, Any
from src.common.config import load_yaml_config
from src.lineage.graph_model import LineageGraph
from src.lineage.metadata_parser import MetadataParser
from src.common.logging import get_logger

logger = get_logger("graph_builder")

class GraphBuilder:
    """Builds and refreshes lineage graph in memory and persists to control SQLite DB."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path
        self.parser = MetadataParser()

    def build_from_yaml(self, yaml_path: str = "config/lineage_sources.yaml") -> LineageGraph:
        data = load_yaml_config(yaml_path)
        nodes, edges = self.parser.parse_sources_yaml(data)

        graph = LineageGraph()
        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)

        self._persist_graph(nodes, edges)
        logger.info(f"Built lineage graph with {len(nodes)} nodes and {len(edges)} edges from {yaml_path}")
        return graph

    def _persist_graph(self, nodes, edges):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            for n in nodes:
                cursor.execute(
                    """
                    INSERT INTO lineage_node (node_id, name, type, environment, active, metadata_version)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        name = excluded.name,
                        type = excluded.type,
                        environment = excluded.environment,
                        active = excluded.active
                    """,
                    (n.node_id, n.name, n.type.value if hasattr(n.type, "value") else str(n.type), n.environment, 1 if n.active else 0, n.metadata_version)
                )

            for e in edges:
                cursor.execute(
                    """
                    INSERT INTO lineage_edge (edge_id, source_id, target_id, type, active)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(edge_id) DO UPDATE SET
                        source_id = excluded.source_id,
                        target_id = excluded.target_id,
                        type = excluded.type,
                        active = excluded.active
                    """,
                    (e.edge_id, e.source_id, e.target_id, e.type.value if hasattr(e.type, "value") else str(e.type), 1 if e.active else 0)
                )
            conn.commit()
        finally:
            conn.close()
