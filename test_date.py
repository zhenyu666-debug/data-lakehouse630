import duckdb

BASE = "C:/Users/Hasee/.qclaw/workspace/get_jobs/data-lakehouse/duckdb_railway"
con = duckdb.connect(":memory:")

# Create view for 2024 only (faster test)
con.execute(f"""
    CREATE VIEW v2024 AS
    SELECT "Service:RDT-ID", "Service:Date", "Service:Type", "Service:Company",
           "Service:Train number", "Service:Completely cancelled", "Service:Partly cancelled",
           "Service:Maximum delay", "Stop:RDT-ID", "Stop:Station code", "Stop:Station name",
           "Stop:Arrival time", "Stop:Arrival delay", "Stop:Arrival cancelled",
           "Stop:Departure time", "Stop:Departure delay", "Stop:Departure cancelled"
    FROM read_csv_auto('{BASE}/services-2024.csv.gz', compression='gzip', header=true)
""")

# Test strftime on DATE
print("Testing strftime on DATE type:")
df = con.execute("""
    SELECT "Service:Date", strftime('%Y', "Service:Date") AS year
    FROM v2024 LIMIT 5
""").fetchdf()
print(df.to_string())

# Test CASE strftime weekday
print("\nTesting weekday extraction:")
df2 = con.execute("""
    SELECT
        strftime('%w', "Service:Date") AS w,
        CASE CAST(strftime('%w', "Service:Date") AS INT)
            WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday' END AS weekday_name
    FROM v2024 LIMIT 10
""").fetchdf()
print(df2.to_string())

con.close()
