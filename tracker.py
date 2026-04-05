import sys
import os
import pandas as pd
import numpy as np
import json
import importlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable

class StrategyTracker:
    """
    策略绩效追踪器 - 裁判员 (真实数据版 + ECharts 可视化)
    """
    
    def __init__(self, initial_capital=100000, commission_rate=0.0003, slippage=0.001):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate  # A 股一般万三
        self.slippage = slippage                # 滑点千分之一
        self.strategies = {}
        
    def add_strategy(self, name: str, signal_func: Callable):
        """
        添加策略。
        signal_func: 接收 DataFrame，返回与 df 等长的信号列表 (1=Buy, -1=Sell, 0=Hold)
        """
        self.strategies[name] = signal_func

    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取真实 A 股数据。
        优先尝试使用 copaw-stock-data-api，失败则使用 akshare。
        """
        print(f"📡 正在获取数据：{symbol} ({start_date} - {end_date}) ...")
        
        # 1. 尝试本地 API
        try:
            local_api_path = os.path.join(os.path.dirname(__file__), '..', 'copaw-stock-data-api')
            sys.path.insert(0, local_api_path)
            from stock_data_api import StockAPI 
            api = StockAPI()
            df = api.get_daily_k(symbol, start_date, end_date)
            if df is not None and not df.empty:
                print("✅ 使用本地 API (stock_data_api) 获取数据成功")
                return df
        except Exception as e:
            print(f"⚠️ 本地 API 获取失败: {e}")
            
        # 2. 降级使用 akshare
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if df is not None and not df.empty:
                df.rename(columns={'日期': 'Date', '开盘': 'Open', '收盘': 'Close', '最高': 'High', '最低': 'Low', '成交量': 'Volume'}, inplace=True)
                print("✅ 使用 Akshare 获取数据成功")
                return df
        except Exception as e:
            print(f"❌ Akshare 获取失败: {e}")
            
        return None

    def run_backtest(self, strategy_name: str, df: pd.DataFrame) -> Dict:
        """
        运行单个策略的回测模拟。
        """
        print(f"⚙️ 运行策略回测：{strategy_name} ...")
        
        if strategy_name not in self.strategies:
            raise ValueError(f"策略 {strategy_name} 未注册")
            
        signal_func = self.strategies[strategy_name]
        signals = signal_func(df)
        
        if len(signals) != len(df):
            raise ValueError(f"策略返回的信号数量 ({len(signals)}) 与数据长度 ({len(df)}) 不匹配")
            
        equity_curve = []
        current_capital = self.initial_capital
        position = 0 # 持股数量
        entry_price = 0
        
        curve_data = []
        
        for i, row in df.iterrows():
            price = row['Close']
            signal = signals[i]
            date_str = row['Date'] if isinstance(row['Date'], str) else row['Date'].strftime('%Y-%m-%d')
            
            # 交易逻辑
            if signal == 1 and position == 0: # 买入
                # 全仓买入
                cost = price * (1 + self.slippage) * (1 + self.commission_rate)
                # 计算能买多少股 (100 整数倍)
                shares = int((current_capital / cost) // 100) * 100
                if shares > 0:
                    position = shares
                    entry_price = price
                    current_capital -= shares * cost
                    # print(f"  [{date_str}] 买入 @ {price}, 数量 {shares}")
            
            elif signal == -1 and position > 0: # 卖出
                revenue = price * (1 - self.slippage) * (1 - self.commission_rate)
                current_capital += position * revenue
                # print(f"  [{date_str}] 卖出 @ {price}, 数量 {position}")
                position = 0
                entry_price = 0
            
            # 每日资产 = 现金 + 持股市值
            total_asset = current_capital + (position * price)
            equity_curve.append(total_asset)
            
            curve_data.append({
                'date': date_str,
                'value': round(total_asset, 2),
                'price': price
            })
            
        return {
            'strategy_name': strategy_name,
            'curve': curve_data,
            'final_equity': equity_curve[-1],
            'initial_equity': self.initial_capital
        }

    def calculate_metrics(self, result: Dict) -> Dict:
        """计算绩效指标"""
        curve = result['curve']
        if not curve:
            return {}
            
        values = [d['value'] for d in curve]
        initial = values[0]
        final = values[-1]
        
        total_return = (final - initial) / initial * 100
        
        # 最大回撤
        max_dd = 0
        peak = initial
        for val in values:
            if val > peak: peak = val
            dd = (peak - val) / peak
            if dd > max_dd: max_dd = dd
            
        # 夏普比率 (简化计算)
        returns = np.diff(values) / values[:-1]
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
        else:
            sharpe = 0
            
        return {
            'total_return': total_return,
            'max_drawdown': max_dd * 100,
            'sharpe': sharpe
        }

    def generate_report(self, results: List[Dict], symbol: str):
        """生成带有 ECharts 的 HTML 报告"""
        
        # 准备 ECharts 数据
        series_data = []
        dates = []
        
        for res in results:
            curve = res['curve']
            series_data.append({
                'name': res['strategy_name'],
                'type': 'line',
                'data': [d['value'] for d in curve],
                'smooth': True,
                'showSymbol': False
            })
            if not dates:
                dates = [d['date'] for d in curve]

        # 计算指标
        metrics_table = []
        for res in results:
            m = self.calculate_metrics(res)
            metrics_table.append({
                'name': res['strategy_name'],
                'return': f"{m['total_return']:.2f}%",
                'drawdown': f"{m['max_drawdown']:.2f}%",
                'sharpe': f"{m['sharpe']:.2f}"
            })

        # 排序推荐
        best = max(results, key=lambda x: self.calculate_metrics(x)['total_return'])
        
        echarts_series = json.dumps(series_data, ensure_ascii=False)
        echarts_x_axis = json.dumps(dates, ensure_ascii=False)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>策略绩效对比 - {symbol}</title>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
                h1 {{ text-align: center; color: #2c3e50; margin-bottom: 5px; }}
                .subtitle {{ text-align: center; color: #7f8c8d; margin-bottom: 30px; font-size: 0.9em; }}
                #chart {{ width: 100%; height: 400px; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95em; }}
                th {{ background: #ecf0f1; padding: 12px; text-align: center; border-bottom: 2px solid #bdc3c7; }}
                td {{ padding: 10px; text-align: center; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
                .ret-good {{ color: #e74c3c; font-weight: bold; }}
                .ret-bad {{ color: #2ecc71; font-weight: bold; }}
                .rec-box {{ background: #e8f8f5; border-left: 5px solid #1abc9c; padding: 15px; margin-top: 20px; border-radius: 4px; }}
                .footer {{ text-align: center; margin-top: 40px; color: #95a5a6; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 策略绩效追踪看板</h1>
                <p class="subtitle">测试标的：{symbol} | 初始资金：{self.initial_capital:,.0f} 元</p>
                
                <div id="chart"></div>
                
                <h2>📈 核心指标对比</h2>
                <table>
                    <tr>
                        <th>策略名称</th>
                        <th>总收益率</th>
                        <th>最大回撤</th>
                        <th>夏普比率</th>
                    </tr>
                    {''.join([f'<tr><td><b>{m["name"]}</b></td><td class="{"ret-good" if float(m["return"].strip("%")) > 0 else "ret-bad"}">{m["return"]}</td><td>{m["drawdown"]}</td><td>{m["sharpe"]}</td></tr>' for m in metrics_table])}
                </table>
                
                <div class="rec-box">
                    💡 <b>系统建议</b>: 根据历史回测，<b>{best['strategy_name']}</b> 实现了最高的总收益率。
                    <br>但在实际决策中，请结合当前的市场波动率（如 VIX 或 ATR）进行综合判断。
                    高回撤策略在震荡市中可能面临较大压力。
                </div>
                
                <div class="footer">
                    Generated by Strategy Tracker v1.0 | Powered by Control Loop
                </div>
            </div>
            
            <script>
                var chart = echarts.init(document.getElementById('chart'));
                var option = {{
                    tooltip: {{ trigger: 'axis' }},
                    legend: {{ data: {json.dumps([r['strategy_name'] for r in results], ensure_ascii=False)} }},
                    grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
                    xAxis: {{
                        type: 'category',
                        boundaryGap: false,
                        data: {echarts_x_axis}
                    }},
                    yAxis: {{
                        type: 'value',
                        name: '资产净值 (元)'
                    }},
                    series: {echarts_series}
                }};
                chart.setOption(option);
            </script>
        </body>
        </html>
        """
        return html
