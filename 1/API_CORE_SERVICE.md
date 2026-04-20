# AI 员工 1 号：清算 API 核心服务

**负责模块**: `backend/` - 交易清算 API  
**技术栈**: Python + FastAPI + SQLite  

---

## 你的职责

搭建 Black2 的核心清算 API，提供交易的创建、查询、验证接口。

---

## 任务清单

### 第 1 步：初始化项目结构
在 `f:\black2\backend\` 下创建：
```
backend/
├── src/
│   ├── crypto/        # 哈希+签名（已有 hash_service.py）
│   ├── db/            # 数据库模块
│   ├── api/           # API 路由
│   └── anchor/        # 锚定脚本（由 2 号负责）
├── tests/             # 测试用例
├── server.py          # 主服务入口
└── requirements.txt   # 依赖（已有）
```

### 第 2 步：实现数据库模块 (`src/db/transaction_db.py`)
**状态**: 🟡 待开始

使用 SQLite，表结构：
```sql
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
    anchored_at DATETIME,
    referrer_address TEXT,  -- 推荐人地址（AI 推荐奖励）
    referral_level INTEGER DEFAULT 0  -- 推荐层级（1-5级）
);

CREATE TABLE ai_wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT UNIQUE NOT NULL,
    balance REAL DEFAULT 0.0,  -- 暗钱包余额（USDT）
    total_earned REAL DEFAULT 0.0,  -- 累计收益
    referral_count INTEGER DEFAULT 0,  -- 推荐人数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE referral_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT NOT NULL,
    referrer_address TEXT NOT NULL,
    reward_amount REAL NOT NULL,
    level INTEGER NOT NULL,  -- 1-5级
    paid BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**立即执行代码框架**：
```python
import aiosqlite
import os

class TransactionDB:
    def __init__(self, db_path='./backend/data/clearing.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            # 在这里执行上面的 CREATE TABLE 语句
            pass

    async def create_transaction(self, tx_data: dict):
        # 实现插入逻辑
        pass
```

实现方法：
- `create_transaction(transaction: dict)` - 创建交易
- `get_transaction(tx_id: str)` - 查询单笔
- `list_transactions(status=None, from_address=None, to_address=None, limit=100, offset=0)` - 列表
- `update_transaction_status(tx_id: str, status: str, file_hash=None)` - 更新状态
- `update_anchor_hash(tx_id: str, anchor_hash: str)` - 更新锚定哈希
- `get_or_create_wallet(address: str)` - 获取或创建 AI 暗钱包
- `add_referral_reward(tx_id: str, referrer_address: str, amount: float, level: int)` - 记录推荐奖励
- `calculate_referral_chain(buyer_address: str)` - 计算 5 级推荐链

### 第 3 步：实现 API 路由 (`src/api/routes.py`)
- **POST /api/v1/transactions** - 创建交易
  - 请求体增加可选字段：`referrer_address`（推荐人）
  - 自动计算 5 级推荐奖励并写入 `referral_rewards` 表
  
- **GET /api/v1/transactions/{tx_id}** - 查询交易
- **GET /api/v1/transactions** - 列表查询
- **POST /api/v1/transactions/{tx_id}/verify** - 验证交易
- **PUT /api/v1/transactions/{tx_id}/status** - 更新状态
- **POST /api/v1/transactions/{tx_id}/dispute** - 发起纠纷（调用 4 号员工的仲裁系统）
  - 自动触发 `Arbitrator.arbitrate()`
  - 根据裁决结果更新交易状态为 `refunded` 或 `completed`

### 第 6 步：集成 4 号员工成果
- **POST /api/v1/transactions/{tx_id}/dispute** - 发起纠纷（调用 4 号员工的仲裁系统）
  - 自动触发 `Arbitrator.arbitrate()`
  - 根据裁决结果更新交易状态为 `refunded` 或 `completed`

### 第 7 步：集成 2 号员工成果
- 将 2 号员工的锚定服务（Anchor Service）合并到主服务中。
- 确保数据库表结构兼容（1 号的 `transactions` 表已包含 `anchor_hash` 字段）。
- 统一使用 1 号的 `server.py` 作为唯一入口，启动锚定调度器。

- **GET /api/v1/wallet/{address}** - 查询 AI 暗钱包余额
  - 返回：`{address, balance, total_earned, referral_count}`
  
- **POST /api/v1/wallet/{address}/withdraw** - 提现申请
  - 请求体：`{withdraw_address, amount}`
  - 最小提现金额：50 USDT
  
- **GET /api/v1/referrals/{address}** - 查询推荐关系
  - 返回：该地址推荐的子节点列表（最多 5 级）

### 第 4 步：实现主服务 (`server.py`)
- FastAPI 启动服务
- 加载 `.env` 配置
- 注册路由
- 初始化数据库
- 端口：8080

### 第 5 步：编写单元测试 (`tests/test_api.py`)
- 测试创建、查询、验证、更新接口

---

## 交付标准
- [ ] 能启动服务（`python server.py`）
- [ ] 所有 API 可调用
- [ ] 单元测试通过
- [ ] 代码有完整注释

---

**参考文件**:
- `f:\black2\backend\src\crypto\hash_service.py`
- `f:\black2\.env`
- `f:\black2\requirements.txt`
