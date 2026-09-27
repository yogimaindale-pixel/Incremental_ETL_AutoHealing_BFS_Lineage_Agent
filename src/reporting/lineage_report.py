import os
import csv
from typing import Dict, List, Any

class LineageReportGenerator:
    """Exports upstream lineage and downstream impact analysis reports to CSV and JSON."""

    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(artifacts_dir, exist_ok=True)

    def export_blast_radius_csv(self, node_id: str, blast_radius: Dict[str, Any]) -> str:
        filepath = os.path.join(self.artifacts_dir, f"blast_radius_{node_id}.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Node ID", "Name", "Type", "Depth", "Path"])
            for asset in blast_radius.get("impacted_assets", []):
                writer.writerow([
                    asset["node_id"],
                    asset["name"],
                    asset["type"],
                    asset["depth"],
                    asset["path"]
                ])
        return filepath
