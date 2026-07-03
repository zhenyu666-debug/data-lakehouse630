"""Quick data sanity check via Trino REST API."""
import json
import time
import urllib.request
import urllib.error

TRINO_URL = "http://localhost:8080"


def _exec_in_trino(sql: str, user: str = "trino", timeout: float = 15.0):
    req = urllib.request.Request(
        f"{TRINO_URL}/v1/statement",
        data=json.dumps({"statement": sql}).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Trino-User": user},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _poll(next_uri: str, user: str = "trino", max_wait: float = 90.0):
    deadline = time.time() + max_wait
    while time.time() < deadline:
        req = urllib.request.Request(
            next_uri, headers={"X-Trino-User": user}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            obj = json.loads(r.read())
        state = obj.get("stats", {}).get("state", "UNKNOWN")
        if state in ("FINISHED", "FAILED", "FINISHING"):
            return obj
        time.sleep(1.5)
    return {"error": {"message": "poll timeout"}}


def count(table: str):
    sql = f"SELECT COUNT(*) AS n FROM iceberg_catalog.default.{table}"
    print(f"\n=== {table} ===")
    print(f"SQL: {sql}")
    try:
        init = _exec_in_trino(sql)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body[:400]}")
        return None
    except Exception as e:
        print(f"INIT error: {e!r}")
        return None
    print(f"INIT: {init.get('stats', {}).get('state', '?')}")
    nxt = init.get("nextUri")
    if not nxt:
        # maybe error in initial response
        print(json.dumps(init, ensure_ascii=False)[:500])
        return None
    final = _poll(nxt, max_wait=60.0)
    state = final.get("stats", {}).get("state", "?")
    print(f"FINAL state: {state}")
    err = final.get("error")
    if err:
        print(f"ERROR: {err.get('message', '')[:400]}")
        return None
    data = final.get("data") or []
    columns = [c["name"] for c in final.get("columns", [])]
    print(f"columns={columns} rows={data}")
    if data and columns:
        return data[0][0]
    return 0


if __name__ == "__main__":
    out = {}
    for t in ("user_behavior_dwd", "user_behavior_pvuv_1m", "item_hot_1h"):
        out[t] = count(t)
    print("\n=== Summary ===")
    print(json.dumps(out, ensure_ascii=False, indent=2))
