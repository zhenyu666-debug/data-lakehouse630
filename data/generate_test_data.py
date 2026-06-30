#!/usr/bin/env python3
"""
生成模拟淘宝用户行为数据集（用于本地测试）
保留与原始 UserBehavior.csv 完全一致的格式。
数据范围：2027-11-25 到 2027-12-03，共 9 天。
"""

import csv
import random
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 配置 ────────────────────────────────────────────────────────────────────
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "UserBehavior.csv"
NUM_USERS = 10_000          # 模拟 1 万用户（原始约 100 万）
NUM_ITEMS = 50_000          # 模拟 5 万商品（原始约 400 万）
NUM_CATEGORIES = 1_000      # 模拟 1000 个类目
RECORDS_PER_USER = 100      # 每个用户约 100 条行为
START_DATE = datetime(2017, 11, 25, 0, 0, 0, tzinfo=timezone(timedelta(hours=8)))  # 北京时间
END_DATE   = datetime(2017, 12, 3, 23, 59, 59, tzinfo=timezone(timedelta(hours=8)))

# 行为类型权重（接近真实分布）
BEHAVIOR_WEIGHTS = {
    "pv":  88.4,   # 点击
    "fav":  4.6,   # 收藏
    "cart": 4.4,   # 加购
    "buy":  2.6,   # 购买
}
BEHAVIOR_TYPES = list(BEHAVIOR_WEIGHTS.keys())
BEHAVIOR_CUMULATIVE = []
total = 0
for bt in BEHAVIOR_TYPES:
    total += BEHAVIOR_WEIGHTS[bt]
    BEHAVIOR_CUMULATIVE.append(total)


def pick_behavior() -> str:
    r = random.uniform(0, 100)
    for i, threshold in enumerate(BEHAVIOR_CUMULATIVE):
        if r < threshold:
            return BEHAVIOR_TYPES[i]
    return BEHAVIOR_TYPES[-1]


def unix_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def generate_records():
    """生成用户行为记录"""
    total_range = END_DATE - START_DATE
    total_seconds = total_range.total_seconds()

    records = []

    for user_id in range(1, NUM_USERS + 1):
        num_records = int(random.gauss(RECORDS_PER_USER, 30))
        num_records = max(5, min(num_records, 500))

        # 随机生成行为时间
        offsets = sorted(random.sample(
            range(int(total_seconds)), num_records
        ))

        for offset in offsets:
            event_time = START_DATE + timedelta(seconds=offset)
            ts = unix_timestamp(event_time)

            record = {
                "user_id": user_id,
                "item_id": random.randint(1, NUM_ITEMS),
                "category_id": random.randint(1, NUM_CATEGORIES),
                "behavior_type": pick_behavior(),
                "timestamp": ts,
            }
            records.append(record)

        if user_id % 1000 == 0:
            print(f"已生成 {user_id}/{NUM_USERS} 用户的行为记录...")

    return records


def write_csv(records):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"写入 CSV: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "item_id", "category_id", "behavior_type", "timestamp"])
        for r in records:
            writer.writerow([
                r["user_id"],
                r["item_id"],
                r["category_id"],
                r["behavior_type"],
                r["timestamp"],
            ])

    print(f"写入完成: {len(records):,} 条记录")
    print(f"文件大小: {OUTPUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")


def main():
    print("=" * 60)
    print("生成模拟淘宝用户行为数据集")
    print(f"用户数: {NUM_USERS:,} | 商品数: {NUM_ITEMS:,} | 类目数: {NUM_CATEGORIES}")
    print(f"时间范围: {START_DATE.date()} ~ {END_DATE.date()}")
    print("=" * 60)

    t0 = time.time()
    records = generate_records()
    write_csv(records)

    print(f"总耗时: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
