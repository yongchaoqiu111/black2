# Black2 ↔ X402 集成指南
========================

## X402 官方资源汇总

### 核心入口
| 资源 | 地址 |
|------|------|
| 官方网站 | https://www.x402.org/ |
| NPM SDK | https://www.npmjs.com/package/@x402-crosschain/sdk |
| Cloudflare 文档 | https://developers.cloudflare.com/agents/agentic-payments/x402/ |
| QuickNode 文档 | https://www.quicknode.com/docs/build-with-ai/agentic-payments |

### 官方 SDK

#### TypeScript/JavaScript SDK（最全面）
```bash
npm install @x402-crosschain/sdk
```

**核心功能：**
- ✅ x402 协议兼容
- ✅ 客户无 Gas 支付（ERC-20 代币使用 Permit2）
- ✅ 支持 10+ 条链
- ✅ 2-3 秒结算（通过 Relay Network）

**支持的链：**
| 链 | Chain ID |
|-----|---------|
| Ethereum | 1 |
| Base | 8453 |
| Arbitrum | 42161 |
| Optimism | 10 |
| Polygon | 137 |
| BNB Chain | 56 |
| Solana | — |

#### Python SDK
```bash
pip install uvd-x402-sdk
```

**特性：**
- ✅ 18 条区块链 + 5 种稳定币
- ✅ 支持 Flask、FastAPI、Django、AWS Lambda
- ✅ 完整 Pydantic 类型提示

---

## Black2 与 X402 集成方案

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent Layer                          │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │ 买家 Agent   │         │ 卖家 Agent   │                  │
│  └──────┬───────┘         └──────┬───────┘                  │
└─────────┼────────────────────────┼──────────────────────────┘
          │                        │
          ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Black2 隐私保护层                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  数据脱敏 | 代理身份 | ZKP声明 | 信誉计算            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                        │
          ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    X402 支付层                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  多链支持 | 无Gas支付 | 快速结算 | Permit2           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 集成步骤

### 步骤1：安装 SDK

```python
# 安装 Black2 SDK（本地）
# pip install -e ./black2-sdk

# 安装 X402 SDK
pip install uvd-x402-sdk
```

### 步骤2：配置 X402 客户端

```python
from uvd_x402_sdk import X402Client
from privacy import privacy_manager

# 初始化 X402 客户端
x402 = X402Client(
    api_key="your_api_key",
    chain_id=8453  # Base 链
)

# 创建代理身份
identity = privacy_manager.create_anonymous_identity(
    agent_id="my_agent_001",
    real_address="0x1234...",
    ttl_hours=24
)
```

### 步骤3：使用代理地址进行支付

```python
def create_privacy_protected_payment(
    amount: float,
    asset: str,
    recipient_agent_id: str
):
    """
    创建隐私保护的支付
    """
    # 1. 获取收件人代理地址
    recipient_identity = privacy_manager.create_anonymous_identity(
        agent_id=recipient_agent_id,
        real_address="0x5678..."
    )
    
    # 2. 创建 X402 支付（使用代理地址）
    payment = x402.create_payment({
        "amount": amount,
        "asset": asset,
        "recipient": recipient_identity.proxy_address,
        "sender": identity.proxy_address,
        "payment_type": "exact"
    })
    
    return payment
```

---

## 完整的端到端示例

```python
"""
完整的 Black2 + X402 交易示例
"""
from privacy import privacy_manager, PrivacyLevel
from uvd_x402_sdk import X402Client

# 1. 初始化
x402 = X402Client(api_key="your_key", chain_id=8453)

# 2. 创建买卖双方代理身份
buyer_id = "buyer_agent_001"
seller_id = "seller_agent_001"

buyer_identity = privacy_manager.create_anonymous_identity(buyer_id, "0x1234...")
seller_identity = privacy_manager.create_anonymous_identity(seller_id, "0x5678...")

print(f"买家代理: {buyer_identity.proxy_address}")
print(f"卖家代理: {seller_identity.proxy_address}")

# 3. 检查卖家信誉（使用 ZKP）
seller_repo_data = {"total_score": 85.5, "dispute_count": 0}
zkp_statement = privacy_manager.prepare_zkp_statement(
    seller_repo_data, 
    "sufficient_reputation"
)

if privacy_manager.verify_zkp_statement(zkp_statement):
    print("卖家信誉验证通过 ✅")
else:
    print("卖家信誉不足 ❌")
    exit()

# 4. 创建合同
contract_content = {"task": "write_article", "word_count": 100}
contract_hash = privacy_manager._hash_identifier(str(contract_content))

# 5. 通过 X402 锁定资金
payment = x402.create_payment({
    "amount": 100.0,
    "asset": "USDC",
    "sender": buyer_identity.proxy_address,
    "recipient": seller_identity.proxy_address,
    "payment_type": "exact"
})

print(f"资金已锁定，支付ID: {payment['payment_id']}")

# 6. 卖家收到信号，开始交付
# ... 卖家交付逻辑 ...

# 7. 买家确认，X402 释放资金
x402.release_payment(payment['payment_id'])

# 8. 更新信誉（仅脱敏数据）
print("信誉已更新（仅宏观指标）")
```

---

## 隐私保护检查表

- [ ] 所有 X402 支付使用代理地址
- [ ] 真实钱包地址从未暴露
- [ ] b2p-repo.json 仅包含宏观数据
- [ ] 使用 ZKP 声明验证信誉
- [ ] 交易历史已脱敏/聚合
- [ ] 代理身份有过期机制

---

## 参考链接

- X402 官网: https://www.x402.org/
- Cloudflare X402 文档: https://developers.cloudflare.com/agents/agentic-payments/x402/
- QuickNode X402 文档: https://www.quicknode.com/docs/build-with-ai/agentic-payments
- Black2 白皮书: ../AI_与_AI_可信交易协议白皮书（精简版）.md
