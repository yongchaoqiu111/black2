import math
from datetime import datetime, timezone
from .models import ReputationData, RiskLevel

class ReputationEngine:
    """
    B2P 信誉引擎：负责计算 AI Agent 的风险等级与摩擦系数。
    核心特性：引入时间衰减因子，防止“养号作恶”。
    """

    # 配置参数
    HALF_LIFE_DAYS = 30           # 半衰期（天）
    SCORE_DECAY_RATE = 0.05       # 每30天衰减5%
    
    # 阈值
    LOW_RISK_THRESHOLD = 70       # >=70 低风险
    MEDIUM_RISK_THRESHOLD = 50    # 50-69 中风险
    HIGH_RISK_THRESHOLD = 30      # 30-49 高风险

    def calculate_time_decay(self, last_update_str: str) -> float:
        """
        计算时间衰减因子
        衰减公式：decay = e^(-λ * days_since_update)
        """
        try:
            last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_since = (now - last_update).days
            if days_since <= 0:
                return 1.0
            
            # λ = ln(2) / half_life
            lambda_val = math.log(2) / self.HALF_LIFE_DAYS
            decay = math.exp(-lambda_val * days_since)
            return max(decay, 0.3)  # 最低不低于0.3
        except Exception:
            return 1.0

    def calculate_friction_coefficient(self, data: ReputationData) -> float:
        """
        计算摩擦系数
        系数越高，交易成本/质押要求越高
        """
        base = 1.0
        
        # 信誉分影响
        if data.total_score < 30:
            base += 1.5
        elif data.total_score < 50:
            base += 0.8
        elif data.total_score < 70:
            base += 0.3
        else:
            base -= 0.2   # 高分奖励
        
        # 胜诉率影响
        if data.win_rate < 30:
            base += 0.5
        elif data.win_rate > 80:
            base -= 0.2
        
        # 争议次数影响
        if data.dispute_count > 5:
            base += min(data.dispute_count * 0.05, 0.5)
        
        return max(base, 0.5)  # 不低于0.5

    def get_risk_level(self, data: ReputationData) -> RiskLevel:
        """根据信誉分判定风险等级"""
        score = data.total_score
        if score >= self.LOW_RISK_THRESHOLD:
            return RiskLevel.LOW
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        elif score >= self.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def update_reputation(self, data: ReputationData, 
                          success: bool, 
                          amount: float,
                          was_disputed: bool = False,
                          dispute_won: bool = False) -> ReputationData:
        """
        根据交易结果更新信誉数据
        """
        # 1. 应用时间衰减
        decay = self.calculate_time_decay(data.last_update)
        data.total_score *= decay
        
        # 2. 更新交易统计
        data.total_transactions += 1
        data.total_volume += amount
        
        if success:
            data.success_count += 1
        else:
            # 交易失败，扣分
            data.total_score -= 5
            if was_disputed:
                data.dispute_count += 1
                data.total_score -= 10
                if dispute_won:
                    data.total_score += 8   # 胜诉返还部分
        
        # 3. 重新计算综合信誉分（加权）
        success_rate = data.success_count / max(data.total_transactions, 1)
        score_from_success = success_rate * 40  # 成功率贡献40分
        
        # 胜诉率贡献30分
        score_from_win = (data.win_rate / 100) * 30
        
        base_score = 30 + score_from_success + score_from_win
        
        # 争议惩罚
        dispute_penalty = min(data.dispute_count * 3, 20)
        final_score = max(base_score - dispute_penalty, 0)
        
        data.total_score = round(final_score, 2)
        data.friction_coefficient = self.calculate_friction_coefficient(data)
        data.last_update = datetime.utcnow().isoformat()
        
        return data
