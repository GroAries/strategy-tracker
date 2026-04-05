---
name: strategy_tracker
description: 交易策略绩效追踪与对比系统 - 自动化回测多策略，生成横向对比看板，辅助策略优选与参数调优。
---

# 策略绩效追踪看板 (Strategy Tracker)

基于控制论负反馈原理构建的策略评估系统。

## 核心功能

1. **多策略公平对比**: 在相同市场数据、资金、滑点设置下运行不同策略。
2. **核心指标计算**: 总收益率、最大回撤、夏普比率、胜率、盈亏比。
3. **可视化报告**: 生成 HTML 对比看板，包含资金曲线叠加图。
4. **策略优选建议**: 基于数据自动给出配置建议（如“当前震荡市建议用 CATS-A"）。

## 使用方式

### Python API

```python
from strategy_tracker import StrategyTracker

tracker = StrategyTracker()

# 添加要测试的策略
tracker.add_strategy("CATS-A", "cats_a")
tracker.add_strategy("Oracle", "oracle_v2")

# 运行回测 (默认最近 6 个月)
report = tracker.run_comparison(
    symbols=['600519', '000001', '300750'], # 测试标的
    start_date='20251001',
    end_date='20260401',
    initial_capital=100000
)

# 查看 HTML 报告
tracker.export_html(report, "comparison_report.html")
```

## 包含的策略适配器

目前支持以下内置策略的自动对接：
- `cats_a`: CATS-A 全天候策略
- `oracle`: Oracle 动态动量策略
- `naked_k`: 裸 K 策略 (需配合特定信号模式)

## 为什么要用它？

- **拒绝幸存者偏差**: 不仅看赚了多少，更看亏了多少（最大回撤）。
- **环境适应性分析**: 发现哪个策略在什么行情下表现最好。
- **参数寻优**: 配合不同参数运行，找到最优解。
