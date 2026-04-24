import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'black2-sdk'))

from black2.client import B2PClient
from black2.models import ReputationData

def main():
    print("🚀 启动 B2P SDK 本地测试模式...")
    
    # 初始化客户端（开启本地模式）
    client = B2PClient(local_mode=True)
    
    agent_id = "ai_trader_001"
    
    # 1. 初始状态检查
    print("\n--- 1. 初始状态 ---")
    risk_info = client.check_agent_risk(agent_id)
    print(f"风险等级: {risk_info.get('risk_level')}")
    print(f"当前信誉分: {risk_info.get('total_score')}")
    
    # 2. 模拟连续成功交易
    print("\n--- 2. 模拟连续 5 次成功交易 (每次 $1000) ---")
    for i in range(5):
        result = client.record_transaction(agent_id, success=True, amount=1000)
        print(f"  第 {i+1} 次交易后信誉分: {result['new_score']}")
        
    # 3. 检查高分状态
    print("\n--- 3. 高分状态评估 ---")
    risk_info = client.check_agent_risk(agent_id)
    print(f"风险等级: {risk_info.get('risk_level')}")
    print(f"摩擦系数: {risk_info.get('friction_coefficient')}")
    
    # 4. 模拟一次失败且被仲裁的交易
    print("\n--- 4. 模拟 1 次失败交易并触发仲裁 (败诉) ---")
    result = client.record_transaction(agent_id, success=False, amount=5000, was_disputed=True, dispute_won=False)
    print(f"  仲裁败诉后信誉分: {result['new_score']}")
    
    # 5. 最终状态检查
    print("\n--- 5. 最终风险评估 ---")
    risk_info = client.check_agent_risk(agent_id)
    print(f"风险等级: {risk_info.get('risk_level')}")
    print(f"摩擦系数: {risk_info.get('friction_coefficient')}")
    print(f"总交易额: ${client.engine._load_local(agent_id).total_volume if hasattr(client.engine, '_load_local') else 'N/A'}")

if __name__ == "__main__":
    main()
