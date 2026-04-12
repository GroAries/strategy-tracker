"""
Global Macro Filter v1.0 (全球宏观联动过滤器)
================================================
基于第一性原理与控制论设计，用于在策略共振前评估宏观环境风险。
核心理念：宏观环境是“天气”，策略是“种子”。暴雨天不宜播种。
"""

class GlobalMacroFilter:
    def __init__(self):
        # 2026 Trump 2.0 时代的基准阈值
        self.thresholds = {
            'us_10y_yield': {'safe': 3.5, 'danger': 4.5},
            'usd_index': {'safe': 100, 'danger': 105},
            'gold_price': {'safe': 2500, 'danger': 3000}, # 黄金过高意味着信用危机/避险
            'vix': {'safe': 15, 'danger': 25},
        }

    def evaluate(self, us_10y: float, vix: float, geopolitical: str = 'NEUTRAL'):
        """
        评估当前宏观环境，返回风险等级和仓位上限。
        
        :param us_10y: 美国 10 年期国债收益率
        :param vix: 恐慌指数 (或替代指标如日韩跌幅/日元暴涨)
        :param geopolitical: 地缘状态 ('PEACE', 'NEUTRAL', 'WAR')
        :return: dict (regime, max_position, advice)
        """
        score = 0
        advice = []

        # 1. 美债收益率 (流动性水龙头)
        if us_10y >= self.thresholds['us_10y_yield']['danger']:
            score -= 40
            advice.append("流动性收紧，严控高估值")
        elif us_10y >= self.thresholds['us_10y_yield']['safe']:
            score -= 10
            advice.append("流动性中性，关注业绩")
        else:
            score += 20
            advice.append("流动性宽松，利好成长")

        # 2. 恐慌指数 VIX (全球避险情绪)
        if vix >= self.thresholds['vix']['danger']:
            score -= 40
            advice.append("极度恐慌，现金为王")
        elif vix >= self.thresholds['vix']['safe']:
            score -= 10
        else:
            score += 10

        # 3. 地缘政治 (黑天鹅)
        if geopolitical == 'WAR':
            score -= 50
            advice.append("战争避险，关注军工/航运/黄金")
        elif geopolitical == 'PEACE':
            score += 20
            advice.append("风险偏好上升，进攻为主")

        # 最终定级
        regime = 'NORMAL'
        max_position = 0.7 # 默认保守仓位

        if score >= 30:
            regime = 'RISK_ON'
            max_position = 1.0
        elif score <= -30:
            regime = 'RISK_OFF'
            max_position = 0.3
        else:
            regime = 'NEUTRAL'
            max_position = 0.6

        return {
            'regime': regime,
            'score': score,
            'max_position': max_position,
            'advice': advice
        }
