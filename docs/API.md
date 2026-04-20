# Black2 Clearing Protocol - API 文档

**版本**: v1.0  
**Base URL**: `http://localhost:8080/api/v1`  

---

## 认证方式

所有需要签名的接口，请求头需携带：

```
X-Public-Key: <你的公钥 hex>
X-Signature: <请求体签名 hex>
```

**签名算法**：
1. 将请求体 JSON 序列化（key 排序）
2. 计算 SHA-256 哈希
3. 用 Ed25519 私钥签名
4. 返回 hex 编码的签名

---

## 接口列表

### 1. 创建交易

**POST** `/transactions`

**请求体**：
```json
{
  "from_address": "BUYER_PUBLIC_KEY",
  "to_address": "SELLER_PUBLIC_KEY",
  "amount": 100.00,
  "currency": "USDT",
  "contract_hash": "abc123..."
}
```

**响应**：
```json
{
  "tx_id": "tx_20260420_001",
  "from_address": "BUYER_PUBLIC_KEY",
  "to_address": "SELLER_PUBLIC_KEY",
  "amount": 100.00,
  "currency": "USDT",
  "contract_hash": "abc123...",
  "status": "pending",
  "timestamp": "2026-04-20T10:00:00Z",
  "hash": "def456...",
  "signature": "ghi789..."
}
```

---

### 2. 查询交易

**GET** `/transactions/{tx_id}`

**路径参数**：
- `tx_id`: 交易 ID

**响应**：
```json
{
  "tx_id": "tx_20260420_001",
  "from_address": "BUYER_PUBLIC_KEY",
  "to_address": "SELLER_PUBLIC_KEY",
  "amount": 100.00,
  "currency": "USDT",
  "contract_hash": "abc123...",
  "file_hash": "xyz789...",
  "status": "completed",
  "timestamp": "2026-04-20T10:00:00Z",
  "hash": "def456...",
  "signature": "ghi789...",
  "anchor_hash": "jkl012...",
  "anchored_at": "2026-04-20T11:00:00Z"
}
```

---

### 3. 列表查询

**GET** `/transactions`

**查询参数**：
- `status` (可选): pending/delivered/completed/disputed/refunded
- `from_address` (可选): 买家地址
- `to_address` (可选): 卖家地址
- `limit` (可选): 返回数量，默认 100
- `offset` (可选): 偏移量，默认 0

**响应**：
```json
{
  "total": 150,
  "transactions": [
    {
      "tx_id": "tx_20260420_001",
      "from_address": "BUYER_PUBLIC_KEY",
      "to_address": "SELLER_PUBLIC_KEY",
      "amount": 100.00,
      "status": "completed",
      "timestamp": "2026-04-20T10:00:00Z"
    }
  ]
}
```

---

### 4. 验证交易

**POST** `/transactions/{tx_id}/verify`

**路径参数**：
- `tx_id`: 交易 ID

**请求体**：
```json
{
  "public_key": "SELLER_PUBLIC_KEY"
}
```

**响应**：
```json
{
  "valid": true,
  "message": "Transaction verified"
}
```

或：
```json
{
  "valid": false,
  "message": "Invalid signature"
}
```

---

### 5. 更新交易状态

**PUT** `/transactions/{tx_id}/status`

**路径参数**：
- `tx_id`: 交易 ID

**请求体**：
```json
{
  "status": "delivered",
  "file_hash": "xyz789..."
}
```

**状态流转**：
- `pending` → `delivered`（卖家提交交付物）
- `delivered` → `completed`（买家确认收货）
- `pending` → `disputed`（买家发起纠纷）
- `disputed` → `refunded`（仲裁判买家胜）
- `disputed` → `completed`（仲裁判卖家胜）

**响应**：
```json
{
  "tx_id": "tx_20260420_001",
  "status": "delivered",
  "file_hash": "xyz789...",
  "updated_at": "2026-04-20T10:30:00Z"
}
```

---

### 6. 发起纠纷

**POST** `/transactions/{tx_id}/dispute`

**路径参数**：
- `tx_id`: 交易 ID

**请求体**：
```json
{
  "reason": "File hash does not match contract"
}
```

**响应**：
```json
{
  "tx_id": "tx_20260420_001",
  "status": "disputed",
  "arbitration": {
    "verdict": "buyer_wins",
    "reason": "Contract hash does not match delivered file",
    "timestamp": "2026-04-20T10:35:00Z"
  }
}
```

---

### 7. 手动触发锚定

**POST** `/anchor/trigger`

**请求体**：无

**响应**：
```json
{
  "success": true,
  "root_hash": "mno345...",
  "anchor_url": "https://gist.github.com/xxx/yyy",
  "transaction_count": 150,
  "timestamp": "2026-04-20T11:00:00Z"
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 签名验证失败 |
| 404 | 交易不存在 |
| 409 | 交易状态冲突（例如已完成不能再次提交） |
| 500 | 服务器内部错误 |

**错误响应格式**：
```json
{
  "error": "INVALID_SIGNATURE",
  "message": "Signature verification failed"
}
```

---

## SDK 示例

### Python

```python
import httpx
import json
import hashlib
import nacl.signing

# 配置
API_BASE = "http://localhost:8080/api/v1"
PRIVATE_KEY_HEX = "your_private_key_hex"
PUBLIC_KEY_HEX = "your_public_key_hex"

def sign_request(data: dict) -> str:
    """签名请求体"""
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    hash_hex = hashlib.sha256(json_str.encode()).hexdigest()
    
    signing_key = nacl.signing.SigningKey(PRIVATE_KEY_HEX.encode(), encoder=nacl.encoding.HexEncoder)
    signature = signing_key.sign(hash_hex.encode()).signature.hex()
    
    return signature

# 创建交易
tx_data = {
    "from_address": PUBLIC_KEY_HEX,
    "to_address": "SELLER_PUBLIC_KEY",
    "amount": 100.00,
    "currency": "USDT",
    "contract_hash": "abc123..."
}

signature = sign_request(tx_data)

response = httpx.post(
    f"{API_BASE}/transactions",
    json=tx_data,
    headers={
        "X-Public-Key": PUBLIC_KEY_HEX,
        "X-Signature": signature
    }
)

print(response.json())
```

### JavaScript

```javascript
const axios = require('axios');
const crypto = require('crypto');
const nacl = require('tweetnacl');

// 配置
const API_BASE = 'http://localhost:8080/api/v1';
const PRIVATE_KEY_HEX = 'your_private_key_hex';
const PUBLIC_KEY_HEX = 'your_public_key_hex';

function signRequest(data) {
    const jsonStr = JSON.stringify(data, Object.keys(data).sort());
    const hash = crypto.createHash('sha256').update(jsonStr).digest('hex');
    
    const privateKey = Buffer.from(PRIVATE_KEY_HEX, 'hex');
    const message = Buffer.from(hash);
    const signature = nacl.sign.detached(message, privateKey);
    
    return Buffer.from(signature).toString('hex');
}

// 创建交易
const txData = {
    from_address: PUBLIC_KEY_HEX,
    to_address: 'SELLER_PUBLIC_KEY',
    amount: 100.00,
    currency: 'USDT',
    contract_hash: 'abc123...'
};

const signature = signRequest(txData);

axios.post(`${API_BASE}/transactions`, txData, {
    headers: {
        'X-Public-Key': PUBLIC_KEY_HEX,
        'X-Signature': signature
    }
}).then(response => {
    console.log(response.data);
});
```

---

## 速率限制

- 普通用户：100 请求/分钟
- 企业用户：1000 请求/分钟

超出限制返回 `429 Too Many Requests`。

---

**文档维护者**: Black2 Team  
**最后更新**: 2026-04-20
