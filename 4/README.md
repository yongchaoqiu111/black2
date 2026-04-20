# 仲裁系统实现

## 项目结构

```
├── arbitrator.py          # 仲裁系统核心实现
├── test_arbitrator.py     # 测试用例
├── ARBITRATION_SYSTEM.md  # 原始需求文档
└── README.md              # 本说明文档
```

## 功能实现

### 核心类 `Arbitrator`

**文件**: `arbitrator.py`

**主要方法**:
- `arbitrate(tx_id, contract_hash, file_hash)`: 执行仲裁逻辑

**仲裁规则**:
1. 如果 `file_hash` 为空 → 卖家未交付 → **判买家胜**
2. 如果 `contract_hash == file_hash` → 卖家履约 → **判卖家胜**
3. 如果 `contract_hash != file_hash` → 卖家违约 → **判买家胜**

**返回格式**:
```json
{
  "tx_id": "xxx",
  "verdict": "seller_wins" | "buyer_wins",
  "reason": "详细原因",
  "timestamp": "2026-04-20T10:00:00Z"
}
```

## 测试用例

**文件**: `test_arbitrator.py`

**测试场景**:
1. `test_seller_wins_when_hash_matches`: 哈希匹配场景 - 卖家胜
2. `test_buyer_wins_when_hash_mismatches`: 哈希不匹配场景 - 买家胜
3. `test_buyer_wins_when_no_file`: 未交付场景 - 买家胜

## 使用示例

```python
from arbitrator import Arbitrator

# 初始化仲裁器
arbitrator = Arbitrator()

# 测试场景 1: 哈希匹配 - 卖家胜
result = arbitrator.arbitrate(
    tx_id="tx_001",
    contract_hash="abc123",
    file_hash="abc123"
)
print(result)

# 输出:
# {
#   "tx_id": "tx_001",
#   "verdict": "seller_wins",
#   "reason": "Contract hash matches delivered file",
#   "timestamp": "2026-04-20T10:00:00Z"
# }
```

## 集成说明

要集成到完整系统中，需要：

1. 将 `arbitrator.py` 移动到 `backend/src/agents/` 目录
2. 实现纠纷触发接口 (`POST /api/v1/transactions/{tx_id}/dispute`)
3. 实现仲裁结果处理逻辑，更新交易状态
4. 创建 `arbitration_results` 表存储仲裁结果

## 技术栈
- Python 3.x
- 标准库: `json`, `datetime`

## 测试运行

```bash
# 运行测试
python test_arbitrator.py

# 运行示例
python arbitrator.py
```
