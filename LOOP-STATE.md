# LOOP-STATE.md - Data Lakehouse Setup

## Session: 2026-07-01 09:28

## Status: ✅ ALL COMPLETE

---

## Dataset 1: Dutch Railway ✅

**路径:** `duckdb_railway/`
**来源:** https://blobs.duckdb.org/nl-railway/ (DuckDB CDN)

| 文件 | 大小 | 行数 |
|------|------|------|
| services-2019-2025 × 7 | 2.51 GB | 152,176,324 行 |

### Schema（17 列）
每行 = 一个列车停靠站  
服务信息：列车号、公司(NS)、类型(Intercity/Sprinter)、取消状态  
停靠信息：站名、到站/出发时间、延误分钟数、取消状态  
时间范围：2019-01-01 ~ 2025-12-31（7年）

### SQL 分析结果（10 条查询）

| Query | 结论 |
|-------|------|
| Q1 年度数据量 | 2020 年最多（60,918 站/天），2023 年最少 |
| Q2 延误趋势 | 2019→2024 从 0.6min 升至 1.0min，COVID 期间最低 0.5min |
| Q3 公司对比 | NS (0.71min) 最准时；NS Int (5.04min) / Eurobahn (1.58min) 最延误 |
| Q4 列车类型 | 夜间/跨境列车延误率 15-24%；Sprinter/Stoptrein < 1% |
| Q5 取消率 | 2020 COVID 最高（7.5%）；2019 最低（2.16%）；2024 改善至 4.1% |
| Q6 延误车站 | Zell am See (62min)、Berlin Zoo (23min)、Bonn Hbf (11min) |
| Q7 延误日期 | 2023-11-02 (4.10min) — 可能暴风雪；11月下旬持续高延误 |
| Q8 时段 | 早高峰(7-9)最延误(0.96min)；晚高峰(17-19)最低(0.64min) |
| Q9 月度趋势 | 11月延误最高；COVID 2020-03~05 骤降 |
| Q10 工作日 | 工作日(0.77min)显著高于周末(0.58min) |

---

## Dataset 2: UserBehavior ✅

**路径:** `data/raw/UserBehavior.csv` (28MB, 997,413 行)  
淘宝用户行为数据（2017-11-24 ~ 2017-12-03）  
8 条 SQL 查询，4 秒完成

| 分析维度 | 结论 |
|---------|------|
| 行为漏斗 | pv 88.4% → fav 4.6% → cart 4.4% → buy 2.6% |
| 日转化率 | 稳定 2.85%~3.03% |
| 购买路径 | 88% pv→cart→buy；11% 只收藏不购买 |
| 用户分群 | VIP 47%；Active 23%；Warm 30% |
| 热门时段 | 18:00-19:00 购买量最高 |
| 热门类目 | TOP10 类目购买量差距极小（分布均匀）|

---

## Visualizations ✅ (NEW)

**输出目录:** `charts/` (9 个图表，0.93 MB)

| 图表 | 内容 |
|------|------|
| `01_yearly_delay.png` | 年度延误趋势 + 取消率（双 Y 轴）|
| `02_company_delay.png` | 各公司平均延误对比（TOP 12）|
| `03_monthly_heatmap.png` | 月度延误热力图（2019-2025）|
| `04_time_weekday.png` | 时段分析 + 工作日对比 |
| `05_monthly_cancel_delay.png` | 月度取消率 + 延误趋势（COVID 阴影）|
| `06_delay_distribution.png` | 延误分布直方图（对数刻度，采样 50 万）|
| `07_userbehavior_funnel.png` | 行为漏斗 + 日转化率 |
| `08_userbehavior_segments.png` | 用户分群饼图 + 购买路径条形图 |
| `09_userbehavior_hourly.png` | 小时行为曲线 + TOP10 类目 |

**脚本:** `viz_dashboard.py`  
**样式:** 深色主题（#1a1a2e 背景，霓虹配色）

---

## Scripts Summary

| 文件 | 说明 |
|------|------|
| `dl2.py` | 下载脚本 |
| `verify_railway.py` | DuckDB 完整性验证 |
| `duckdb_railway_analytics.py` | Q1-Q6 分析 |
| `duckdb_railway_q7_q10.py` | Q7-Q10 分析 |
| `viz_dashboard.py` | 9 个 Matplotlib 图表 |
| `test_ts.py` | DuckDB 时间函数测试 |

---

## Data Lakehouse: COMPLETE ✅
Dutch Railway (1.52 亿行) + UserBehavior (100 万行)  
全套 SQL 分析 + 可视化完成。
