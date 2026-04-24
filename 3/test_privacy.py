"""
Black2 隐私保护模块测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from privacy import (
    privacy_manager,
    PrivacyLevel,
    AnonymousIdentity
)


def test_privacy_manager():
    """测试隐私管理器核心功能"""
    print("=" * 60)
    print("测试1: 隐私管理器核心功能")
    print("=" * 60)
    
    # 测试1: 代理地址生成
    real_address = "0x1234567890abcdef1234567890abcdef12345678"
    proxy1 = privacy_manager.generate_proxy_address(real_address)
    proxy2 = privacy_manager.generate_proxy_address(real_address)
    
    assert proxy1 != real_address, "代理地址应与真实地址不同"
    assert proxy1 != proxy2, "两次生成的代理地址应该不同"
    print(f"  ✅ 代理地址生成测试通过")
    
    # 测试2: 创建匿名身份
    identity = privacy_manager.create_anonymous_identity(
        agent_id="test_agent_001",
        real_address=real_address,
        ttl_hours=24
    )
    
    assert isinstance(identity, AnonymousIdentity), "应返回 AnonymousIdentity"
    assert identity.agent_id == "test_agent_001", "Agent ID 不匹配"
    assert identity.active is True, "身份应处于激活状态"
    print(f"  ✅ 匿名身份创建测试通过")
    
    # 测试3: 身份存储
    assert identity.proxy_address in privacy_manager.anonymous_identities, "身份应被存储"
    print(f"  ✅ 身份存储测试通过")


def test_data_sanitization():
    """测试数据脱敏功能"""
    print("\n" + "=" * 60)
    print("测试2: 数据脱敏功能")
    print("=" * 60)
    
    original_data = {
        "agent_id": "test_agent",
        "wallet_address": "0x1234...",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "total_score": 85.5,
        "transaction_history": [
            {"amount": 100},
            {"amount": 200}
        ]
    }
    
    # 测试 AGGREGATED 级别
    sanitized_agg = privacy_manager.deidentify_data(
        original_data.copy(), 
        PrivacyLevel.AGGREGATED
    )
    
    assert "wallet_address" not in sanitized_agg, "钱包地址应被移除"
    assert "email" not in sanitized_agg, "邮箱应被移除"
    assert "transaction_history" not in sanitized_agg, "交易历史应被聚合"
    assert "total_volume" in sanitized_agg, "应有总交易量"
    print(f"  ✅ AGGREGATED 级别脱敏测试通过")
    
    # 测试 ANONYMOUS 级别
    sanitized_anon = privacy_manager.deidentify_data(
        original_data.copy(), 
        PrivacyLevel.ANONYMOUS
    )
    
    assert sanitized_anon["agent_id"] != "test_agent", "Agent ID 应被哈希"
    print(f"  ✅ ANONYMOUS 级别脱敏测试通过")


def test_zkp_statements():
    """测试 ZKP 声明功能"""
    print("\n" + "=" * 60)
    print("测试3: ZKP 声明功能")
    print("=" * 60)
    
    repo_data = {
        "total_score": 85.5,
        "dispute_count": 0
    }
    
    # 测试信誉足够声明
    statement1 = privacy_manager.prepare_zkp_statement(
        repo_data, 
        "sufficient_reputation"
    )
    
    assert statement1["statement"] == "agent_has_sufficient_reputation", "声明类型错误"
    assert statement1["min_score"] == 50.0, "最低分错误"
    assert "timestamp" in statement1, "应包含时间戳"
    print(f"  ✅ 信誉足够声明创建测试通过")
    
    # 测试验证
    is_valid = privacy_manager.verify_zkp_statement(statement1)
    assert is_valid is True, "信誉足够应验证通过"
    print(f"  ✅ 信誉足够验证测试通过")
    
    # 测试无纠纷声明
    statement2 = privacy_manager.prepare_zkp_statement(
        repo_data, 
        "no_recent_disputes"
    )
    
    assert statement2["statement"] == "no_recent_disputes", "声明类型错误"
    is_valid2 = privacy_manager.verify_zkp_statement(statement2)
    assert is_valid2 is True, "无纠纷应验证通过"
    print(f"  ✅ 无纠纷声明验证测试通过")


def test_hash_identifier():
    """测试标识符哈希"""
    print("\n" + "=" * 60)
    print("测试4: 标识符哈希")
    print("=" * 60)
    
    original = "test_agent_123"
    hashed = privacy_manager._hash_identifier(original)
    
    assert len(hashed) == 16, "哈希长度应为16"
    assert hashed != original, "哈希结果不应等于原字符串"
    
    # 测试一致性
    hashed2 = privacy_manager._hash_identifier(original)
    assert hashed == hashed2, "相同输入应产生相同哈希"
    print(f"  ✅ 标识符哈希测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Black2 隐私保护模块 - 测试套件")
    print("=" * 60)
    
    try:
        test_privacy_manager()
        test_data_sanitization()
        test_zkp_statements()
        test_hash_identifier()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
