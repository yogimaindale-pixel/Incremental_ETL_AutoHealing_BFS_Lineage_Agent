# 02 Business Problem and Technical Value

## 1. Context & Business Problem
In modern enterprise data platforms, incremental ETL pipelines process millions of events per hour. When data pipelines fail due to transient network resets, late arriving source files, duplicate primary keys, or schema drift:
- Data engineering teams spend hours manually inspecting logs and SQL queries.
- Upstream root causes and downstream business dashboard impacts remain hidden without automated lineage mapping.
- Uncoordinated retries or manual patches risk data corruption, duplicate loads, or broken financial reports.

## 2. Technical Value Proposition
The **Incremental ETL Auto-Healing & BFS Data Lineage Agent** solves these challenges by providing:
1. **Deterministic Auto-Healing**: Zero-LLM error signature classification and automated allow-listed runbooks.
2. **BFS Lineage Traversal**: Cycle-safe Breadth-First Search (BFS) graph traversal to isolate upstream root causes and calculate downstream blast radius.
3. **Risk-Policy Governed Approvals**: Automated execution for low-risk actions and human sign-off gates for high-risk actions.
4. **Immutable Audit Plane**: Append-only state machine transitions logged in SQLite.

## 3. Operational KPIs
- **Detection-to-Classification Time**: < 100 milliseconds
- **Mean Time To Recovery (MTTR)**: Reduced from hours to < 10 seconds for auto-healed incidents
- **Auto-Heal Rate**: 80%+ of deterministic pipeline failures
- **False Remediation Count**: 0 (governed by idempotency keys and precheck validation)
