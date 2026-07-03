import pandas as pd
import psycopg2
from io import StringIO

# Load CSV
csv_path = "C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/data/raw/UserBehavior.csv"
print("Loading CSV...")
df = pd.read_csv(csv_path)
print(f"Rows: {len(df)}")

# Connect to postgres
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="iceberg_catalog",
    user="admin",
    password="password"
)
cur = conn.cursor()

# Create staging table
print("Creating staging table...")
cur.execute("""
DROP TABLE IF EXISTS staging_user_behavior;
CREATE TABLE staging_user_behavior (
    user_id BIGINT,
    item_id BIGINT,
    category_id BIGINT,
    behavior_type VARCHAR(20),
    ts BIGINT,
    event_time TIMESTAMP
)
""")

# Bulk copy using COPY
print("Bulk loading via COPY...")
buf = StringIO()
df.to_csv(buf, index=False, header=False)
buf.seek(0)
cur.copy_expert("COPY staging_user_behavior FROM STDIN WITH (FORMAT CSV)", buf)

conn.commit()
cur.execute("SELECT COUNT(*) FROM staging_user_behavior")
count = cur.fetchone()[0]
print(f"Loaded {count} rows")

# Also add to Iceberg via Trino
print("Done! Staging table ready.")
cur.close()
conn.close()
