import os
import json
import sqlite3
from typing import Dict, Any

class IncidentReportGenerator:
    """Generates structured Markdown and JSON incident evidence reports."""

    def __init__(self, db_path: str = "data/control_plane.db", artifacts_dir: str = "artifacts"):
        self.db_path = db_path
        self.artifacts_dir = artifacts_dir
        os.makedirs(artifacts_dir, exist_ok=True)

    def generate_report(self, incident_id: str) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incident WHERE incident_id = ?", (incident_id,))
        inc_row = cursor.fetchone()
        conn.close()

        if not inc_row:
            return ""

        md_content = f"""# Incident Report: {incident_id}

- **Pipeline ID**: {inc_row[2]}
- **Correlation ID**: {inc_row[3]}
- **Status**: {inc_row[4]}
- **Classification**: {inc_row[5]}
- **Confidence Score**: {inc_row[6]}
- **Root Cause Node**: {inc_row[7]}
- **Selected Runbook**: {inc_row[8]}
- **Created At**: {inc_row[9]}

## Evidence Summary
Structured evidence logged in SQLite control database.
"""
        report_path = os.path.join(self.artifacts_dir, f"incident_{incident_id}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return report_path
