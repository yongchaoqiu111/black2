# AI 员工 2 号：锚定服务

**负责模块**: `backend/src/anchor/` - 定期锚定脚本  
**技术栈**: Python + httpx + GitHub API  

---

## 你的职责

实现定期将交易根哈希锚定到公共平台（GitHub Gist），确保证据不可篡改。

---

## 任务清单

### 第 1 步：实现锚定逻辑 (`src/anchor/anchor_service.py`)

#### 功能 1：计算交易根哈希
- 从数据库读取所有未锚定的交易
- 按时间排序，拼接所有交易哈希
- 计算 Merkle Root 或简单 SHA-256 根哈希

#### 功能 2：锚定到 GitHub Gist（主方案，0 成本）
- 使用 GitHub API 创建/更新 Gist
- Gist 内容格式：
  ```json
  {
    "timestamp": "2026-04-20T10:00:00Z",
    "root_hash": "abc123...",
    "transaction_count": 150,
    "previous_anchor": "xyz789..."
  }
  ```
- 返回 Gist URL 和 Commit Hash

#### 功能 3：更新数据库
- 将锚定哈希和时间戳写入对应交易记录

---

### 备选方案（后续扩展）

#### 方案 B：以太坊 Sepolia 测试网（0 成本）
- **频率**：每天或每周
- **实现**：用 Web3.py 发送一笔 0 ETH 交易，data 字段填根哈希
- **优点**：区块链不可篡改、公开可查
- **配置**：`.env` 中增加 `ANCHOR_ETH_RPC_URL`, `ANCHOR_ETH_PRIVATE_KEY`

#### 方案 C：Arweave 永久存储（低成本 ~$0.01/MB）
- **频率**：每周或每月
- **实现**：上传完整交易记录 JSON 到 Arweave
- **优点**：永久存储、去中心化
- **配置**：`.env` 中增加 `ANCHOR_ARWEAVE_WALLET_PATH`

### 第 2 步：实现定时任务 (`src/anchor/scheduler.py`)
- 使用 `asyncio` 或 `APScheduler`
- 每隔 N 小时执行一次锚定（从 `.env` 读取 `ANCHOR_INTERVAL_HOURS`）
- 记录日志到 `logs/anchor.log`

### 第 3 步：集成到主服务
- 在 `server.py` 启动时后台运行锚定调度器
- 提供手动触发接口：**POST /api/v1/anchor/trigger**

### 第 4 步：编写测试
- 测试根哈希计算
- 测试 Gist 创建（可用 Mock）
- 测试数据库更新

---

## 交付标准
- [x] 能计算交易根哈希
- [x] 能成功创建/更新 GitHub Gist
- [x] 定时任务正常运行
- [x] 手动触发接口可用

---

**验收记录 (2026-04-20)**:
- **代码审查**: `anchor_service.py` 实现了 Merkle Root 计算和 GitHub Gist 锚定逻辑。
- **调度器**: `scheduler.py` 提供了后台定时任务和手动触发功能。
- **数据库**: `transaction_db.py` 实现了锚定记录的存储和查询。
- **集成状态**: 待合并入 1 号员工的主服务。

---

**参考文件**:
- `f:\black2\.env` - `ANCHOR_GITHUB_TOKEN`, `ANCHOR_GITHUB_GIST_ID`
- `f:\black2\backend\src\db\transaction_db.py` - 由 1 号提供
