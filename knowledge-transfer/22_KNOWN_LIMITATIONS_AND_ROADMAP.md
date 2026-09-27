# Known Limitations and Roadmap

## Confirmed Code Limitations
1. SQLite is used for local demo data plane; enterprise warehouses (Snowflake/BigQuery/PostgreSQL) require connector adapters.
2. High-risk destructive runbooks are disabled in production by policy.

## Recommended Next Increments
1. Add PostgreSQL/Cloud Data Warehouse adapters.
2. Add OpenLineage / dbt parser integrations.
