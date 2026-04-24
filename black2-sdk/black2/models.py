from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"          # 可交易，无需额外质押
    MEDIUM = "medium"    # 可交易，需提高质押比例
    HIGH = "high"        # 风险较高，建议拒绝或极高质押
    CRITICAL = "critical"  # 拒绝交易

@dataclass
class ReputationData:
    """
    b2p-repo.json 的数据结构（存储在 Git 仓库中）
    宏观脱敏数据，公开可读
    """
    # 身份标识
    agent_id: str                  # 唯一标识
    
    # 宏观信誉指标（公开）
    total_score: float = 70.0      # 综合信誉分 0-100
    win_rate: float = 0.0          # 胜诉率
    total_transactions: int = 0    # 总交易次数
    total_volume: float = 0.0      # 总交易金额
    dispute_count: int = 0         # 被仲裁次数
    success_count: int = 0         # 交易成功次数
    
    # 摩擦系数（实时计算）
    friction_coefficient: float = 1.0
    
    # 时间衰减相关
    last_update: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # 历史凭证（加密/哈希指针）
    arbitration_history: List[str] = field(default_factory=list)
    
    # 质押信息（与 X402 联动）
    staked_amount: float = 0.0     
    staked_asset: str = "USDC"     
