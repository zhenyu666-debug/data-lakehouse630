"""
Dutch Railway Data Downloader  v2 - robust single-stream with retries
Source: https://blobs.duckdb.org/nl-railway/
"""
import requests, os, time, sys

OUT = r"C:\Users\Hasee\.qclaw\workspace\get_jobs\data-lakehouse\duckdb_railway"
os.makedirs(OUT, exist_ok=True)

FILES = [
    ("services-2019.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2019.csv.gz", 348_000_000),
    ("services-2020.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2020.csv.gz", 355_000_000),
    ("services-2021.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2021.csv.gz", 350_000_000),
    ("services-2022.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2022.csv.gz", 356_000_000),
    ("services-2023.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2023.csv.gz", 346_000_000),
    ("services-2024.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2024.csv.gz", 357_000_000),
    ("services-2025.csv.gz", "https://blobs.duckdb.org/nl-railway/services-2025.csv.gz", 396_000_000),
]
TOTAL = sum(f[2] for f in FILES)
T0 = time.time()
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RailDownloader/1.0)"})

def fmt(b):
    if b >= 1e9: return f"{b/1e9:.2f}GB"
    if b >= 1e6: return f"{b/1e6:.0f}MB"
    return f"{b/1e3:.0f}KB"

def progress(name, done, total):
    pct = done/total*100 if total else 0
    elapsed = time.time()-T0
    speed = done/elapsed if elapsed > 0 else 0
    bar = "#" * int(pct/5)
    rem = (total-done)/(speed+0.01)
    sys.stdout.write(f"\r{name:<28} {pct:5.1f}% {fmt(done)}/{fmt(total)} ETA={rem/60:.0f}min    \r")
    sys.stdout.flush()

for fname, url, expected in FILES:
    fpath = os.path.join(OUT, fname)
    existing = os.path.getsize(fpath) if os.path.exists(fpath) else 0

    if existing >= expected * 0.95:
        print(f"SKIP {fname} ({fmt(existing)} already complete)")
        continue

    print(f"\nDOWN {fname}  ({fmt(existing)} already have)")

    for attempt in range(5):
        try:
            t0 = time.time()
            r = session.get(url, stream=True, timeout=(20, 600))
            r.raise_for_status()
            total_sz = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            with open(fpath, "ab" if existing > 0 else "wb") as f:
                if existing > 0:
                    f.seek(0, 2)  # append
                for chunk in r.iter_content(chunk_size=256*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress(fname, existing+downloaded, total_sz or expected)
            print()
            sz = os.path.getsize(fpath)
            elapsed = time.time()-t0
            print(f"OK   {fname}  {fmt(sz)}  {fmt(sz/elapsed)}/s")
            break
        except Exception as e:
            print(f"\nERR  attempt {attempt+1}: {type(e).__name__} {str(e)[:80]}")
            if attempt < 4:
                wait = (attempt+1)*15
                print(f"     retrying in {wait}s ...")
                time.sleep(wait)
            else:
                print(f"FAIL  {fname}  -- giving up after 5 attempts")

elapsed = time.time()-T0
total_sz = sum(os.path.getsize(os.path.join(OUT, f[0]))
               for f in FILES if os.path.exists(os.path.join(OUT, f[0])))
print(f"\n{'='*60}")
print(f"Finished in {elapsed/60:.1f}min")
print(f"Total: {fmt(total_sz)}  ({len([f for f in FILES if os.path.exists(os.path.join(OUT, f[0]))])}/{len(FILES)} files)")
