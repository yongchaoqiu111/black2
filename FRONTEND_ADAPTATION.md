# Black2 前端适配任务

**负责模块**: `f:\black\src\` - 前端页面  
**技术栈**: Vue3 + Vite  

---

## 你的职责

将 Black 1.0 的前端页面适配到 Black2 新 API，保持页面风格不变。

---

## 任务清单

### 第 1 步：修改 API 调用

#### 文件：`src/services/api.js`（新建或修改）
```javascript
const API_BASE = 'http://localhost:8080/api/v1'

export async function createTransaction(data) {
  const response = await fetch(`${API_BASE}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return response.json()
}

export async function getTransaction(txId) {
  const response = await fetch(`${API_BASE}/transactions/${txId}`)
  return response.json()
}

export async function getWalletBalance(address) {
  const response = await fetch(`${API_BASE}/wallet/${address}`)
  return response.json()
}
```

### 第 2 步：修改 Create.vue（发布需求页）

#### 关键改动：
1. **提交前生成合同哈希**
   ```javascript
   import { sha256 } from '@/utils/crypto.js'
   
   const contractContent = {
     task: formData.task,
     requirements: formData.requirements,
     deadline: formData.deadline
   }
   const contractHash = await sha256(JSON.stringify(contractContent))
   ```

2. **调用新 API**
   ```javascript
   const result = await createTransaction({
     from_address: userAddress,
     to_address: sellerAddress,
     amount: formData.amount,
     currency: 'USDT',
     contract_hash: contractHash,
     referrer_address: formData.referrer || null
   })
   ```

3. **显示交易 ID**
   - 提交成功后显示 `result.tx_id`
   - 提供"查看交易状态"链接

### 第 3 步：修改 Shop.vue / ProductCard.vue

#### 关键改动：
1. **显示交易状态**
   - 从 API 获取 `status` 字段
   - 状态映射：
     - `pending` → "待交付"
     - `delivered` → "已交付，待确认"
     - `completed` → "已完成"
     - `disputed` → "纠纷中"
     - `refunded` → "已退款"

2. **点击商品卡片跳转到交易详情页**

### 第 4 步：新增 Wallet.vue（暗钱包页面）

#### 功能：
1. **显示余额**
   ```javascript
   const wallet = await getWalletBalance(userAddress)
   // { address, balance, total_earned, referral_count }
   ```

2. **提现按钮**
   - 最小提现金额：50 USDT
   - 调用 `POST /api/v1/wallet/{address}/withdraw`

3. **推荐关系图**
   - 调用 `GET /api/v1/referrals/{address}`
   - 展示 5 级推荐树

### 第 5 步：复用 Black 1.0 的样式

- 保持 `tailwind.config.js` 不变
- 保持 `style.css` 不变
- 只改逻辑，不改 UI

---

## 交付标准
- [ ] Create.vue 能成功创建交易并显示 tx_id
- [ ] Shop.vue 能显示交易状态
- [ ] Wallet.vue 能显示暗钱包余额
- [ ] 所有 API 调用正常
- [ ] 页面风格与 Black 1.0 一致

---

**参考文件**:
- `f:\black\src\views\Create.vue`
- `f:\black\src\views\Shop.vue`
- `f:\black\src\components\ProductCard.vue`
- `f:\black2\docs\API.md`
