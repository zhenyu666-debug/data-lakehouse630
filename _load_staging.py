import pandas as pd
import psycopg2
from io import StringIO

csv_path = "C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/data/raw/UserBehavior.csv"
print(f"Loading CSV: {csv_path}")
df = pd.read_csv(csv_path, dtype=str)
print(f"Rows: {len(df)}, Cols: {list(df.columns)}")

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="iceberg_catalog", user="admin", password="password"
)
conn.autocommit = True
cur = conn.cursor()

# Create staging table (only 5 cols from CSV, event_time added after COPY)
print("Creating staging table (5 cols)...")
cur.execute("""
DROP TABLE IF EXISTS staging_user_behavior;
CREATE TABLE staging_user_behavior (
    user_id BIGINT,
    item_id BIGINT,
    category_id BIGINT,
    behavior_type VARCHAR(20),
    ts BIGINT
);
CREATE INDEX ON staging_user_behavior(ts);
""")

# Bulk copy using COPY (only 5 columns from CSV)
print("Bulk loading via COPY...")
buf = StringIO()
df.columns = ['user_id', 'item_id', 'category_id', 'behavior_type', 'ts']
df.to_csv(buf, index=False, header=False)
buf.seek(0)
cur.copy_expert(
    "COPY staging_user_behavior(user_id,item_id,category_id,behavior_type,ts) FROM STDIN WITH (FORMAT CSV)",
    buf
)

cur.execute("SELECT COUNT(*) FROM staging_user_behavior")
count = cur.fetchone()[0]
print(f"Loaded {count} rows into PostgreSQL!")

# Add event_time column
print("Adding event_time column...")
cur.execute("ALTER TABLE staging_user_behavior ADD COLUMN event_time TIMESTAMP;")

# Fill event_time from ts
print("Computing event_time from ts...")
cur.execute("""
UPDATE staging_user_behavior
SET event_time = TO_TIMESTAMP(ts)
WHERE ts > 0;
""")
cur.execute("SELECT COUNT(*) FROM staging_user_behavior WHERE event_time IS NOT NULL")
count_valid = cur.fetchone()[0]
print(f"Rows with event_time: {count_valid}")

cur.close()
conn.close()
print("Done!")
