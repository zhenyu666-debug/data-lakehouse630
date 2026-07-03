import duckdb

con = duckdb.connect()

url = "https://blobs.duckdb.org/nl-railway/services-2024.csv.gz"

print("Testing DuckDB remote query (no local download)...")
print(f"URL: {url}\n")

# Get column names and sample
print("1. Schema (first 3 rows):")
result = con.execute(f"""
    SELECT * FROM read_csv_auto('{url}', compression='gzip', header=True) LIMIT 3
""").fetchall()
for r in result:
    print(" ", r)

# Count rows (streaming - won't load all into memory)
print("\n2. Row count (streaming scan):")
cnt = con.execute(f"""
    SELECT count(*) FROM read_csv_auto('{url}', compression='gzip', header=True)
""").fetchone()
print(f"   Total rows: {cnt[0]:,}")

print("\nDuckDB remote query SUCCESS - no local files needed!")
con.close()
