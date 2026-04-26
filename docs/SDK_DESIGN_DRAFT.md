# Black2 SDK 接口定义草案

**版本**: v0.1.0 (Prototype)  
**目标**: 为 AI Agent 提供简洁的 API 调用封装

---

## 1. Python SDK (`black2-sdk-py`)

### 核心类架构

```python
class Black2Client:
    """Main client for Black2 protocol interaction"""
    
    def __init__(self, api_base: str, private_key: str = None):
        """
        Initialize Black2 client
        
        Args:
            api_base: Black2 API base URL (e.g., http://localhost:3000/api/v1)
            private_key: Optional private key for signing requests
        """
        pass
    
    # Transaction Management
    async def create_escrow(
        self,
        seller_address: str,
        amount: float,
        contract_hash: str,
        currency: str = "USDT"
    ) -> Dict[str, Any]:
        """
        Create an escrow transaction
        
        Returns:
            {tx_id, escrow_id, status, amount}
        """
        pass
    
    async def complete_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Complete transaction and trigger fund release
        
        Returns:
            {tx_id, status, fund_release_result}
        """
        pass
    
    async def get_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Get transaction details
        
        Returns:
            {tx_id, status, amount, escrow_details, ...}
        """
        pass
    
    # Reputation System
    async def get_reputation_score(self, address: str) -> Dict[str, Any]:
        """
        Get AI agent reputation score
        
        Returns:
            {address, reputation_score, dispute_count, success_rate, ...}
        """
        pass
    
    # Arbitration Fund Pool
    async def get_arbitration_fund_pool(self) -> Dict[str, Any]:
        """
        Get arbitration fund pool statistics
        
        Returns:
            {total_balance, total_injections, recent_injections}
        """
        pass


class TransactionManager:
    """Helper class for batch transaction operations"""
    
    def __init__(self, client: Black2Client):
        pass
    
    async def batch_create_escrows(self, transactions: List[Dict]) -> List[Dict]:
        """Create multiple escrows in batch"""
        pass
    
    async def monitor_transactions(self, tx_ids: List[str]) -> Dict[str, str]:
        """Monitor multiple transaction statuses"""
        pass


class ReputationOracle:
    """Reputation data query and analysis"""
    
    def __init__(self, client: Black2Client):
        pass
    
    async def check_risk_level(self, address: str) -> str:
        """
        Check risk level for an AI agent
        
        Returns: 'low', 'medium', 'high', 'critical'
        """
        pass
    
    async def get_trading_history(self, address: str, limit: int = 100) -> List[Dict]:
        """Get trading history for an address"""
        pass
```

### 使用示例

```python
from black2_sdk import Black2Client

# Initialize client
client = Black2Client(
    api_base="http://localhost:3000/api/v1",
    private_key="your_private_key_hex"
)

# Create escrow
result = await client.create_escrow(
    seller_address="0xseller...",
    amount=100.0,
    contract_hash="abc123..."
)
print(f"Transaction created: {result['tx_id']}")

# Check reputation
reputation = await client.get_reputation_score("0xagent...")
print(f"Reputation score: {reputation['reputation_score']}")

# Complete transaction
completion = await client.complete_transaction(result['tx_id'])
print(f"Funds released: {completion['data']['fund_release_result']}")
```

---

## 2. JavaScript SDK (`black2-sdk-js`)

### 核心类架构

```javascript
class Black2Client {
  constructor(apiBase, privateKey = null) {
    this.apiBase = apiBase;
    this.privateKey = privateKey;
  }

  // Transaction Management
  async createEscrow({ sellerAddress, amount, contractHash, currency = 'USDT' }) {
    // POST /api/v1/transactions
    // Returns: {tx_id, escrow_id, status, amount}
  }

  async completeTransaction(txId) {
    // POST /api/v1/transactions/{tx_id}/complete
    // Returns: {tx_id, status, fund_release_result}
  }

  async getTransaction(txId) {
    // GET /api/v1/transactions/{tx_id}
    // Returns: {tx_id, status, amount, escrow_details, ...}
  }

  // Reputation System
  async getReputationScore(address) {
    // GET /api/v1/reputation/{address}
    // Returns: {address, reputation_score, dispute_count, success_rate, ...}
  }

  // Arbitration Fund Pool
  async getArbitrationFundPool() {
    // GET /api/v1/arbitration/fund-pool
    // Returns: {total_balance, total_injections, recent_injections}
  }
}

class TransactionManager {
  constructor(client) {
    this.client = client;
  }

  async batchCreateEscrows(transactions) {
    // Batch create multiple escrows
  }

  async monitorTransactions(txIds) {
    // Monitor multiple transaction statuses
  }
}

class ReputationOracle {
  constructor(client) {
    this.client = client;
  }

  async checkRiskLevel(address) {
    // Returns: 'low', 'medium', 'high', 'critical'
  }

  async getTradingHistory(address, limit = 100) {
    // Get trading history for an address
  }
}
```

### 使用示例

```javascript
const { Black2Client } = require('black2-sdk');

// Initialize client
const client = new Black2Client(
  'http://localhost:3000/api/v1',
  'your_private_key_hex'
);

// Create escrow
const result = await client.createEscrow({
  sellerAddress: '0xseller...',
  amount: 100.0,
  contractHash: 'abc123...'
});
console.log(`Transaction created: ${result.tx_id}`);

// Check reputation
const reputation = await client.getReputationScore('0xagent...');
console.log(`Reputation score: ${reputation.reputation_score}`);

// Complete transaction
const completion = await client.completeTransaction(result.tx_id);
console.log(`Funds released: ${completion.data.fund_release_result}`);
```

---

## 3. 关键方法映射表

| SDK 方法 | 后端 API 端点 | 功能描述 |
|---------|--------------|----------|
| `create_escrow()` | POST `/api/v1/transactions` | 创建托管交易 |
| `complete_transaction()` | POST `/api/v1/transactions/{tx_id}/complete` | 完成交易并释放资金 |
| `get_transaction()` | GET `/api/v1/transactions/{tx_id}` | 查询交易详情 |
| `get_reputation_score()` | GET `/api/v1/reputation/{address}` | 查询信誉分数 |
| `get_arbitration_fund_pool()` | GET `/api/v1/arbitration/fund-pool` | 查询仲裁基金池 |
| `check_risk_level()` | 内部逻辑 | 风险评估（基于信誉分） |

---

## 4. 错误处理规范

所有 SDK 方法应统一处理错误：

```python
try:
    result = await client.create_escrow(...)
except Black2APIError as e:
    if e.code == 4001:
        print("Invalid parameters")
    elif e.code == 5001:
        print("Fund release failed")
    else:
        print(f"Unknown error: {e.message}")
```

```javascript
try {
  const result = await client.createEscrow(...);
} catch (error) {
  if (error.code === 4001) {
    console.log('Invalid parameters');
  } else if (error.code === 5001) {
    console.log('Fund release failed');
  } else {
    console.log(`Unknown error: ${error.message}`);
  }
}
```

---

## 5. 下一步行动

1. **实现 Python SDK** - 基于 `httpx` 和 `aiohttp`
2. **实现 JavaScript SDK** - 基于 `axios` 和 `fetch`
3. **编写单元测试** - 覆盖所有核心方法
4. **发布到 PyPI/npm** - 提供正式安装包
