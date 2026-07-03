"""Write PostgreSQL staging data to Iceberg via REST API using pyiceberg + PyArrow."""
import psycopg2
import pyarrow as pa
from pyiceberg.catalog import load_catalog

# 1. Connect to PostgreSQL
print("Connecting to PostgreSQL...")
conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="iceberg_catalog", user="admin", password="password"
)
conn.autocommit = True
cur = conn.cursor()

# 2. Load Iceberg catalog via REST
print("Loading Iceberg catalog...")
catalog = load_catalog(
    "iceberg-rest",
    **{
        "type": "rest",
        "uri": "http://localhost:8181",
        "warehouse": "s3://warehouse",
        "s3.access-key-id": "admin",
        "s3.secret-access-key": "password",
        "s3.endpoint": "http://localhost:9000",
        "s3.path-style-access": "true",
    }
)

# 3. Get the table
tbl = catalog.load_table("lake.user_behavior_dwd")

# 4. Read from PostgreSQL in batches and write to Iceberg
BATCH = 10000
offset = 0
total_written = 0

print("Reading PostgreSQL and writing to Iceberg...")
while True:
    cur.execute("""
        SELECT user_id, item_id, category_id, behavior_type, ts, event_time
        FROM staging_user_behavior
        WHERE behavior_type IN ('pv', 'buy', 'cart', 'fav')
          AND user_id > 0 AND item_id > 0 AND category_id > 0 AND ts > 0
          AND event_time IS NOT NULL
        ORDER BY ts
        LIMIT %s OFFSET %s
    """, (BATCH, offset))
    rows = cur.fetchall()
    if not rows:
        break

    user_ids = [r[0] for r in rows]
    item_ids = [r[1] for r in rows]
    category_ids = [r[2] for r in rows]
    behaviors = [r[3] for r in rows]
    tss = [r[4] for r in rows]
    event_times = [r[5] for r in rows]
    pts = [(r[5].strftime("%Y-%m-%d") if r[5] else None) for r in rows]

    # Build PyArrow Table
    table = pa.table({
        "user_id": user_ids,
        "item_id": item_ids,
        "category_id": category_ids,
        "behavior_type": behaviors,
        "event_time": event_times,
        "pt": pts,
    })

    # Write batch to Iceberg
    tbl.append(table)
    total_written += len(rows)
    print(f"  Wrote batch: offset={offset}, size={len(rows)}, total={total_written}")
    offset += BATCH

    if len(rows) < BATCH:
        break

cur.close()
conn.close()
print(f"\nDone! Total rows written: {total_written}")
