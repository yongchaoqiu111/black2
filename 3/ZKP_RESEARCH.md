# Black2 零知识证明 (ZKP) 预研报告
========================================

## 1. 为什么需要 ZKP？

在 Black2 信誉系统中，我们需要解决一个机制：
- 证明"我有足够信誉"
- 证明"我没有近期纠纷"
- 证明"我的交易记录良好"

而不需要：
- 暴露具体交易历史
- 暴露真实钱包地址
- 暴露商业关系

---

## 2. ZKP 在 Black2 中的应用场景

### 场景A：信誉验证

**当前方式：
```
买家：你有足够信誉分多少？
Black2：85分
买家：给我看你的交易记录
Black2：这里是所有记录...
```

**ZKP 方式：
```
买家：你有足够信誉吗？
Black2：[ZKP 声明]
买家：[验证声明]
结果：验证通过 ✅
```

### 场景B：身份匿名交易

```
使用 ZK-SNARK 可以证明：
- 我是信誉 > 50 分
- 我没被仲裁过
- 我有过成功交易
```

---

## 3. 技术选型

### 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|---------|
| **当前简化版** | 实现简单，无需依赖 | 不是真正的 ZKP | MVP 阶段 |
| **ZK-SNARK | 证明小，验证快 | 需要 Setup，依赖重 | 生产环境 |
| **ZK-STARK** | 无需 Setup，透明 | 证明大 | 公开透明场景 |
| **PLONK** | 通用，可更新 | 复杂度高 | 复杂业务逻辑 |

---

## 4. 当前实现（简化版 ZKP）

在 Black2 SDK 中的实现：

```python
from privacy import privacy_manager

# 准备声明
statement = privacy_manager.prepare_zkp_statement(
    data={"total_score": 85.5, "dispute_count": 0},
    statement_type="sufficient_reputation"
)

# 验证声明
is_valid = privacy_manager.verify_zkp_statement(zkp_statement)
```

声明格式：
```json
{
  "statement": "agent_has_sufficient_reputation",
  "min_score": 50.0,
  "actual_score": 85.5,
  "score_meets_threshold": true,
  "timestamp": "2026-04-25T10:30:00Z"
}
```

---

## 5. 未来升级路线图

### 阶段 1：当前（已完成）
- ✅ 简化声明/验证机制
- ✅ 隐私字段设计
- ✅ 代理身份

### 阶段 2：集成真实 ZKP 库
- [ ] 集成 zk-SNARK 库（如 `pyzk）
- [ ] 实现信誉电路
- [ ] 部署验证器

### 阶段 3：链上验证
- [ ] 将 ZKP 验证合约
- [ ] 链上验证证明发布
- [ ] 与 X402 集成

---

## 6. 推荐 ZKP 库

### Python ZKP 选项

1. **pyzk（推荐）
```python
# 可能的未来实现
```

2. **arkworks-rs (Rust 绑定)
```rust
// Rust 实现，性能好
```

---

## 7. 总结

当前 Black2 当前使用简化版 ZKP，为：
- 快速实现 MVP
- 满足基本隐私保护
- 为未来 ZKP 升级预留接口
