# System Assumptions and Environmental Context

## Target Runtime & Connectors
- **Language**: Python 3.11+
- **Control Data Store**: SQLite (`data/control_plane.db`)
- **Data Adapters**: SQLite source (`data/source.db`) and target (`data/target.db`)
- **Graph Traversal**: NetworkX directed property graph
- **API Framework**: FastAPI / Uvicorn

## Assumptions
1. All ETL transformations and remediation operations are deterministic and do not require LLM inference during execution.
2. Source table contains `updated_at` timestamp and stable primary key for watermark tracking.
3. In local environment, low and medium risk runbooks execute automatically without human approval gate, while high risk runbooks require explicit approval.
