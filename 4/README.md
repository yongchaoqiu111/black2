# Black2 SDK - B2P + X402 Integration Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![X402 Compatible](https://img.shields.io/badge/X402-v2-green.svg)](https://www.x402.org/)

**Black2 SDK** 是 B2P (Black2 Protocol) 协议的官方 Python 实现，提供 AI Agent 之间的可信交易基础设施。通过集成 X402 跨链支付协议，实现安全、无需 Gas 的托管交易和自动仲裁。

## 📦 核心功能

- ✅ **信誉风险评估** - 基于链上历史和社交证明的 AI Agent 信誉系统
- ✅ **X402 托管支付** - 条件支付锁定，2-3 秒跨链结算
- ✅ **自动仲裁系统** - 基于哈希比对的纠纷自动裁决
- ✅ **本地模拟模式** - 无需 API Key 即可开发和测试
- ✅ **多资产支持** - USDC, USDT, ETH, BTC 等多种加密货币

## 🚀 快速开始

### 安装

```bash
# 从源码安装
cd black2-sdk
pip install -e .

# 或者直接使用
pip install black2-sdk
```

### 基础用法

#### 1. 初始化客户端

```python
from black2 import B2PClient
from black2.x402_bridge import X402Bridge

# 初始化 B2P 客户端（本地模式）
client = B2PClient(local_mode=True)

# 初始化 X402 桥接（模拟模式）
bridge = X402Bridge(mock_mode=True)
```

#### 2. 检查 Agent 风险

```python
# 查询 AI Agent 的风险等级
assessment = client.check_agent_risk("agent_001")

print(f"Risk Level: {assessment['risk_level']}")
print(f"Friction Coefficient: {assessment['friction_coefficient']}")
print(f"Total Score: {assessment['total_score']}")
```

#### 3. 发起托管支付

```python
# 发起一笔托管支付（条件支付）
escrow_result = bridge.initiate_escrow_payment(
    sender_id="buyer_001",
    receiver_id="seller_002",
    amount=500.0,
    asset="USDC",
    contract_hash="abc123def456"  # 合同约定的交付物哈希
)

print(f"Escrow ID: {escrow_result['escrow_id']}")
print(f"Status: {escrow_result['status']}")
# 输出：Status: locked (资金已锁定)
```

#### 4. 提交交付物

```python
# 卖家提交实际交付物
tx_id = escrow_result['escrow_id']
file_hash = "abc123def456"  # 应该与 contract_hash 匹配

# 在实际系统中，这里会调用 API 提交交付物
# response = requests.post(f"/api/transactions/{tx_id}/deliver", json={"file_hash": file_hash})
```

#### 5. 纠纷仲裁

```python
from test_arbitrator import ArbitrationSimulator

# 创建仲裁模拟器
simulator = ArbitrationSimulator(mock_mode=True)

# 场景 1: 正常履约（哈希匹配 - 卖家胜）
tx = simulator.create_transaction(
    buyer_id="buyer_001",
    seller_id="seller_002",
    amount=500.0,
    contract_hash="abc123"
)

simulator.submit_delivery(tx['tx_id'], file_hash="abc123")

# 无纠纷，直接放款给卖家
result = bridge.release_funds(
    escrow_id=tx['tx_id'],
    recipient=tx['seller_id'],
    verdict="seller_wins"
)

# 场景 2: 质量纠纷（哈希不匹配 - 买家胜）
tx2 = simulator.create_transaction(
    buyer_id="buyer_001",
    seller_id="seller_002",
    amount=500.0,
    contract_hash="abc123"
)

simulator.submit_delivery(tx2['tx_id'], file_hash="xyz789")  # 不匹配

# 买家发起纠纷
dispute = simulator.initiate_dispute(
    tx_id=tx2['tx_id'],
    reason="Product quality does not match contract"
)

# 自动仲裁
arbitration = simulator.arbitrate(dispute['dispute_id'])
print(f"Verdict: {arbitration['verdict']}")  # buyer_wins

# 执行裁决 - 退款给买家
execution = simulator.execute_verdict(dispute['dispute_id'])
print(f"Refund tx hash: {execution['tx_hash']}")
```

## 📚 API 参考

### B2PClient

#### `__init__(github_token=None, ipfs_host="http://127.0.0.1:5001", local_mode=False)`

初始化 B2P 客户端。

**参数:**
- `github_token` (可选): GitHub API Token，用于访问信誉仓库
- `ipfs_host` (可选): IPFS 节点地址
- `local_mode` (布尔): 是否使用本地模式（调试用）

#### `check_agent_risk(agent_id, github_owner=None, github_repo=None)`

查询 AI Agent 的风险等级。

**返回:**
```json
{
  "risk_level": "LOW",
  "friction_coefficient": 0.15,
  "total_score": 850
}
```

#### `record_transaction(agent_id, success, amount, was_disputed=False, dispute_won=False)`

记录交易结果并更新信誉。

### X402Bridge

#### `__init__(api_key=None, mock_mode=False)`

初始化 X402 支付桥接。

**参数:**
- `api_key` (可选): X402 API Key，不提供则使用环境变量 `X402_API_KEY`
- `mock_mode` (布尔): 是否使用模拟模式

#### `initiate_escrow_payment(sender_id, receiver_id, amount, asset="USDC", contract_hash=None)`

发起托管支付。

**返回:**
```json
{
  "status": "locked",
  "escrow_id": "esc_buyer_001_seller_002_500",
  "amount": 500.0,
  "message": "Funds locked in X402 Relay Network awaiting B2P verdict."
}
```

#### `release_funds(escrow_id, recipient, verdict)`

根据仲裁裁决释放资金。

**参数:**
- `verdict`: `"seller_wins"` 或 `"buyer_wins"`

#### `check_balance(agent_id, asset="USDC")`

查询 Agent 余额。

### ArbitrationSimulator

完整的仲裁流程模拟器，用于测试和演示。

#### `run_full_scenario(scenario)`

运行完整的仲裁场景。

**支持场景:**
- `"normal_completion"` - 正常履约
- `"quality_dispute"` - 质量纠纷
- `"non_delivery"` - 未交付

## 🔧 错误码体系

| 错误码 | 名称 | 说明 |
|--------|------|------|
| 1001 | REPUTATION_REJECTED | 信誉拒绝（Agent 风险过高） |
| 1002 | INSUFFICIENT_BALANCE | 余额不足 |
| 1003 | NETWORK_TIMEOUT | 网络超时 |
| 1004 | INVALID_ADDRESS | 无效地址 |
| 1005 | ESCROW_NOT_FOUND | 托管 ID 不存在 |
| 1006 | ARBITRATION_PENDING | 仲裁中 |
| 9999 | INTERNAL_ERROR | 内部错误 |

## 🧪 运行测试

```bash
# 运行仲裁模拟器测试
python test_arbitrator.py

# 运行单元测试
python -m pytest tests/
```

## 📖 示例代码

更多示例请参考：

- [Python 完整示例](examples/python_example.py)
- [JavaScript 完整示例](examples/javascript_example.js)
- [仲裁模拟器](test_arbitrator.py)

## 🌐 X402 官方资源

- **官方网站**: [x402.org](https://www.x402.org/)
- **NPM SDK**: [@x402-crosschain/sdk](https://www.npmjs.com/package/@x402-crosschain/sdk)
- **Python SDK**: `pip install uvd-x402-sdk`
- **支持链**: Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain, Solana 等 18+ 条链

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 📞 联系方式

- Website: [black2.ai](https://black2.ai)
- Twitter: @Black2Protocol
- Discord: Black2 Community

---

**Built with ❤️ by the Black2 Team**
