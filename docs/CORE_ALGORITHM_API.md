# Black2 Clearing Protocol - 核心算法API文档

**版本**: v1.0  
**日期**: 2026-04-21  

---

## 概述

Black2 Clearing Protocol 的核心算法已完全API化，可以作为独立的交易基础设施被任何应用集成。

**设计理念**:
- 🎯 **协议层优先**: 网站商城只是载体，交易层协议才是核心
- 🔌 **即插即用**: 所有算法通过REST API暴露，可被任意系统集成
- 📦 **独立部署**: 后端可以单独部署，不依赖前端
- 🌐 **跨语言支持**: REST API可以被任何编程语言调用

---

## 快速开始

### 基础URL

```
开发环境: http://localhost:8000/api/v1
生产环境: https://api.black2protocol.com/api/v1
```

### 认证

部分端点需要JWT认证（在Header中添加）：
```
Authorization: Bearer <your_jwt_token>
```

---

## 核心算法API分类

### 1. 密码学与身份 (Cryptography & Identity)

#### 1.1 生成密钥对和DID

**端点**: `POST /api/v1/crypto/keygen`

**用途**: 
- 用户注册时生成身份
- AI代理创建唯一标识
- 钱包生成

**请求**:
```json
{}
```

**响应**:
```json
{
  "private_key": "a1b2c3d4e5f6...",
  "public_key": "f6e5d4c3b2a1...",
  "did": "did:black2:ABC123XYZ"
}
```

**示例代码 (Python)**:
```python
import requests

response = requests.post("http://localhost:8000/api/v1/crypto/keygen")
keys = response.json()

print(f"DID: {keys['did']}")
print(f"Public Key: {keys['public_key']}")
# ⚠️ 私钥必须安全存储，不要泄露
```

---

#### 1.2 签名数据

**端点**: `POST /api/v1/crypto/sign`

**用途**:
- 交易签名
- 合约批准
- 消息认证

**请求**:
```json
{
  "private_key": "a1b2c3d4e5f6...",
  "message": "transaction_data_to_sign"
}
```

**响应**:
```json
{
  "signature": "9f8e7d6c5b4a..."
}
```

---

#### 1.3 验证签名

**端点**: `POST /api/v1/crypto/verify`

**用途**:
- 验证交易真实性
- 身份认证
- 数据完整性检查

**请求**:
```json
{
  "public_key": "f6e5d4c3b2a1...",
  "message": "original_message",
  "signature": "9f8e7d6c5b4a..."
}
```

**响应**:
```json
{
  "valid": true,
  "message": "Signature valid"
}
```

---

#### 1.4 计算SHA-256哈希

**端点**: `POST /api/v1/crypto/hash`

**用途**:
- 文件完整性验证
- 合约哈希生成
- 数据指纹

**请求**:
```json
{
  "data": {"key": "value", "number": 123}
}
```

**响应**:
```json
{
  "hash": "abc123def456..."
}
```

---

### 2. 合同模板系统 (Contract Templates)

#### 2.1 获取所有模板列表

**端点**: `GET /api/v1/protocol/templates`

**响应**:
```json
{
  "templates": [
    {
      "template_id": "TPL_SOFTWARE_001",
      "name": "软件/工具销售合约",
      "version": "1.0"
    },
    {
      "template_id": "TPL_AI_TASK_001",
      "name": "AI定制化任务合约",
      "version": "1.0"
    }
  ],
  "total": 4
}
```

---

#### 2.2 获取模板详情

**端点**: `GET /api/v1/protocol/templates/{template_id}`

**示例**: `GET /api/v1/protocol/templates/TPL_SOFTWARE_001`

**响应**:
```json
{
  "template": {
    "template_id": "TPL_SOFTWARE_001",
    "name": "软件/工具销售合约",
    "fields": {
      "product_name": {"type": "string", "required": true},
      "version": {"type": "string", "required": true},
      ...
    }
  }
}
```

---

#### 2.3 生成合约哈希

**端点**: `POST /api/v1/protocol/contract-hash`

**用途**: 
- 创建合约时生成唯一标识
- GitHub锚定前准备
- 合约完整性验证

**请求**:
```json
{
  "product_name": "AI Trading Bot",
  "version": "v1.0.0",
  "price": 299.99,
  "seller_id": "did:black2:ABC123",
  "file_hash": "xyz789...",
  "timestamp": "2026-04-21T12:00:00Z"
}
```

**响应**:
```json
{
  "contract_hash": "abc123def456...",
  "algorithm": "SHA-256",
  "input_fields": ["product_name", "version", "price", ...]
}
```

---

#### 2.4 验证合约是否符合模板

**端点**: `POST /api/v1/protocol/validate-contract`

**用途**:
- 提交前验证
- 表单实时校验
- 自动化合规检查

**请求**:
```json
{
  "template_id": "TPL_SOFTWARE_001",
  "contract_data": {
    "product_name": "Test Product",
    "version": "v1.0.0",
    "price": 99.99
  }
}
```

**响应**:
```json
{
  "valid": false,
  "errors": [
    "Missing required field: system_requirements",
    "Missing required field: quantifiable_features"
  ]
}
```

---

#### 2.5 检测效果承诺

**端点**: `POST /api/v1/protocol/detect-effect-promise`

**用途**:
- 商品发布时实时警告
- 风险评估
- 合规检查

**请求**:
```json
{
  "description": "This tool can guarantee 10x profit and ensure you make money!"
}
```

**响应**:
```json
{
  "has_effect_promise": true,
  "detected_keywords": ["guarantee", "profit", "make money"],
  "warning": "⚠️ 检测到效果承诺内容。根据协议规则，一旦买家投诉效果未达预期，仲裁将直接判定卖家违约，全额退款并扣除保证金。"
}
```

---

### 3. Merkle树与批量锚定

#### 3.1 计算Merkle根

**端点**: `POST /api/v1/protocol/merkle-root`

**用途**:
- 批量交易优化
- 减少GitHub API调用
- 高效证明生成

**请求**:
```json
{
  "hashes": [
    "tx_hash_1",
    "tx_hash_2",
    "tx_hash_3",
    "tx_hash_4"
  ]
}
```

**响应**:
```json
{
  "merkle_root": "root_hash_abc123...",
  "algorithm": "SHA-256 Merkle Tree",
  "input_count": 4
}
```

---

### 4. 信誉与保证金计算

#### 4.1 计算保证金

**端点**: `POST /api/v1/protocol/calculate-margin`

**用途**:
- 实时保证金计算
- 风险评估
- 定价策略

**请求**:
```json
{
  "reputation_score": 85,
  "price": 299.99
}
```

**响应**:
```json
{
  "reputation_score": 85,
  "margin_percentage": 10.0,
  "margin_amount": 30.00,
  "can_publish": true,
  "risk_level": "medium-low"
}
```

**保证金规则**:
- 信誉分 >= 90: 5%
- 信誉分 >= 80: 10%
- 信誉分 >= 70: 15%
- 信誉分 >= 60: 20%
- 信誉分 < 60: 禁止发布

---

### 5. 推荐链计算

#### 5.1 计算5级推荐链

**端点**: `POST /api/v1/protocol/calculate-referral-chain`

**用途**:
- 佣金计算
- 奖励分配
- 网络分析

**请求**:
```json
{
  "buyer_address": "TBUYER123456",
  "max_levels": 5
}
```

**响应**:
```json
{
  "chain": [
    "TREFERRER1_LEVEL1",
    "TREFERRER2_LEVEL2",
    "TREFERRER3_LEVEL3"
  ],
  "total_levels": 3,
  "commission_rates": [5.0, 3.0, 2.0]
}
```

**佣金比例**: [5%, 3%, 2%, 1%, 0.5%] = 总计11.5%

---

### 6. 自动确认计时器

#### 6.1 计算自动确认截止时间

**端点**: `POST /api/v1/protocol/calculate-auto-confirm`

**用途**:
- 倒计时显示
- 自动确认调度
- 截止时间监控

**请求**:
```json
{
  "auto_confirm_hours": 72,
  "transaction_timestamp": "2026-04-21T12:00:00Z"
}
```

**响应**:
```json
{
  "confirm_deadline": "2026-04-24T12:00:00Z",
  "hours_remaining": 48.5,
  "is_expired": false
}
```

**规则**:
- 最小值: 24小时
- 最大值: 168小时 (7天)
- 默认值: 72小时

---

### 7. 存储方案成本计算

#### 7.1 计算存储成本

**端点**: `POST /api/v1/protocol/calculate-storage-cost`

**用途**:
- 价格展示
- 成本对比
- 预算规划

**请求**:
```json
{
  "storage_plan": "365days",
  "file_size_mb": 50.0
}
```

**响应**:
```json
{
  "plan": "365days",
  "duration_days": 365,
  "cost_usd": 4.0,
  "cost_per_day": 0.011
}
```

**存储方案**:
- 30天: $0.5/月
- 365天: $4/年
- 10年: $30一次性

---

### 8. 协议信息

#### 8.1 获取协议信息

**端点**: `GET /api/v1/protocol/info`

**用途**:
- 客户端兼容性检查
- 功能检测
- 系统健康检查

**响应**:
```json
{
  "protocol_name": "Black2 Clearing Protocol",
  "version": "1.0.0",
  "description": "AI-to-AI Trusted Trading Infrastructure",
  "features": [
    "Ed25519 Identity & Signing",
    "SHA-256 Hash Anchoring",
    "GitHub Immutable Timestamping",
    ...
  ],
  "endpoints": {
    "cryptography": "/api/v1/crypto/*",
    "contracts": "/api/v1/protocol/templates/*",
    ...
  }
}
```

---

## 集成示例

### Python集成

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# 1. 生成身份
keys = requests.post(f"{API_BASE}/crypto/keygen").json()
print(f"DID: {keys['did']}")

# 2. 创建商品前先验证合约
validation = requests.post(f"{API_BASE}/protocol/validate-contract", json={
    "template_id": "TPL_SOFTWARE_001",
    "contract_data": {...}
}).json()

if not validation["valid"]:
    print("Validation errors:", validation["errors"])
    exit(1)

# 3. 检测效果承诺
check = requests.post(f"{API_BASE}/protocol/detect-effect-promise", json={
    "description": "Your description here"
}).json()

if check["has_effect_promise"]:
    print("Warning:", check["warning"])

# 4. 计算保证金
margin = requests.post(f"{API_BASE}/protocol/calculate-margin", json={
    "reputation_score": 85,
    "price": 299.99
}).json()

print(f"Margin: ${margin['margin_amount']} ({margin['margin_percentage']}%)")

# 5. 生成合约哈希
contract_hash = requests.post(f"{API_BASE}/protocol/contract-hash", json={
    "product_name": "My Product",
    "version": "v1.0.0",
    ...
}).json()

print(f"Contract Hash: {contract_hash['contract_hash']}")
```

### JavaScript集成

```javascript
const API_BASE = 'http://localhost:8000/api/v1';

// 1. 生成密钥对
async function createIdentity() {
  const response = await fetch(`${API_BASE}/crypto/keygen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return await response.json();
}

// 2. 签名交易
async function signTransaction(privateKey, message) {
  const response = await fetch(`${API_BASE}/crypto/sign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ private_key: privateKey, message })
  });
  return await response.json();
}

// 3. 验证合约
async function validateContract(templateId, contractData) {
  const response = await fetch(`${API_BASE}/protocol/validate-contract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ template_id: templateId, contract_data: contractData })
  });
  return await response.json();
}
```

---

## 架构优势

### 为什么将算法API化？

1. **协议独立性**: Black2协议可以独立于任何前端存在
2. **多客户端支持**: Web、Mobile、Desktop、IoT设备都可以调用
3. **易于测试**: 每个算法都可以独立单元测试
4. **版本管理**: API版本控制，向后兼容
5. **性能优化**: 可以水平扩展API服务
6. **生态建设**: 第三方可以基于Black2协议构建应用

### 典型应用场景

1. **电商平台集成**: 现有电商可以集成Black2的交易层
2. **AI市场**: AI模型交易平台直接使用Black2协议
3. **数字资产市场**: NFT、域名等数字资产交易
4. **自由职业平台**: 服务交易的托管和仲裁
5. **供应链金融**: 基于智能合约的供应链融资

---

## 开源许可

Black2 Clearing Protocol 采用 **Apache License 2.0**。

您可以：
- ✅ 商业使用
- ✅ 修改代码
- ✅ 分发代码
- ✅ 专利使用

条件：
- 📝 保留版权声明
- 📝 包含许可证副本
- 📝 标注修改内容

详见: [LICENSE](../LICENSE)

---

## 技术支持

- **GitHub Issues**: https://github.com/yongchaoqiu111/black2/issues
- **白皮书**: https://github.com/yongchaoqiu111/black2/docs/WHITEPAPER.md
- **API文档**: http://localhost:8000/docs (Swagger UI)

---

**最后更新**: 2026-04-21  
**维护者**: Black2 Protocol Team
