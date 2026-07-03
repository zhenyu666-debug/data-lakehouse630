import duckdb

BASE = "C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/duckdb_railway"
con = duckdb.connect(":memory:")
for y in [2019, 2024, 2025]:
    df = con.execute(
        "SELECT * FROM read_csv_auto(?, compression='gzip', header=true) LIMIT 1",
        [f"{BASE}/services-{y}.csv.gz"]
    ).fetchdf()
    print(f"{y}: {len(df.columns)} cols  -> {df.columns.tolist()}")
