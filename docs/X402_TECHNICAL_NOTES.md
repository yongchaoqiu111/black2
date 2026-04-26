# X402 协议技术笔记

**研究日期**: 2026-04-27  
**目的**: 为替换 `backend/src/x402/bridge.py` Mock 逻辑做准备

---

## 1. X402 核心原理

### 1.1 什么是 X402？

X402 是基于 HTTP 402 "Payment Required" 状态码构建的**原生链上支付协议**，专为 AI Agent 和机器自动化交易设计。

**核心特点**：
- ✅ **免注册** - 无需 API Key、账户或 KYC
- ✅ **钱包签名鉴权** - 使用链上交易哈希作为支付凭证
- ✅ **微支付支持** - 成本趋近于零，2秒内完成
- ✅ **多链兼容** - 支持 Base、BNB Chain、Solana 等

### 1.2 工作流程

```
sequenceDiagram
    participant C as AI Agent (Client)
    participant S as Black2 Server
    participant BC as Blockchain

    C->>S: 1. POST /api/v1/transactions (创建托管)
    S-->>C: 2. HTTP 200 + {tx_id, escrow_id}
    
    C->>BC: 3. 链上转账 USDT 到托管地址
    BC-->>C: 4. 返回 tx_hash
    
    C->>S: 5. POST /transactions/{tx_id}/complete (附带 tx_hash)
    S->>BC: 6. 验证 tx_hash 有效性
    BC-->>S: 7. 确认转账成功
    S->>S: 8. 扣除平台费 (5%)
    S->>BC: 9. 释放资金给卖家
    S-->>C: 10. HTTP 200 + {fund_release_result}
```

---

## 2. HTTP 402 响应结构

当服务端需要客户端支付时，返回：

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json

{
  "x402": {
    "version": "2",
    "accepts": [
      {
        "network": "base-sepolia",
        "asset": "USDT",
        "amount": "100.0",
        "payTo": "0xPlatformWalletAddress...",
        "description": "Escrow payment for transaction tx_001"
      }
    ],
    "resource": "/api/v1/transactions/tx_001/complete",
    "scheme": "exact"
  }
}
```

**关键字段**：
- `network`: 区块链网络（如 base-sepolia、bnb-chain）
- `asset`: 支付代币（USDT、USDC）
- `amount`: 精确金额
- `payTo`: 收款地址（平台托管钱包）
- `resource`: 支付对应的 API 资源

---

## 3. 支付凭证传递

客户端完成链上支付后，在重试请求中通过 Header 携带：

```http
POST /api/v1/transactions/tx_001/complete
X-402-Payment: {"network":"base-sepolia","txHash":"0xabc...123","asset":"USDT","amount":"100.0"}
```

**服务端验证流程**：
1. 解析 `X-402-Payment` Header
2. 调用区块链节点验证 `txHash` 是否存在且有效
3. 确认转账金额 ≥ 要求金额
4. 确认收款地址匹配
5. 验证通过后释放资金

---

## 4. 当前 Mock 实现分析

### 4.1 `initiate_escrow()` 方法

**当前逻辑**（第 70-103 行）：
```python
escrow_id = f"escrow_{int(time.time() * 1000)}_{sender[:10]}"
escrow_address = f"0x{''.join(self._random_hex(40))}"
```

**问题**：
- ❌ 随机生成 escrow_address，不是真实的链上地址
- ❌ 没有与区块链交互

**真实集成需改为**：
```python
# 调用 X402 B2P SDK 创建真实托管合约
from x402_sdk import create_escrow_contract

escrow_contract = await create_escrow_contract(
    network="base-sepolia",
    asset="USDT",
    amount=amount,
    buyer=sender,
    seller=receiver
)

return EscrowResult(
    escrow_id=escrow_contract.id,
    escrow_address=escrow_contract.address,  # 真实链上地址
    status="awaiting_payment",
    amount=amount,
    asset=asset,
    created_at=datetime.now().isoformat()
)
```

### 4.2 `release_funds()` 方法

**当前逻辑**（第 104-144 行）：
```python
net_amount = amount - platform_fee - arbitration_fee
tx_hash = f"0x{''.join(self._random_hex(64))}"  # 随机哈希
```

**问题**：
- ❌ 随机生成 tx_hash，没有真实链上交易
- ❌ 没有实际转账操作

**真实集成需改为**：
```python
# 调用 X402 B2P SDK 释放资金
from x402_sdk import release_escrow_funds

tx_hash = await release_escrow_funds(
    escrow_id=escrow_id,
    recipient=recipient,
    amount=net_amount,
    platform_fee_wallet=self.fee_wallet_address,
    platform_fee=platform_fee
)

return ReleaseResult(
    success=True,
    tx_hash=tx_hash,  # 真实链上交易哈希
    recipient=recipient,
    amount=net_amount,
    verdict=verdict,
    message=f"Funds released to {recipient}"
)
```

---

## 5. 钱包签名鉴权流程

### 5.1 为什么不需要 API Key？

X402 的设计哲学是**"链上验证就是一切"**：
- 传统 API：API Key → 中心化认证 → 信任中间方
- X402：钱包签名 → 链上验证 → 无需信任

### 5.2 签名过程

```python
# 1. 客户端准备支付数据
payment_data = {
    "network": "base-sepolia",
    "txHash": "0xabc...123",
    "asset": "USDT",
    "amount": "100.0"
}

# 2. 序列化并签名
import json
from eth_account import Account

json_str = json.dumps(payment_data, sort_keys=True)
signature = Account.sign_message(
    text=json_str,
    private_key=client_private_key
)

# 3. 附加到 HTTP 请求
headers = {
    "X-402-Payment": json_str,
    "X-402-Signature": signature.signature.hex()
}
```

### 5.3 服务端验证

```python
# 1. 提取签名
payment_json = request.headers.get("X-402-Payment")
signature_hex = request.headers.get("X-402-Signature")

# 2. 恢复公钥
from eth_account import Account
recovered_address = Account.recover_message(
    text=payment_json,
    signature=signature_hex
)

# 3. 验证公钥是否匹配付款地址
if recovered_address != expected_buyer_address:
    raise HTTPException(4002, "Invalid signature")

# 4. 验证链上交易
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://base-sepolia.infura.io"))
tx = w3.eth.get_transaction(payment_data["txHash"])
if tx.to != escrow_address:
    raise HTTPException(4002, "Payment sent to wrong address")
```

---

## 6. 集成路线图

### Phase 1: 准备工作（已完成）
- ✅ 理解 X402 协议原理
- ✅ 修正代码注释中的错误理解
- ✅ 设计标准化 API 响应格式

### Phase 2: SDK 调研（进行中）
- 🔲 查找 X402 B2P SDK 官方文档
- 🔲 测试 SDK 本地安装
- 🔲 编写最小可用示例

### Phase 3: 代码替换
- 🔲 替换 `initiate_escrow()` 为真实 SDK 调用
- 🔲 替换 `release_funds()` 为真实 SDK 调用
- 🔲 添加钱包签名验证中间件

### Phase 4: 测试与部署
- 🔲 编写端到端测试（使用测试网）
- 🔲 压力测试（高并发场景）
- 🔲 部署到生产环境

---

## 7. 关键资源链接

- **X402 官方文档**: https://docs.x402.org
- **B2P SDK GitHub**: https://github.com/cambrian-network/x402-sdk
- **Coinbase Agentic Wallets**: https://www.coinbase.com/agentic-wallets
- **示例代码**: https://gitcode.com/GitHub_Trending/x4/x402

---

## 8. 注意事项

⚠️ **安全警告**：
1. 私钥永远不要暴露在代码中，使用环境变量或密钥管理服务
2. 生产环境必须使用主网，测试阶段使用测试网（base-sepolia）
3. 所有链上操作都需要 Gas 费，确保平台钱包有足够 ETH

⚠️ **性能优化**：
1. 区块链查询应缓存结果，避免重复 RPC 调用
2. 使用 WebSocket 监听链上事件，而非轮询
3. 批量处理多个交易的资金释放，减少 Gas 消耗
