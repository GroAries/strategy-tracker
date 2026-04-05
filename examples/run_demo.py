import sys
import os
# Fix path to parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker import StrategyTracker

def run_demo():
    """
    演示：对比 3 个策略在过去半年的表现
    """
    tracker = StrategyTracker()
    
    # 模拟数据
    mock_comparison = [
        {'name': 'CATS-A (全天候)', 'total_return': 12.45, 'max_drawdown': 4.20, 'sharpe': 2.15, 'win_rate': 58.5, 'dates': ['2025-10-01', '2026-04-01']},
        {'name': 'Oracle (动量)', 'total_return': 8.30, 'max_drawdown': 12.50, 'sharpe': 1.05, 'win_rate': 45.2, 'dates': ['2025-10-01', '2026-04-01']},
        {'name': '裸 K (形态)', 'total_return': 5.10, 'max_drawdown': 8.10, 'sharpe': 0.85, 'win_rate': 62.0, 'dates': ['2025-10-01', '2026-04-01']}
    ]
    
    print("📊 生成策略对比报告...")
    html = tracker.generate_report(mock_comparison, "沪深 300 样本池")
    
    out_path = os.path.join(os.path.dirname(__file__), "demo_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成：{out_path}")

if __name__ == "__main__":
    run_demo()
