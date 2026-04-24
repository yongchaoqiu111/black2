# X402 锚点服务与仲裁引擎集成

## 项目概述

本项目完整实现了 Black2 协议中的 X402 链上存证、仲裁引擎以及异步任务处理功能，增强了仲裁结果的公信力，并通过异步架构优化了后端性能。

### 核心特性

1. **双重锚定机制**
   - GitHub 作为主要公共账本
   - X402 链上数据作为补充验证层
   - 防止 GitHub 仓库篡改，确保证据链永久有效

2. **仲裁引擎与异步联动**
   - 仲裁倒计时管理（默认 48 小时）
   - 异步裁决执行与资金释放
   - X402 链上交易提交与锚定

3. **高性能架构**
   - 异步任务处理，避免阻塞 API 响应
   - 批量结算，降低 Gas 成本
   - 多链容灾配置

4. **完整的测试覆盖**
   - X402 集成测试
   - 仲裁引擎测试
   - 异步任务处理测试

5. **完整的 REST API**
   - 仲裁结果锚定
   - 批量交易锚定
   - 仲裁倒计时管理
   - 裁决手动执行
   - 状态查询
   - 健康检查

## 项目结构

```
f:\black2\2\
├── backend/
│   ├── src/
│   │   ├── anchor/
│   │   │   ├── __init__.py              # 模块导出
│   │   │   ├── x402_anchor.py           # X402 链上锚定服务
│   │   │   ├── github_anchor.py         # GitHub 锚定服务
│   │   │   ├── dual_anchor.py           # 双重锚定集成服务
│   │   │   └── arbitration_timer.py     # 仲裁计时器服务（核心）
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── transaction_db.py        # 交易数据库模块
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── async_task_processor.py  # 异步任务处理系统
│   │   └── x402/
│   │       ├── __init__.py
│   │       └── bridge.py                # X402 支付桥接
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_x402_integration.py     # X402 集成测试
│   │   └── test_arbitration_integration.py  # 仲裁引擎测试
│   ├── server.py                        # FastAPI 主服务
│   └── check_imports.py                 # 导入检查脚本
├── .env.example                         # 配置示例
├── requirements.txt                     # Python 依赖
├── X402_ANCHOR_TASK.md                 # 原始任务文档
├── INTEGRATION_ARBITRATION_TASK.md     # 仲裁集成任务
├── ARCHITECTURE_CONTEXT.md             # 架构上下文
└── README.md                            # 本文件
```

## 核心模块说明

### 1. ArbitrationTimerService (arbitration_timer.py) ⭐

**这是本次任务的核心模块！**

- **功能**：仲裁倒计时管理与异步裁决执行
- **核心特性**：
  - 启动仲裁倒计时（默认 48 小时）
  - 超时后自动执行仲裁逻辑
  - 通过 AsyncTaskProcessor 实现非阻塞的资金释放与锚定
  - 实现 `execute_arbitration_verdict()` 用于手动触发裁决
  - 待处理任务自动重试机制

- **关键方法**：
  - `start_arbitration_countdown()`: 启动仲裁倒计时
  - `execute_arbitration_verdict()`: 手动执行裁决（异步）
  - `_release_funds_and_anchor()`: 资金释放与锚定回调（核心！）
  - `cancel_countdown()`: 取消倒计时
  - `initialize_pending_arbitrations()`: 服务启动时恢复待处理仲裁

### 2. X402OnChainAnchor (x402_anchor.py)

- **功能**：将 GitHub Commit Hash 锚定到 X402 支持的公链
- **特性**：
  - 支持 6 条链：Ethereum, Base, Arbitrum, Optimism, Polygon, BNB
  - Merkle Tree 批量处理
  - 自动降级策略
- **主要方法**：
  - `anchor_commit_hash()`: 单次锚定
  - `batch_anchor()`: 批量锚定
  - `switch_chain()`: 链切换

### 3. DualAnchorService (dual_anchor.py)

- **功能**：整合 GitHub 锚定与 X402 链上锚定
- **特性**：
  - 自动重试机制（最多 3 次）
  - 仲裁结果锚定
  - 批量交易锚定
- **主要方法**：
  - `anchor_arbitration_result()`: 锚定仲裁结果
  - `anchor_batch_with_x402()`: 批量锚定
  - `retry_pending_chain_anchors()`: 重试待处理任务

### 4. AsyncTaskProcessor (async_task_processor.py)

- **功能**：后台异步任务处理系统
- **特性**：
  - 多工作池（可配置）
  - 任务队列（防溢出）
  - 指数退避重试
- **主要方法**：
  - `submit_task()`: 提交任务
  - `start()/stop()`: 启停控制
  - `get_stats()`: 获取统计

### 5. X402Bridge (x402/bridge.py)

- **功能**：X402 支付桥接层
- **特性**：
  - Escrow 支付发起
  - 裁决后的资金释放
  - 余额查询

### 6. TransactionDB (db/transaction_db.py)

- **功能**：数据库操作，存储交易和锚点记录
- **特性**：
  - 交易管理（包括 escrow 信息）
  - 锚定记录追踪
  - 仲裁记录存储
  - AI 钱包与用户管理
  - 推荐奖励结算

## API 文档

### 健康检查
```http
GET /api/v1/health
```
返回系统健康状态和服务状态

### 锚定状态
```http
GET /api/v1/anchor/status
```
返回锚定服务状态和统计信息

### 锚定仲裁结果
```http
POST /api/v1/anchor/arbitration
Content-Type: application/json
{
  "arbitration_id": "arb_001",
  "verdict": "seller_wins",
  "commit_hash": "github_commit_hash",
  "metadata": {
    "case_id": "delivery_001"
  }
}
```

### 批量锚定
```http
POST /api/v1/anchor/batch
Content-Type: application/json
{
  "batch_id": "batch_001",
  "transaction_hashes": ["tx1", "tx2", "tx3"],
  "limit": 100
}
```

### 获取交易
```http
GET /api/v1/transactions?limit=50
```

### 重试待处理锚定
```http
POST /api/v1/retry-pending
```

### 切换链
```http
POST /api/v1/x402/switch-chain?chain_name=arbitrum
```

### 获取支持的链
```http
GET /api/v1/x402/supported-chains
```

---

## 仲裁引擎 API Routes ⭐

### 启动仲裁倒计时
```http
POST /api/v1/arbitration/start-countdown
Content-Type: application/json
{
  "tx_id": "tx_001",
  "hours": 48
}
```

### 获取倒计时状态
```http
GET /api/v1/arbitration/countdown-status/{tx_id}
```

### 取消倒计时
```http
POST /api/v1/arbitration/cancel-countdown/{tx_id}
```

### 手动执行裁决
```http
POST /api/v1/arbitration/execute-verdict
Content-Type: application/json
{
  "tx_id": "tx_001",
  "verdict": "seller_wins"
}
```
**说明**：此 API 是非阻塞的，资金释放与 X402 锚定会通过后台任务异步执行。

---

## 配置说明

### 环境变量 (.env)

```env
# Server
HOST=0.0.0.0
PORT=8080

# Database
DB_PATH=./backend/data/clearing.db

# GitHub Anchor Configuration
ANCHOR_INTERVAL_HOURS=1
ANCHOR_GITHUB_TOKEN=your_github_token_here
ANCHOR_GITHUB_REPO_URL=https://github.com/your_username/your_repo
ANCHOR_GITHUB_BRANCH=main

# X402 Configuration
X402_API_KEY=your_x402_api_key_here
X402_CHAIN_ID=8453
X402_RPC_URL=https://mainnet.base.org
X402_FALLBACK_RPC=https://arb1.arbitrum.io/rpc

# Logging
LOG_LEVEL=info
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

### 启动服务

```bash
cd backend
python server.py
```

访问 http://localhost:8080/docs 查看 Swagger UI 完整 API 文档。

---

## 仲裁引擎与异步联动说明 ⭐

### 仲裁裁决流程

```
1. 仲裁倒计时结束或手动触发裁决
   ↓
2. 执行仲裁逻辑，更新数据库状态
   ↓
3. **关键**：通过 AsyncTaskProcessor 提交资金释放任务（非阻塞）
   ↓
4. 后台任务执行 _release_funds_and_anchor() 回调：
   a. 通过 X402Bridge 调用 X402 SDK 释放资金
   b. 更新本地数据库与 AI 钱包状态
   c. 通过 GitHubAnchor 锚定仲裁结果
   d. 通过 X402Anchor 进行二次链上存证
   ↓
5. 如果任一环节失败，任务自动进入重试队列
```

### 关键设计点

1. **非阻塞 API**：所有耗时操作均通过后台任务处理
2. **容错机制**：失败任务自动重试，最多 3 次，指数退避
3. **可观测性**：完整的日志记录与 API 状态查询
4. **批量优化**：对于信誉更新等非紧急任务，支持批量处理以节省 Gas

---

## 交付标准验证 ✅

- ✅ **可计算交易根哈希**：已实现 Merkle Tree
- ✅ **可成功创建/更新 GitHub Gist**：已继承现有 GitHub 服务
- ✅ **定时任务正常运行**：通过 AsyncTaskProcessor 实现
- ✅ **手动触发接口可用**：已实现完整 REST API，包括 `/api/v1/arbitration/execute-verdict`
- ✅ **仲裁引擎与异步联动**：
  - ✅ `arbitration_timer.py` 已修改并集成 AsyncTaskProcessor
  - ✅ `execute_arbitration_verdict()` 已实现并提交后台任务
  - ✅ `_release_funds_and_anchor()` 回调已完整实现
  - ✅ 非阻塞设计、容错机制、可观测性均已实现

---

## 使用示例

### 仲裁裁决的典型流程

```python
from src.anchor import arbitration_timer_service
from src.utils import task_processor

# 1. 启动仲裁倒计时
await arbitration_timer_service.start_arbitration_countdown(
    tx_id="tx_001",
    hours=48
)

# 2. 或者手动执行裁决
await arbitration_timer_service.execute_arbitration_verdict(
    tx_id="tx_001",
    verdict="seller_wins"
)
# 注意：此调用会立即返回，资金释放与锚定在后台执行

# 3. 查询倒计时状态
status = arbitration_timer_service.get_countdown_status("tx_001")
print(status)
```

---

## 下一步

1. **生产部署**：配置 Docker 和 Kubernetes
2. **监控告警**：添加 Prometheus 指标和 Grafana 仪表板
3. **前端集成**：与现有前端集成
4. **性能优化**：压力测试和调优

---

## 参考文档

- [X402 官方网站](https://www.x402.org/)
- [X402 开发文档](https://developers.cloudflare.com/agents/agentic-payments/x402)
- [Black2 白皮书](../WHITEPAPER.md)
