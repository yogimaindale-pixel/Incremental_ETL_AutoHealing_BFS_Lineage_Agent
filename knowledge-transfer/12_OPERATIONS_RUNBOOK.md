# 12 Operations Runbook

## 1. Daily Operations Checklist
1. **Health Check**: Run `curl http://localhost:8000/health` or `python3 run_demo.py --etl-only`.
2. **Review Incidents**: Inspect `data/control_plane.db` table `incident` for status `ESCALATED` or `AWAITING_APPROVAL`.
3. **Approval Queue**: Approve pending incidents via API `POST /incidents/{incident_id}/approve`.
4. **Audit Validation**: Check table `audit_event` for transition records.
