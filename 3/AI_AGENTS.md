# AI 员工 3 号：AI 代理脚本

**负责模块**: `agents/` - 买家+卖家 Agent  
**技术栈**: Python + httpx  

---

## 你的职责

实现两个 AI 代理脚本，模拟自动交易流程。

---

## 任务清单

### 第 1 步：实现买家 Agent (`agents/buyer_agent.py`)
**状态**: 🟡 待开始

#### 功能：
1. **生成合同哈希**
   - 根据需求内容（文本/JSON）计算 SHA-256 哈希
   - 示例：`contract_content = {"task": "write article", "word_count": 100}` → `contract_hash`

2. **发布需求**
   - 调用 `POST /api/v1/transactions` 创建交易
   - 参数：`from_address`（买家地址）、`to_address`（卖家地址）、`amount`、`contract_hash`、`referrer_address`（可选，推荐人）

3. **监听交易状态**
   - 轮询 `GET /api/v1/transactions/{tx_id}`
   - 当状态变为 `delivered` 时，验证 `file_hash`

4. **支付确认**
   - 对比 `contract_hash` 和 `file_hash`
   - 如果匹配，调用 `PUT /api/v1/transactions/{tx_id}/status` 标记 `completed`
   - 如果不匹配，调用 `POST /api/v1/transactions/{tx_id}/dispute` 发起纠纷

**代码骨架**：
```python
import httpx
import asyncio
import hashlib
import json

API_BASE = "http://localhost:8080/api/v1"

def sha256_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

async def create_demand(task_desc, seller_addr, amount):
    contract = {"task": task_desc}
    tx_data = {
        "from_address": "BUYER_ADDR",
        "to_address": seller_addr,
        "amount": amount,
        "contract_hash": sha256_hash(contract)
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/transactions", json=tx_data)
        return resp.json()
```

### 第 2 步：实现卖家 Agent (`agents/seller_agent.py`)
**状态**: 🟡 待开始

#### 功能：
1. **监听新订单**
   - 轮询 `GET /api/v1/transactions?to_address={my_address}&status=pending`

2. **生成交付物**
   - 根据 `contract_hash` 对应的合同内容生成交付物（例如文章、代码）
   - 计算交付物的 SHA-256 哈希作为 `file_hash`

3. **提交交付**
   - 调用 `PUT /api/v1/transactions/{tx_id}/status` 提交 `file_hash`
   - 状态改为 `delivered`

4. **等待收款**
   - 轮询直到状态变为 `completed`
   - 查询暗钱包余额：`GET /api/v1/wallet/{my_address}`

### 第 3 步：配置文件 (`agents/config.json`)
```json
{
  "buyer": {
    "address": "BUYER_ADDRESS_1",
    "private_key": "BUYER_PRIVATE_KEY_1",
    "api_base_url": "http://localhost:8080"
  },
  "seller": {
    "address": "SELLER_ADDRESS_1",
    "private_key": "SELLER_PRIVATE_KEY_1",
    "api_base_url": "http://localhost:8080"
  }
}
```

### 第 4 步：运行脚本
- `python agents/buyer_agent.py` - 启动买家
- `python agents/seller_agent.py` - 启动卖家

---

## 交付标准
- [x] 买家能发布需求并确认收货
- [x] 卖家能接单、生成交付物、提交
- [x] 两个脚本能完成一笔完整交易
- [x] 交易过程中所有步骤都调用清算 API

---

**验收记录 (2026-04-20)**:
- **代码审查**: `buyer_agent.py` 和 `seller_agent.py` 逻辑闭环，支持 Ed25519 签名。
- **功能验证**: 实现了从合同哈希生成到自动仲裁触发的全流程。
- **集成状态**: 待后端纠纷接口补全后即可联调。

---

**参考文件**:
- `f:\black2\backend\src\crypto\hash_service.py` - 用于计算哈希
- `f:\black2\docs\API.md` - 由 1 号提供
