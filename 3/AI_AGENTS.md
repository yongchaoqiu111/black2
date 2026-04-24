# Black2 AI Agent 隐私保护交互规范
=====================================

## 概述
本文档定义了 AI Agent 在接入 Black2 清算协议时的隐私保护标准与交互规范，确保交易隐私符合 GDPR 等合规要求。

---

## 隐私等级说明 (Privacy Level)

Black2 SDK 提供四种隐私保护等级，可根据不同场景选择：

| 等级 | 说明 | 适用场景 |
|------|------|----------|
| **PUBLIC** | 完全公开，不做任何处理 | 内部测试、可信任环境 |
| **AGGREGATED** | 仅聚合数据，移除具体交易细节 | 公开发布到 GitHub 的 b2p-repo.json |
| **ANONYMOUS** | 匿名化处理，哈希化标识符 | API 响应、第三方查询 |
| **ZKP** | 零知识证明，仅提供声明 | 最高隐私要求场景 |

### Privacy Level 快速使用

```python
from black2.privacy import PrivacyLevel, privacy_manager

# 1. AGGREGATED - 用于公开仓库数据
sanitized_github = privacy_manager.deidentify_data(
    repo_data,
    PrivacyLevel.AGGREGATED
)

# 2. ANONYMOUS - 用于 API 响应
sanitized_api = privacy_manager.deidentify_data(
    data,
    PrivacyLevel.ANONYMOUS
)

# 3. ZKP - 用于高隐私要求场景
zkp_proof = privacy_manager.generate_zkp_proof(agent_id, repo_data)
```

### 隐私处理效果对比

| 原始字段 | PUBLIC | AGGREGATED | ANONYMOUS | ZKP |
|---------|--------|------------|-----------|-----|
| agent_id | ✅ | ✅ | 🔒 (哈希) | 🔒 (哈希) |
| wallet_address | ✅ | ❌ (移除) | ❌ (移除) | ❌ (移除) |
| total_score | ✅ | ✅ | ✅ | ✅ |
| transaction_history | ✅ | ❌ (聚合) | ❌ (聚合) | ❌ (聚合) |
| total_transactions | ❌ | ✅ (新增) | ✅ (新增) | ✅ (新增) |
| total_volume | ❌ | ✅ (新增) | ✅ (新增) | ✅ (新增) |

---

## 第一部分：数据脱敏与选择性披露

### 1.1 b2p-repo.json 隐私字段设计

b2p-repo.json 仅存储宏观脱敏数据，不包含微观交易细节：

```json
{
  "agent_id": "agent_123abc",
  "total_score": 85.5,
  "win_rate": 92.0,
  "total_transactions": 156,
  "total_volume": 15600.50,
  "dispute_count": 3,
  "success_count": 148,
  "friction_coefficient": 0.8,
  "last_update": "2026-04-25T10:30:00",
  "arbitration_history": [
    "hash:abc123...",
    "hash:def456..."
  ],
  "staked_amount": 1000.0,
  "staked_asset": "USDC"
}
```

**公开字段说明：**
- ✅ **total_score: 综合信誉分 (0-100)
- ✅ **win_rate: 胜诉率 (%)
- ✅ **total_transactions: 总交易次数
- ✅ **total_volume: 总交易金额
- ✅ **dispute_count: 被仲裁次数
- ✅ **success_count: 成功交易次数
- ✅ **friction_coefficient: 摩擦系数
- ✅ **arbitration_history: 仅哈希指针，不包含详细内容

**隐藏字段（不公开）：**
- ❌ 具体交易详情
- ❌ 真实钱包地址
- ❌ 用户个人信息
- ❌ 交易对手身份

---

### 1.2 一次性地址与代理身份

AI Agent 在调用 X402 支付时，使用代理身份，避免暴露真实钱包：

```python
from privacy import privacy_manager

# 创建匿名身份
agent_id = "my_ai_agent_001"
real_address = "0x1234567890abcdef1234567890abcdef12345678"

identity = privacy_manager.create_anonymous_identity(
    agent_id=agent_id,
    real_address=real_address,
    ttl_hours=24  # 24小时有效期
)

print(f"代理地址: {identity.proxy_address}")
```

**代理身份特性：
- 🕵️‍♂️ 自动过期机制（默认24小时）
- 🔒 真实地址与代理地址单向映射
- 📊 不影响信誉计算
- 🎯 每笔交易可使用新代理

---

## 第二部分：零知识证明 (ZKP) 预研

### 2.1 ZKP 应用场景

#### 场景1：证明"我有足够信誉"而不泄露历史

```python
from privacy import privacy_manager

# 准备ZKP声明
repo_data = {
    "total_score": 85.5,
    "dispute_count": 3
}

zkp_statement = privacy_manager.prepare_zkp_statement(
    data=repo_data,
    statement_type="sufficient_reputation"
)

# 验证声明
is_valid = privacy_manager.verify_zkp_statement(zkp_statement)
```

**声明内容：
```json
{
  "statement": "agent_has_sufficient_reputation",
  "min_score": 50.0,
  "actual_score": 85.5,
  "score_meets_threshold": true,
  "timestamp": "2026-04-25T10:30:00Z"
}
```

#### 场景2：证明"近期无纠纷"

```python
zkp_statement = privacy_manager.prepare_zkp_statement(
    data=repo_data,
    statement_type="no_recent_disputes"
)
```

### 2.2 隐私保护 API 设计

```python
# 隐私保护查询接口
GET /api/v1/privacy/check_reputation
{
  "agent_id": "agent_123abc",
  "check_type": "risk_level|zkp_statement"
}

# 响应（仅返回必要信息）
{
  "risk_level": "low",
  "zkp_statement": {...},
  "verified": true
}
```

---

## 第三部分：AI 交互标准化

### 3.1 标准交互流程

```
┌──────────┐        ┌──────────┐        ┌──────────┐
│ 买家   │        │ Black2  │        │ 卖家   │
│ Agent  │        │ 清算层  │        │ Agent  │
└────┬───┘        └────┬───┘        └────┬───┘
     │               │               │
     │ 1. 发布需求  │               │
     │──────────────>│               │
     │               │               │
     │               │ 2. 验证信誉  │
     │               │──────────────>│
     │               │               │
     │               │ 3. 信誉证明  │
     │               │<──────────────│
     │               │ (ZKP声明)    │
     │               │               │
     │ 4. 锁定资金  │               │
     │──────────────>│               │
     │ (使用代理地址)│               │
     │               │               │
     │               │ 5. 资金已锁定│
     │               │──────────────>│
     │               │ (信号)       │
     │               │               │
     │               │               │ 6. 开始交付
     │               │               │
     │               │               │
     │ 7. 确认收货  │               │
     │<───────────────────────────────│
     │               │               │
     │ 8. 释放资金  │               │
     │──────────────>│               │
     │               │               │
     │               │ 9. 更新信誉  │
     │<──────────────│               │
     │ (脱敏数据)  │               │
```

### 3.2 AI 行为规范

#### 规范1：收到"资金已锁定"信号后的行为

当 AI Agent 收到 `payment_locked` 信号后：

```python
# 伪代码示例
def on_payment_locked(transaction_id: str, contract_hash: str):
    """
    收到资金锁定信号后的标准行为
    """
    # 1. 验证信号来源（确保来自 Black2）
    if not verify_signal_source():
        return
    
    # 2. 生成/加载合同内容
    contract_content = load_contract(contract_hash)
    
    # 3. 生成交付物
    deliverable = generate_deliverable(contract_content)
    
    # 4. 计算交付物哈希
    file_hash = calculate_hash(deliverable)
    
    # 5. 提交交付
    submit_delivery(transaction_id, file_hash)
    
    # 6. 等待确认
    await_confirmation(transaction_id)
```

#### 规范2：解析支付指令

AI Agent 解析 Black2 返回的支付指令：

```python
def parse_payment_instruction(instruction: dict):
    """
    解析支付指令
    """
    return {
        "amount": instruction.get("amount"),
        "asset": instruction.get("asset"),
        "recipient_proxy": instruction.get("recipient_proxy"),  # 代理地址
        "lock_until": instruction.get("lock_until"),
        "contract_hash": instruction.get("contract_hash")
    }
```

### 3.3 完整示例

```python
# 完整的 AI Agent 交易流程
from privacy import privacy_manager
from black2_sdk import B2PClient

# 1. 初始化
client = B2PClient(local_mode=True)

# 2. 创建匿名身份
buyer_identity = privacy_manager.create_anonymous_identity(
    agent_id="buyer_agent_001",
    real_address="0x1234..."
)

# 3. 检查卖方信誉（使用ZKP）
seller_reputation = client.check_agent_risk("seller_agent_001")
zkp_statement = privacy_manager.prepare_zkp_statement(
    data=seller_reputation,
    statement_type="sufficient_reputation"
)

if not privacy_manager.verify_zkp_statement(zkp_statement):
    print("卖方信誉不足")
    exit()

# 4. 创建交易
contract_content = {"task": "write_article", "word_count": 100}
contract_hash = calculate_hash(contract_content)

transaction = client.create_transaction(
    from_address=buyer_identity.proxy_address,  # 使用代理地址
    to_address="seller_proxy_address",
    amount=100.0,
    contract_hash=contract_hash
)

# 5. 等待资金锁定
await payment_locked(transaction["tx_id"])

# 6. 卖家交付
# ... (卖家逻辑)

# 7. 买家确认收货
# ...

# 8. 更新信誉（脱敏数据）
client.record_transaction(
    agent_id="seller_agent_001",
    success=True,
    amount=100.0
)
```

---

## 第四部分：合规性检查清单

- [ ] 所有公开数据仅包含宏观指标
- [ ] 使用代理身份进行支付
- [ ] 实现数据脱敏机制
- [ ] 提供ZKP声明接口
- [ ] 符合GDPR数据最小化原则
- [ ] 有明确的AI行为规范文档
- [ ] 完整的交易流程示例

---

## 附录：术语表

| 术语 | 说明 |
|------|------|
| 代理地址 | 一次性使用的钱包地址，不关联真实身份 |
| ZKP声明 | 零知识证明声明，证明某个事实而不泄露详细信息 |
| 数据脱敏 | 移除或替换敏感信息的过程 |
| 摩擦系数 | 衡量交易风险的指标，影响质押要求 |
