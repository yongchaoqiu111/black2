# Black2 后端开发标准规范（AI 优先）

> **核心原则**：本项目是 **AI 交易基础设施**，所有功能围绕 AI 钱包设计和优化。人类钱包仅作为辅助充值渠道。

---

## 📋 目录

1. [数据库横向分表设计](#1-数据库横向分表设计)
2. [API 调用频率限制](#2-api-调用频率限制)
3. [异步队列处理高并发](#3-异步队列处理高并发)
4. [订单系统架构](#4-订单系统架构)
5. [分润计算规范](#5-分润计算规范)

---

## 1. AI 钱包优先原则

### 核心定位
**Black2 是 AI 交易基础设施**，所有业务逻辑围绕 **AI 钱包** 设计：
- ✅ AI 钱包：用于交易、分润、结算（主钱包）
- ⚠️ 人类钱包：仅用于充值到 AI 钱包（辅助渠道）

### 开发规范

#### 1.1 订单扣款从 AI 钱包
```python
# ✅ 正确：从 AI 钱包扣款
await db.execute(
    'UPDATE ai_wallets SET balance = balance - ? WHERE address = ?',
    (amount, ai_address)
)

# ❌ 错误：从人类钱包扣款
await db.execute(
    'UPDATE human_wallets SET points_balance = points_balance - ? ...',
    ...
)
```

#### 1.2 分润写入 AI 钱包
```python
# ✅ 正确：分润同时更新两个表
await db.execute(
    'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
    (amount, ai_address)
)
await db.execute(
    'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
    (amount, ai_address)
)
```

#### 1.3 查询钱包使用 AI 地址
```python
# ✅ 正确：用 AI 地址查 AI 钱包
ai_response = await walletApi.getAIWallet(ai_wallet_address)

# ❌ 错误：用人类地址查 AI 钱包
ai_response = await walletApi.getAIWallet(human_wallet_address)
```

---

## 2. 数据库横向分表设计

### 核心原则

**服务 AI 查询优化**：将高频查询和低频查询的数据分离到不同的表中，减少单次查询的数据量，提升响应速度。

### 设计规范

#### ❌ 错误做法（纵向宽表）

```sql
-- 所有字段都在一张表里
CREATE TABLE transactions (
    tx_id TEXT,
    from_address TEXT,
    to_address TEXT,
    amount REAL,
    -- 分润字段（低频使用）
    tu1_address TEXT,
    tu1_amount REAL,
    tu2_address TEXT,
    tu2_amount REAL,
    tu3_address TEXT,
    tu3_amount REAL,
    settlement_status TEXT,
    -- 仲裁字段（极少使用）
    dispute_reason TEXT,
    verdict TEXT,
    ...
);
```

**问题**：
- AI 查询订单列表时，每次加载全部字段
- 数据量大 → 内存占用高 → 查询慢
- 无法按需加载

---

#### ✅ 正确做法（横向分表）

```sql
-- 表1: 订单基础信息（高频查询）
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT UNIQUE NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USDT',
    contract_hash TEXT NOT NULL,
    file_hash TEXT,
    status TEXT DEFAULT 'pending',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    hash TEXT NOT NULL,
    signature TEXT NOT NULL,
    anchor_hash TEXT,
    anchored_at DATETIME
);

-- 表2: 分润信息（低频查询）
CREATE TABLE transaction_referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT UNIQUE NOT NULL,
    tu1_address TEXT,
    tu1_amount REAL DEFAULT 0,
    tu2_address TEXT,
    tu2_amount REAL DEFAULT 0,
    tu3_address TEXT,
    tu3_amount REAL DEFAULT 0,
    settlement_status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    settled_at DATETIME,
    FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
);

-- 表3: 仲裁记录（条件查询）
CREATE TABLE transaction_arbitrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT UNIQUE NOT NULL,
    dispute_reason TEXT,
    verdict TEXT,  -- 'buyer_wins' | 'seller_wins'
    arbitration_result TEXT,
    resolved_at DATETIME,
    FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
);
```

**优势**：
- AI 查询订单列表：只查 `transactions` 表（轻量）
- 需要分润详情：才 JOIN `transaction_referrals` 表
- 需要仲裁记录：才 JOIN `transaction_arbitrations` 表
- **降低服务器压力，提升查询性能**

---

### 查询示例

#### 场景1：AI 查询订单列表（高频）

```python
# 只查基础信息，不加载分润和仲裁数据
query = '''
    SELECT * FROM transactions 
    WHERE from_address = ? 
    ORDER BY timestamp DESC 
    LIMIT 50 OFFSET 0
'''
```

#### 场景2：查询订单详情（含分润）

```python
# LEFT JOIN 分润表
query = '''
    SELECT t.*, 
           r.tu1_address, r.tu1_amount, 
           r.tu2_address, r.tu2_amount, 
           r.tu3_address, r.tu3_amount, 
           r.settlement_status
    FROM transactions t
    LEFT JOIN transaction_referrals r ON t.tx_id = r.tx_id
    WHERE t.tx_id = ?
'''
```

#### 场景3：查询仲裁记录

```python
# LEFT JOIN 仲裁表
query = '''
    SELECT t.*, a.dispute_reason, a.verdict, a.resolved_at
    FROM transactions t
    LEFT JOIN transaction_arbitrations a ON t.tx_id = a.tx_id
    WHERE t.tx_id = ?
'''
```

---

## 2. API 调用频率限制

### 核心原则

**防止 AI 滥用接口**：对所有可能被频繁调用的 API 接口实施频率限制，保护服务器资源。

### 实施规范

#### 步骤1：导入限流器

```python
from src.utils.rate_limiter import rate_limiter
from fastapi import HTTPException
```

#### 步骤2：在路由函数中应用限流

```python
@router.get("/api/v1/transactions")
async def list_all_transactions(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List transactions with optional filters.
    
    Rate limit: 1 request per 60 seconds per IP
    """
    # 获取客户端标识（IP 或用户ID）
    client_ip = "unknown"  # 生产环境从 request.headers 获取
    
    # 检查限流（60秒间隔）
    allowed, remaining = rate_limiter.is_allowed(
        f"list_tx_{client_ip}", 
        interval=60
    )
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please wait {remaining} seconds before next query."
        )
    
    # 正常业务逻辑
    transactions = await list_transactions(...)
    return transactions
```

---

### 限流策略参考

| API 类型 | 限流间隔 | 说明 |
|---------|---------|------|
| 订单列表查询 | 60秒 | 防止频繁拉取大量数据 |
| 用户信息查询 | 30秒 | 防止频繁查询用户详情 |
| 余额查询 | 10秒 | 允许较频繁查询 |
| 创建订单 | 5秒 | 防止恶意刷单 |
| 提交仲裁 | 300秒 | 防止滥用仲裁 |

---

### 分页限制

**所有列表接口必须设置分页上限**：

```python
limit: int = Query(
    default=50,      # 默认每页50条
    ge=1,            # 最小1条
    le=100           # 最大100条（防止一次性查太多）
)
```

**禁止**：
```python
limit: int = Query(default=1000, le=10000)  # ❌ 太大
limit: int = Query(default=100, le=None)     # ❌ 无上限
```

---

## 3. 异步队列处理高并发

### 核心原则

**避免同步写入导致数据库锁**：将非关键路径的写操作放入 Redis 队列，由后台 worker 异步处理。

### 适用场景

✅ **应该用异步队列**：
- 订单创建后写入分润记录
- 订单完成后结算分润
- 发送通知邮件/消息
- 生成统计报表

❌ **不应该用异步队列**：
- 订单创建本身（必须同步保证成功）
- 用户注册（必须同步返回结果）
- 支付确认（必须同步更新状态）

---

### 实施步骤

#### 步骤1：定义 Worker 任务

```python
# src/utils/settlement_worker.py

def process_referral_creation(
    tx_id: str, 
    tu1_addr: str, tu1_amount: float,
    tu2_addr: str, tu2_amount: float,
    tu3_addr: str, tu3_amount: float
):
    """
    异步创建分润记录
    """
    print(f"[Referral Worker] Creating referral record for order {tx_id}")
    asyncio.run(_process_referral_creation_async(...))


async def _process_referral_creation_async(...):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO transaction_referrals 
            (tx_id, tu1_address, tu1_amount, ...)
            VALUES (?, ?, ?, ...)
        ''', (tx_id, tu1_addr, tu1_amount, ...))
        await db.commit()
```

#### 步骤2：在主流程中推入队列

```python
# src/api/routes.py - 创建订单

@router.post("/api/v1/transactions")
async def create_transaction(transaction: TransactionCreate):
    # 1. 同步写入订单基础信息（必须成功）
    created_tx = await create_transaction(transaction)
    
    # 2. 计算分润数据
    tu1_amount = round(transaction.amount * 0.05, 2)
    tu2_amount = round(transaction.amount * 0.03, 2)
    tu3_amount = round(transaction.amount * 0.02, 2)
    
    # 3. 异步写入分润记录（失败不影响订单创建）
    try:
        from src.utils.redis_queue import referral_queue
        from src.utils.settlement_worker import process_referral_creation
        
        referral_queue.enqueue(
            process_referral_creation,
            tx_id, tu1_addr, tu1_amount,
            tu2_addr, tu2_amount,
            tu3_addr, tu3_amount
        )
    except Exception as e:
        print(f"[Warning] Failed to queue referral creation: {e}")
        # 注意：这里不抛出异常，订单仍然创建成功
    
    return {"message": "Order created", "tx_id": tx_id}
```

---

### 优势

1. **订单创建快**：不因分润写入失败而阻塞
2. **数据库不锁**：异步写入分散了数据库压力
3. **削峰填谷**：高并发时队列缓冲，worker 慢慢处理
4. **容错性强**：worker 失败可以重试，不影响主流程

---

## 4. 订单系统架构

### 订单生命周期

```
创建订单 (pending)
    ↓
买家付款 (paid)
    ↓
卖家发货 (shipped)
    ↓
┌──────────────┬──────────────┐
│              │              │
确认收货      申请仲裁       超时自动确认
(completed)   (disputed)     (completed)
    ↓              ↓
  开始分钱    ┌────┴────┐
              │         │
          卖家赢     买家赢
        (completed)  (refunded)
              ↓         ↓
           开始分钱   退款+取消分润
```

---

### 三种完成方式

#### 方式1：买家确认收货

```python
POST /api/v1/transactions/{tx_id}/complete
```

**流程**：
1. 订单状态 → `completed`
2. 推送结算任务到 Redis 队列
3. Worker 异步分润给三代推荐人
4. 卖家收到 90%

---

#### 方式2：仲裁 → 卖家赢

```python
POST /api/v1/transactions/{tx_id}/dispute
{
  "reason": "商品有问题",
  "evidence": "..."
}
```

**判断逻辑**：
```python
if contract_hash == file_hash:
    # 货对版 → 卖家赢
    verdict = "seller_wins"
    status = "completed"
    # 开始分钱
else:
    # 货不对版 → 买家赢
    verdict = "buyer_wins"
    status = "refunded"
    # 退款 + 取消分润
```

---

#### 方式3：仲裁 → 买家赢

**流程**：
1. 订单状态 → `refunded`
2. 调用 `cancel_referral_rewards(tx_id)` 取消分润
3. 退款给买家
4. 卖家信用扣分

---

## 5. 分润计算规范

### 分润比例

- **tu1（直接推荐人）**：5%
- **tu2（二代推荐人）**：3%
- **tu3（三代推荐人）**：2%
- **卖家**：90%

---

### 四舍五入规则

```python
# ✅ 正确做法
tu1_amount = round(transaction.amount * 0.05, 2)
tu2_amount = round(transaction.amount * 0.03, 2)
tu3_amount = round(transaction.amount * 0.02, 2)

# 确保分润总额不超过订单金额
total_commission = tu1_amount + tu2_amount + tu3_amount
if total_commission > transaction.amount:
    # 按比例缩减
    tu1_amount = round(tu1_amount / total_commission * transaction.amount, 2)
    tu2_amount = round(tu2_amount / total_commission * transaction.amount, 2)
    tu3_amount = round(tu3_amount / total_commission * transaction.amount, 2)
```

**示例**：
- 订单金额：299 USDT
- tu1: 299 × 0.05 = 14.95
- tu2: 299 × 0.03 = 8.97
- tu3: 299 × 0.02 = 5.98
- 总计：29.90 ≤ 299 ✓
- 卖家：299 - 29.90 = 269.10

---

### 防超额约束

**绝对不允许**分润总额超过订单金额：

```python
# ❌ 错误：可能导致分润超过订单金额
tu1_amount = transaction.amount * 0.05  # 可能除不尽

# ✅ 正确：四舍五入 + 总额校验
tu1_amount = round(transaction.amount * 0.05, 2)
if tu1_amount + tu2_amount + tu3_amount > transaction.amount:
    # 调整...
```

---

## 6. 多链钱包架构（未来扩展）

### 核心问题

**多链支持需求**：当前仅支持 TRC-20（波场链），但未来可能需要支持 ERC-20（以太坊）、BSC（币安智能链）等其他链。

### 6.1 当前状态（v1.0）

- ✅ **单链支持**：仅支持 TRC-20（波场链）
- ✅ **数据库设计**：`ai_wallets` 和 `human_wallets` 表只存储地址，不绑定特定链
- ✅ **HD 钱包派生**：母钱包支持多链子钱包派生（TRON/ETH/BSC）

```python
# 当前实现
ai_wallets 表：
{
    "address": "TGmNWoN5bRwf1rpcr4MbojTvdHyC2vh5jf",  # TRON 地址
    "balance": 1000.0,
    "total_earned": 50.0,
    ...
}
```

### 6.2 多链扩展方案

#### 方案 A：数据库加 `chain` 字段（推荐）

```sql
-- v1.0 现有结构
CREATE TABLE ai_wallets (
    address TEXT PRIMARY KEY,
    balance REAL DEFAULT 0,
    ...
);

-- v2.0 扩展方案
ALTER TABLE ai_wallets ADD COLUMN chain TEXT DEFAULT 'TRON';

-- 新增索引提升查询性能
CREATE INDEX idx_ai_wallets_chain ON ai_wallets(chain);
CREATE INDEX idx_ai_wallets_chain_address ON ai_wallets(chain, address);
```

**多链地址示例**：
- TRON: `TGmNWoN5bRwf1rpcr4MbojTvdHyC2vh5jf`
- ETH: `0x742d35Cc6634C0532925a3b844Bc9e7595f2bD88`
- BSC: `0x742d35Cc6634C0532925a3b844Bc9e7595f2bD88`

#### 方案 B：用户接入自有钱包

**特点**：
- 前端 Web3 连接（MetaMask/TronLink/OKX Wallet）
- 后端只验证签名，不管理私钥
- 支持任意链和任意钱包

**实施要点**：
```python
# 用户连接钱包时，只保存地址，不生成新钱包
@router.post("/api/v1/wallets/connect")
async def connect_wallet(data: ConnectWalletRequest):
    """
    用户连接自有钱包
    """
    # 验证签名（确保用户拥有该钱包的私钥）
    is_valid = verify_signature(data.address, data.signature, data.message)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 保存钱包地址到数据库（如果不存在）
    await db.execute(
        'INSERT OR IGNORE INTO ai_wallets (address, chain) VALUES (?, ?)',
        (data.address, data.chain)
    )
    
    return {"message": "Wallet connected", "address": data.address}
```

### 6.3 升级路径

#### v1.0 → v1.1：添加多链支持

**步骤**：
1. 数据库迁移：添加 `chain` 字段
2. 给老用户派生新链子钱包（ETH、BSC）
3. 订单创建 API 添加 `chain` 参数
4. 前端支持链选择器

```python
# 订单创建 API 扩展
@router.post("/api/v1/transactions")
async def create_transaction(transaction: TransactionCreate):
    """
    创建订单，支持多链
    """
    # 验证钱包地址属于指定链
    if not validate_chain_address(transaction.from_address, transaction.chain):
        raise HTTPException(status_code=400, detail=f"Invalid {transaction.chain} address")
    
    # 从指定链的 AI 钱包扣款
    await db.execute(
        'UPDATE ai_wallets SET balance = balance - ? WHERE address = ? AND chain = ?',
        (transaction.amount, transaction.from_address, transaction.chain)
    )
    
    ...
```

#### v1.1 → v2.0：支持自有钱包接入

**步骤**：
1. 添加钱包连接 API（MetaMask/TronLink）
2. 修改签名验证逻辑
3. 前端集成 Web3 库（ethers.js / tronweb）

### 6.4 换链迁移方案

**场景**：需要将用户从 TRON 链迁移到 ETH 链

**流程**：
1. 为每个用户派生 ETH 子钱包（同一助记词）
2. 查询用户 TRON 钱包余额
3. 自动将余额记录到 ETH 钱包（链上实际转账或数据库记录）
4. 通知用户完成迁移

```python
async def migrate_user_chain(user_address: str, from_chain: str, to_chain: str):
    """
    用户链迁移
    """
    # 1. 查询原链钱包余额
    cursor = await db.execute(
        'SELECT balance FROM ai_wallets WHERE address = ? AND chain = ?',
        (user_address, from_chain)
    )
    row = await cursor.fetchone()
    balance = row[0] if row else 0
    
    # 2. 生成新链子钱包地址（从母钱包派生）
    new_address = hd_wallet.derive_address(chain=to_chain)
    
    # 3. 创建新链钱包记录
    await db.execute(
        'INSERT INTO ai_wallets (address, chain, balance) VALUES (?, ?, ?)',
        (new_address, to_chain, balance)
    )
    
    # 4. 更新用户关联
    await db.execute(
        'UPDATE users SET ai_wallet_address = ? WHERE ai_wallet_address = ?',
        (new_address, user_address)
    )
    
    await db.commit()
    
    return {
        "old_address": user_address,
        "new_address": new_address,
        "balance": balance,
        "from_chain": from_chain,
        "to_chain": to_chain
    }
```

### 6.5 实施要点

#### 链上交互层抽象

```python
# ❌ 错误：硬编码 TRON 链
from src.crypto.tron_chain import tron_chain
balance = await tron_chain.get_balance(address)

# ✅ 正确：使用链适配器
from src.crypto.chain_adapter import ChainAdapter

chain_adapter = ChainAdapter(chain="TRON")  # 或 "ETH", "BSC"
balance = await chain_adapter.get_balance(address)
```

#### 充值监听多链

```python
# 监听多个链的充值事件
async def monitor_deposits():
    chains = ["TRON", "ETH", "BSC"]
    
    for chain in chains:
        adapter = ChainAdapter(chain=chain)
        deposits = await adapter.get_recent_deposits()
        
        for deposit in deposits:
            await process_deposit(deposit, chain)
```

#### 前端链选择器

```vue
<!-- 前端组件 -->
<select v-model="selectedChain">
  <option value="TRON">TRC-20 (波场)</option>
  <option value="ETH">ERC-20 (以太坊)</option>
  <option value="BSC">BEP-20 (币安)</option>
</select>
```

### 6.6 核心优势

1. **增量扩展**：多链支持不需要重构现有代码
2. **向后兼容**：v1.0 的订单数据不受影响
3. **用户无感**：换链迁移自动完成，用户无需手动操作
4. **灵活接入**：支持自有钱包和平台钱包两种方式

### 6.7 风险与注意事项

⚠️ **注意事项**：
- 不同链的交易手续费差异大（TRON ~$0.001, ETH ~$1-10）
- 链上确认时间不同（TRON ~3秒, ETH ~15秒）
- 需要维护多个链的节点连接
- 跨链转账需要额外处理（不建议做）

⚠️ **不建议**：
- ❌ 跨链自动转账（成本高、风险大）
- ❌ 混合链钱包（一个地址多链共用，容易混淆）
- ❌ 自动链切换（用户可能不知道自己在哪条链）

---

## 7. 测试规范

### 完成的功能

1. **订单购买流程**
   - ✅ ProductDetail.vue 实现"立即购买"功能
   - ✅ 调用后端 API 创建订单
   - ✅ 自动生成 contract_hash
   - ✅ 跳转到订单列表

2. **订单管理系统**
   - ✅ Orders.vue 从后端 API 加载订单
   - ✅ OrderDetail.vue 显示订单详情
   - ✅ 确认收货按钮 → 触发分润
   - ✅ 申请仲裁按钮 → 触发仲裁流程

3. **数据库横向分表**
   - ✅ 创建 `transaction_referrals` 表
   - ✅ 迁移脚本执行成功
   - ✅ 修改 `list_transactions` 为 JOIN 查询
   - ✅ 修改 `get_transaction` 为 JOIN 查询

4. **异步队列优化**
   - ✅ 订单创建时分润数据推入 Redis 队列
   - ✅ Worker 异步写入 `transaction_referrals` 表
   - ✅ 避免高并发时数据库锁

5. **API 限流保护**
   - ✅ 订单列表查询限流：60秒一次
   - ✅ 分页限制：默认50条，最大100条
   - ✅ 超限返回 429 错误

6. **分润计算优化**
   - ✅ 四舍五入到 2 位小数
   - ✅ 防超额校验：分润总额 ≤ 订单金额

---

### 核心决策记录

| 决策 | 原因 | 影响 |
|-----|------|-----|
| 数据库横向分表 | 服务 AI 查询优化，降低单次查询数据量 | 提升查询性能，降低内存占用 |
| API 频率限制 | 防止 AI 滥用接口，保护服务器资源 | 避免服务器过载，提升稳定性 |
| 异步队列写入 | 避免高并发时数据库锁 | 订单创建更快，容错性更强 |
| 分润预写策略 | 订单创建时就计算好分润，避免结算时再算 | 减少结算时的计算压力 |
| 前端硬编码静态数据 | 合同模板等静态数据不需要后端返回 | 减少 API 调用，提升加载速度 |

---

## 🔧 技术栈

- **后端框架**：FastAPI + Python 3.10+
- **数据库**：SQLite（开发）→ PostgreSQL（生产）
- **缓存/队列**：Redis + RQ（Redis Queue）
- **前端框架**：Vue 3 + Vite + Pinia
- **区块链**：Tron HD Wallet

---

## 📚 相关文档

- [API 文档](../API_DOC.md)
- [白皮书](../AI与AI可信交易协议白皮书（精简版）.md)
- [架构设计](../docs/ARCHITECTURE.md)

---

**最后更新**：2026-04-22  
**维护者**：Black2 开发团队
