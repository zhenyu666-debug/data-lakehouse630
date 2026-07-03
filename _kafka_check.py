"""Helper to inspect Kafka topics and offsets via kafka-console tools inside container."""
import json, subprocess, sys

DOCKER = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"

def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.stdout, p.stderr, p.returncode

def list_topics():
    out, err, rc = sh([DOCKER, "exec", "kafka", "bash", "-c",
        "kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null"])
    return [t.strip() for t in out.splitlines() if t.strip()]

def get_offsets(topic):
    out, err, rc = sh([DOCKER, "exec", "kafka", "bash", "-c",
        f"kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic {topic} 2>/dev/null"])
    total = 0
    parts = []
    for line in out.splitlines():
        # format: topic:partition:offset
        if not line.strip(): continue
        parts = line.split(":")
        if len(parts) >= 3:
            try: total += int(parts[-1])
            except: pass
    return total, out

if __name__ == "__main__":
    topics = list_topics()
    print("topics:", topics)
    for t in topics:
        n, raw = get_offsets(t)
        print(f"\n=== {t} ===")
        print(f"total messages approx: {n}")
        print(raw)
