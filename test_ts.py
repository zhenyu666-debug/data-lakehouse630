import duckdb
con = duckdb.connect(":memory:")
con.execute("CREATE VIEW ub AS SELECT * FROM read_csv_auto('C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/data/raw/UserBehavior.csv', header=true)")

# Try different timestamp approaches
tests = [
    "SELECT timestamp, timestamp::TIMESTAMP FROM ub LIMIT 3",
    "SELECT EPOCH_TO_TIMESTAMP(timestamp) FROM ub LIMIT 3",
    "SELECT TO_TIMESTAMP(timestamp) FROM ub LIMIT 3",
    "SELECT TRY_CAST(timestamp AS TIMESTAMP) FROM ub LIMIT 3",
    "SELECT STRPTIME(timestamp::VARCHAR, '%s') FROM ub LIMIT 3",
]
for t in tests:
    try:
        df = con.execute(t).fetchdf()
        print(f"OK: {t[:60]}\n{df}\n")
    except Exception as e:
        print(f"FAIL: {t[:60]} -> {e}\n")
