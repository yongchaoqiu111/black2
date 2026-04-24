"""
Black2 隐私保护完整示例
演示数据脱敏、代理身份、ZKP声明等功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'black2-sdk'))

from privacy import privacy_manager, PrivacyLevel


def example_1_data_sanitization():
    """示例1：数据脱敏"""
    print("=" * 60)
    print("示例1：数据脱敏与选择性披露")
    print("=" * 60)
    
    # 原始数据（包含敏感信息）
    original_data = {
        "agent_id": "ai_agent_001",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
        "email": "agent@example.com",
        "total_score": 85.5,
        "transaction_history": [
            {"tx_id": "tx1", "amount": 100, "counterparty": "agent_002"},
            {"tx_id": "tx2", "amount": 200, "counterparty": "agent_003"}
        ]
    }
    
    print(f"\n原始数据:")
    print(f"  Agent ID: {original_data['agent_id']}")
    print(f"  钱包地址: {original_data['wallet_address']}")
    print(f"  交易历史: {len(original_data['transaction_history'])} 条")
    
    # 数据脱敏 - AGGREGATED级别
    sanitized_agg = privacy_manager.deidentify_data(
        original_data.copy(), 
        PrivacyLevel.AGGREGATED
    )
    
    print(f"\nAGGREGATED 级别脱敏:")
    print(f"  钱包地址: {'已移除' if 'wallet_address' not in sanitized_agg else sanitized_agg['wallet_address']}")
    print(f"  交易历史: {'已聚合' if 'transaction_history' not in sanitized_agg else '保留'}")
    print(f"  总交易量: {sanitized_agg.get('total_volume', 'N/A')}")
    
    # 数据脱敏 - ANONYMOUS级别
    sanitized_anon = privacy_manager.deidentify_data(
        original_data.copy(), 
        PrivacyLevel.ANONYMOUS
    )
    
    print(f"\nANONYMOUS 级别脱敏:")
    print(f"  Agent ID: {sanitized_anon['agent_id']} (已哈希)")


def example_2_proxy_identity():
    """示例2：代理身份与一次性地址"""
    print("\n" + "=" * 60)
    print("示例2：代理身份与一次性地址")
    print("=" * 60)
    
    agent_id = "my_ai_agent_001"
    real_address = "0x1234567890abcdef1234567890abcdef12345678"
    
    print(f"\n真实钱包地址: {real_address}")
    print(f"Agent ID: {agent_id}")
    
    # 创建代理身份
    identity = privacy_manager.create_anonymous_identity(
        agent_id=agent_id,
        real_address=real_address,
        ttl_hours=24
    )
    
    print(f"\n生成的代理地址: {identity.proxy_address}")
    print(f"创建时间: {identity.created_at}")
    print(f"过期时间: {identity.expires_at}")
    print(f"是否激活: {identity.active}")


def example_3_zkp_statements():
    """示例3：零知识证明声明"""
    print("\n" + "=" * 60)
    print("示例3：零知识证明 (ZKP) 声明")
    print("=" * 60)
    
    # 信誉数据
    repo_data = {
        "total_score": 85.5,
        "dispute_count": 3,
        "win_rate": 92.0
    }
    
    print(f"\nAgent 信誉数据:")
    print(f"  总信誉分: {repo_data['total_score']}")
    print(f"  纠纷次数: {repo_data['dispute_count']}")
    
    # 准备"信誉足够"声明
    statement1 = privacy_manager.prepare_zkp_statement(
        data=repo_data,
        statement_type="sufficient_reputation"
    )
    
    print(f"\nZKP 声明 - 信誉足够:")
    print(f"  声明类型: {statement1['statement']}")
    print(f"  最低要求: {statement1['min_score']}")
    print(f"  实际得分: {statement1['actual_score']}")
    print(f"  是否满足: {statement1['score_meets_threshold']}")
    
    # 验证声明
    is_valid = privacy_manager.verify_zkp_statement(statement1)
    print(f"  验证结果: {'通过 ✅' if is_valid else '失败 ❌'}")
    
    # 准备"无纠纷"声明
    statement2 = privacy_manager.prepare_zkp_statement(
        data=repo_data,
        statement_type="no_recent_disputes"
    )
    
    print(f"\nZKP 声明 - 无近期纠纷:")
    print(f"  声明类型: {statement2['statement']}")
    print(f"  纠纷次数: {statement2['dispute_count']}")
    print(f"  是否清白: {statement2['clean_record']}")


def example_4_complete_workflow():
    """示例4：完整交易流程"""
    print("\n" + "=" * 60)
    print("示例4：完整隐私保护交易流程")
    print("=" * 60)
    
    # 1. 买卖双方创建代理身份
    print("\n[步骤1] 创建代理身份")
    buyer_id = "buyer_agent_001"
    buyer_real = "0x1234..."
    buyer_identity = privacy_manager.create_anonymous_identity(buyer_id, buyer_real, 24)
    print(f"  买家代理地址: {buyer_identity.proxy_address}")
    
    seller_id = "seller_agent_001"
    seller_real = "0x5678..."
    seller_identity = privacy_manager.create_anonymous_identity(seller_id, seller_real, 24)
    print(f"  卖家代理地址: {seller_identity.proxy_address}")
    
    # 2. 买家检查卖家信誉（使用ZKP）
    print("\n[步骤2] 买家检查卖家信誉")
    seller_repo_data = {
        "total_score": 85.5,
        "dispute_count": 0
    }
    
    zkp_statement = privacy_manager.prepare_zkp_statement(
        seller_repo_data, 
        "sufficient_reputation"
    )
    
    is_trustworthy = privacy_manager.verify_zkp_statement(zkp_statement)
    print(f"  卖家信誉验证: {'通过 ✅' if is_trustworthy else '失败 ❌'}")
    
    # 3. 模拟交易流程
    print("\n[步骤3] 交易流程")
    print("  → 买家锁定资金（使用代理地址）")
    print("  → 卖家收到资金锁定信号")
    print("  → 卖家开始交付")
    print("  → 买家确认收货")
    print("  → 资金释放")
    
    # 4. 更新信誉（仅公开聚合数据）
    print("\n[步骤4] 更新信誉（脱敏数据）")
    print("  → 仅更新宏观指标：总交易次数、总成交量、信誉分")
    print("  → 不记录具体交易对手")


if __name__ == "__main__":
    print("Black2 隐私保护功能演示")
    print("=" * 60)
    
    example_1_data_sanitization()
    example_2_proxy_identity()
    example_3_zkp_statements()
    example_4_complete_workflow()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
