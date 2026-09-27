import os
import sqlite3
from datetime import datetime, timedelta

def seed():
    os.makedirs("data", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)

    # 1. Control Plane DB
    control_db = "data/control_plane.db"
    conn_c = sqlite3.connect(control_db)
    with open("sql/control_schema.sql", "r", encoding="utf-8") as f:
        conn_c.executescript(f.read())

    # Seed pipeline definitions
    cursor_c = conn_c.cursor()
    cursor_c.execute(
        """
        INSERT INTO pipeline_definition (pipeline_id, name, source_table, target_table, watermark_column, lookback_minutes, batch_size)
        VALUES ('pipe_orders_incremental', 'Incremental Orders Loader', 'source_orders', 'fact_orders', 'updated_at', 60, 1000)
        ON CONFLICT(pipeline_id) DO NOTHING
        """
    )
    cursor_c.execute(
        """
        INSERT INTO pipeline_definition (pipeline_id, name, source_table, target_table, watermark_column, lookback_minutes, batch_size)
        VALUES ('pipe_customers_incremental', 'Incremental Customers Loader', 'source_customers', 'dim_customers', 'updated_at', 120, 500)
        ON CONFLICT(pipeline_id) DO NOTHING
        """
    )

    # Seed initial watermark
    initial_wm = (datetime.utcnow() - timedelta(days=1)).isoformat()
    cursor_c.execute(
        """
        INSERT INTO watermark_state (pipeline_id, last_watermark, batch_id)
        VALUES ('pipe_orders_incremental', ?, 'batch_init_001')
        ON CONFLICT(pipeline_id) DO NOTHING
        """,
        (initial_wm,)
    )
    conn_c.commit()
    conn_c.close()

    # 2. Source DB
    source_db = "data/source.db"
    conn_s = sqlite3.connect(source_db)
    with open("sql/sample_source.sql", "r", encoding="utf-8") as f:
        conn_s.executescript(f.read())

    cursor_s = conn_s.cursor()
    # Insert sample orders
    now = datetime.utcnow()
    orders = [
        (101, 1, 150.50, 'COMPLETED', (now - timedelta(hours=2)).isoformat()),
        (102, 2, 89.99, 'PENDING', (now - timedelta(hours=1)).isoformat()),
        (103, 1, 220.00, 'COMPLETED', now.isoformat()),
    ]
    cursor_s.executemany("INSERT OR REPLACE INTO source_orders VALUES (?, ?, ?, ?, ?)", orders)

    # Insert sample customers
    customers = [
        (1, 'Alice Smith', 'alice@example.com', 'US', (now - timedelta(hours=5)).isoformat()),
        (2, 'Bob Jones', 'bob@example.com', 'CA', (now - timedelta(hours=3)).isoformat()),
    ]
    cursor_s.executemany("INSERT OR REPLACE INTO source_customers VALUES (?, ?, ?, ?, ?)", customers)

    conn_s.commit()
    conn_s.close()

    # 3. Target DB
    target_db = "data/target.db"
    conn_t = sqlite3.connect(target_db)
    with open("sql/sample_target.sql", "r", encoding="utf-8") as f:
        conn_t.executescript(f.read())
    conn_t.commit()
    conn_t.close()

    print("Demo data seeded successfully.")

if __name__ == "__main__":
    seed()
