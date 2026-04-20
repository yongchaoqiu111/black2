# AI 员工 4 号：仲裁系统

**负责模块**: `agents/arbitrator.py` - 纠纷仲裁逻辑  
**技术栈**: Python  

---

## 你的职责

实现自动仲裁逻辑，当交易产生纠纷时判断责任方。

---

## 任务清单

### 第 1 步：实现仲裁函数 (`agents/arbitrator.py`)

#### 输入：
- `tx_id`: 纠纷交易 ID
- `contract_hash`: 合同约定的交付物哈希
- `file_hash`: 卖家实际提交的交付物哈希

#### 逻辑：
1. 从数据库获取交易详情
2. 对比 `contract_hash` 和 `file_hash`
3. 判断规则：
   - 如果 `contract_hash == file_hash` → 卖家履约，买家无理拒付 → **判卖家胜**
   - 如果 `contract_hash != file_hash` → 卖家违约 → **判买家胜**
   - 如果 `file_hash` 为空 → 卖家未交付 → **判买家胜**

#### 输出：
```json
{
  "tx_id": "xxx",
  "verdict": "seller_wins" | "buyer_wins",
  "reason": "Contract hash matches delivered file",
  "timestamp": "2026-04-20T10:00:00Z"
}
```

### 第 2 步：实现纠纷触发机制
- 买家可以调用 `POST /api/v1/transactions/{tx_id}/dispute` 发起纠纷
- 交易状态改为 `disputed`
- 自动触发仲裁函数

### 第 3 步：仲裁结果处理
- 如果判买家胜：交易状态改为 `refunded`
- 如果判卖家胜：交易状态改为 `completed`
- 记录仲裁结果到数据库（新增 `arbitration_results` 表）

### 第 4 步：编写测试用例
- 测试正常履约场景（哈希匹配）
- 测试违约场景（哈希不匹配）
- 测试未交付场景（file_hash 为空）

---

## 交付标准
- [x] 仲裁函数能正确判断责任方
- [ ] 纠纷触发接口可用（需与 1 号员工 API 对接）
- [ ] 仲裁结果能更新交易状态（需与 1 号员工数据库对接）
- [x] 至少 3 个测试用例通过

---

**验收记录 (2026-04-20)**:
- **代码审查**: `arbitrator.py` 逻辑清晰，实现了核心的哈希比对功能。
- **测试验证**: `test_arbitrator.py` 覆盖了匹配、不匹配和未交付三种核心场景。
- **待办事项**: 
  1. 将 `Arbitrator` 类集成到 1 号员工的 FastAPI 路由中。
  2. 在数据库中实现 `dispute` 状态流转和 `arbitration_results` 表。
  3. 增加更复杂的仲裁规则（如：部分交付、质量争议等人工介入点）。

---

**参考文件**:
- `f:\black2\backend\src\db\transaction_db.py` - 由 1 号提供
- `f:\black2\backend\src\crypto\hash_service.py` - 哈希工具
