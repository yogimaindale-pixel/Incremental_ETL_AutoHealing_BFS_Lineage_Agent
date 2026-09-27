import sqlite3
from typing import Dict, Any

class MetricsCalculator:
    """Calculates operational metrics from control database."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    def get_summary_metrics(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM pipeline_run")
            total_runs = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM pipeline_run WHERE status = 'SUCCESS'")
            successful_runs = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM incident")
            total_incidents = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM incident WHERE status = 'RECOVERED'")
            healed_incidents = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM incident WHERE status = 'ESCALATED'")
            escalated_incidents = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM remediation_run WHERE status = 'ROLLED_BACK'")
            rollback_count = cursor.fetchone()[0] or 0

            auto_heal_rate = (healed_incidents / total_incidents * 100.0) if total_incidents > 0 else 100.0

            return {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "total_incidents": total_incidents,
                "healed_incidents": healed_incidents,
                "escalated_incidents": escalated_incidents,
                "rollback_count": rollback_count,
                "auto_heal_rate_percent": round(auto_heal_rate, 2),
            }
        except Exception:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "total_incidents": 0,
                "healed_incidents": 0,
                "escalated_incidents": 0,
                "rollback_count": 0,
                "auto_heal_rate_percent": 100.0,
            }
        finally:
            conn.close()
