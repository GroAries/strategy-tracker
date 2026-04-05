import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tracker import StrategyTracker

def demo_strategies(df: pd.DataFrame):
    """
    定义演示策略的信号生成函数
    """
    
    def buy_and_hold(df):
        """买入并持有"""
        return [1] + [0] * (len(df) - 1)
        
    def moving_average_cross(df, short=5, long=20):
        """简单的均线交叉策略"""
        signals = []
        ma_short = df['Close'].rolling(window=short).mean()
        ma_long = df['Close'].rolling(window=long).mean()
        
        for i in range(len(df)):
            if pd.isna(ma_short.iloc[i]) or pd.isna(ma_long.iloc[i]):
                signals.append(0)
                continue
            
            if ma_short.iloc[i] > ma_long.iloc[i]:
                signals.append(1) # Buy
            else:
                signals.append(-1) # Sell/Hold empty
        return signals

    def random_strategy(df):
        """随机交易 (噪音对照组)"""
        return np.random.choice([-1, 0, 1], size=len(df)).tolist()

    return {
        '买入并持有': buy_and_hold,
        '均线交叉 (5/20)': moving_average_cross,
        '随机交易': random_strategy
    }

def run_real_data_demo():
    print("🚀 开始接入真实数据演示...")
    
    tracker = StrategyTracker()
    
    # 1. 获取真实数据 (这里用 Akshare 兜底)
    symbol = '600519' # 贵州茅台
    df = tracker.fetch_data(symbol, '20250101', '20251231')
    
    if df is None:
        print("❌ 数据获取失败，无法演示。")
        return

    # 2. 注册策略
    strategies = demo_strategies(df)
    for name, func in strategies.items():
        tracker.add_strategy(name, func)
        
    # 3. 运行回测
    results = []
    for name in strategies.keys():
        res = tracker.run_backtest(name, df)
        results.append(res)
        
    # 4. 生成报告
    print("📝 正在生成 HTML 报告...")
    html = tracker.generate_report(results, symbol)
    
    out_path = os.path.join(os.path.dirname(__file__), "real_data_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成：{out_path}")

if __name__ == "__main__":
    run_real_data_demo()
