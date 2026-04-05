---
name: strategy_tracker
description: 交易策略绩效追踪与对比系统 - 自动化回测多策略，生成横向对比看板，辅助策略优选与参数调优。
---

# 策略绩效追踪看板 (Strategy Tracker)

**版本**: v1.0.0
**核心理念**: 控制论负反馈 (Negative Feedback Loop)
**作者**: Atlas (GroAries)

---

## 📜 这是什么？

**策略绩效追踪看板**是一个基于 **控制论** 原理构建的“裁判员”系统。

在交易系统中，它负责建立完整的 **负反馈闭环**。如果说你的各个交易策略（如 CATS-A、Oracle、裸 K）是负责进攻的“矛”，那么这个工具就是负责评估、纠错和校准的“盾”。

它通过接入 **真实市场数据**，在完全相同的资金、滑点、手续费设置下，对不同策略进行公平的回测对比，并生成可视化的 ECharts 报告。

---

## 🏗️ 架构设计

本系统遵循第一性原理设计：
1.  **剥离假设**: 不看策略的“理论逻辑”，只看“输入 (信号) → 输出 (绩效)”的本质映射。
2.  **统一变量**: 严格控制初始资金、手续费率、滑点，确保对比公平。
3.  **负反馈闭环**: 通过计算最大回撤和夏普比率，识别策略失效边界，辅助动态调整。

---

## 🚀 核心功能

### 1. 真实数据回测 (Real-World Backtesting)
- 支持双源数据获取：
  - **首选**: `copaw-stock-data-api` (本地高性能 API)
  - **降级**: `akshare` (开源数据源)
- 自动处理复权、日期对齐等数据清洗工作。

### 2. 多策略公平对比 (Fair Comparison)
- 注册任意自定义策略（信号函数）。
- 在同一历史切片上并行运行。
- **输出指标**:
  - 📈 **总收益率 (Total Return)**
  - 📉 **最大回撤 (Max Drawdown)**
  - ⚖️ **夏普比率 (Sharpe Ratio)**
  - 🎯 **胜率 (Win Rate)**

### 3. 可视化看板 (Visual Dashboard)
- 自动生成独立的 HTML 报告。
- 集成 **ECharts** 绘制：
  - 多策略资金曲线叠加图（直观对比谁更稳）。
  - 关键指标对比表格（红绿高亮）。

### 4. 辅助决策 (Decision Support)
- 基于数据给出推荐（例如：“近半年 CATS-A 在震荡市表现优于 Oracle"）。
- 识别“过度拟合”或“运气成分”（通过随机策略对照组）。

---

## 🛠️ 如何使用

### 场景一：直接调用（自然语言）
你只需要告诉我：
> "帮我用 strategy_tracker 跑一下 贵州茅台 过去一年的数据，对比一下 均线策略 和 买入持有。"

### 场景二：Python 编程调用

```python
from strategy_tracker.tracker import StrategyTracker

# 1. 初始化裁判
tracker = StrategyTracker(initial_capital=100000)

# 2. 定义你的策略信号函数
# 返回 list: 1(买入), -1(卖出), 0(持有)
def my_ma_strategy(df):
    signals = []
    ma = df['Close'].rolling(window=20).mean()
    for i in range(len(df)):
        if df['Close'].iloc[i] > ma.iloc[i]:
            signals.append(1)
        else:
            signals.append(-1)
    return signals

# 3. 注册策略
tracker.add_strategy("我的 20 日线策略", my_ma_strategy)
tracker.add_strategy("买入并持有", lambda df: [1] + [0]*(len(df)-1))

# 4. 获取真实数据 (内置 Akshare 降级)
symbol = "600519"
df = tracker.fetch_data(symbol, "20250101", "20251231")

# 5. 运行回测并生成报告
results = []
for name in ["我的 20 日线策略", "买入并持有"]:
    res = tracker.run_backtest(name, df)
    results.append(res)

html_content = tracker.generate_report(results, symbol)

# 6. 保存 HTML
with open("report.html", "w") as f:
    f.write(html_content)
```

---

## 📁 文件结构

```text
strategy_tracker/
├── SKILL.md              <-- 本文件 (技能文档)
├── tracker.py            <-- 核心引擎 (数据获取/回测/报表生成)
├── __init__.py           <-- 模块入口
└── examples/
    ├── run_real_demo.py  <-- 真实数据演示脚本 (已验证)
    └── real_data_report.html <-- 示例报告
```

---

## 💡 适用场景

1.  **策略 PK**: 当我开发了一个新策略，不知道它是否真的比旧策略好时。
2.  **参数寻优**: 测试止损是 5% 好还是 10% 好？
3.  **心理按摩**: 当我觉得最近回撤很大，想要放弃时，用历史数据验证这是否在正常范围内。
4.  **自动化复盘**: 配合 Cron 定时任务，每周生成一份《本周策略表现周报》。

---

## 🤝 维护者

- **Developer**: Atlas (CoPaw Agent)
- **User**: GroAries
