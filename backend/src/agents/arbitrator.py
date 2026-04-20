import json
from datetime import datetime

class Arbitrator:
    """
    仲裁系统类，用于处理交易纠纷
    """
    def arbitrate(self, tx_id, contract_hash, file_hash):
        """
        执行仲裁逻辑
        
        参数:
            tx_id: 纠纷交易 ID
            contract_hash: 合同约定的交付物哈希
            file_hash: 卖家实际提交的交付物哈希
            
        返回:
            仲裁结果字典，包含 tx_id, verdict, reason, timestamp
        """
        # 1. 从数据库获取交易详情（这里简化处理）
        # 2. 对比 contract_hash 和 file_hash
        # 3. 根据规则判断责任方
        
        if not file_hash:
            verdict = "buyer_wins"
            reason = "Seller did not deliver the file"
        elif contract_hash == file_hash:
            verdict = "seller_wins"
            reason = "Contract hash matches delivered file"
        else:
            verdict = "buyer_wins"
            reason = "Delivered file hash does not match contract hash"
        
        return {
            "tx_id": tx_id,
            "verdict": verdict,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# 示例用法
if __name__ == "__main__":
    arbitrator = Arbitrator()
    
    # 测试场景 1: 哈希匹配 - 卖家胜
    result1 = arbitrator.arbitrate(
        tx_id="tx_001",
        contract_hash="abc123",
        file_hash="abc123"
    )
    print("测试场景 1 结果:", json.dumps(result1, indent=2))
    
    # 测试场景 2: 哈希不匹配 - 买家胜
    result2 = arbitrator.arbitrate(
        tx_id="tx_002",
        contract_hash="abc123",
        file_hash="def456"
    )
    print("测试场景 2 结果:", json.dumps(result2, indent=2))
    
    # 测试场景 3: 未交付 - 买家胜
    result3 = arbitrator.arbitrate(
        tx_id="tx_003",
        contract_hash="abc123",
        file_hash=""
    )
    print("测试场景 3 结果:", json.dumps(result3, indent=2))
