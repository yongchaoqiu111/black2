# Black2 AI 接口文档

## 用户系统

### 注册
- **接口**: `POST /api/v1/users/register`
- **功能**: 用户注册，自动生成人类钱包和AI钱包
- **参数**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "referrer_address": "AI钱包地址（可选）"
  }
  ```
- **返回**:
  ```json
  {
    "message": "Registration successful",
    "token": "jwt_token",
    "user": {
      "email": "user@example.com",
      "address": "人类钱包地址（充值/交易）",
      "ai_wallet_address": "AI钱包地址（推荐码/收益）",
      "reputation_score": 100
    }
  }
  ```
- **说明**: 
  - 系统自动生成两个Tron钱包地址
  - `address`: 人类钱包地址，用于充值和交易
  - `ai_wallet_address`: AI钱包地址，用作推荐码

### 登录
- **接口**: `POST /api/v1/users/login`
- **功能**: 用户登录
- **参数**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **返回**:
  ```json
  {
    "message": "Login successful",
    "token": "jwt_token",
    "user": {
      "email": "user@example.com",
      "address": "人类钱包地址",
      "ai_wallet_address": "AI钱包地址（推荐码/收益）",
      "reputation_score": 100
    }
  }
  ```

## 钱包系统

### 获取钱包数据
- **接口**: `GET /api/v1/wallets/human/:address`
- **功能**: 获取人类钱包余额
- **返回**:
  ```json
  {
    "id": 1,
    "address": "人类钱包地址",
    "points_balance": 0,
    "locked_points": 0,
    "total_deposited": 0,
    "total_withdrawn": 0
  }
  ```

- **接口**: `GET /api/v1/wallets/ai/:address`
- **功能**: 获取AI钱包数据
- **返回**:
  ```json
  {
    "id": 1,
    "address": "AI钱包地址",
    "balance": 0,
    "total_earned": 0,
    "referral_count": 0
  }
  ```

## 交易系统

### 创建交易
- **接口**: `POST /api/v1/transactions`
- **功能**: 创建交易订单
- **参数**:
  ```json
  {
    "from_address": "付款方地址",
    "to_address": "收款方地址", 
    "amount": 100,
    "currency": "USDT",
    "contract_hash": "合约哈希",
    "file_hash": "文件哈希（可选）",
    "referrer_address": "推荐人地址（可选）"
  }
  ```
- **返回**: 交易详情
- **说明**: 
  - 系统自动查询付款方的tu1/tu2/tu3关系
  - 计算分润金额并写入订单表
  - 为三代推荐人预留奖励（5%, 3%, 2%）

### 确认收货
- **接口**: `POST /api/v1/transactions/{tx_id}/complete`
- **功能**: 买家确认收货，触发异步结算
- **返回**:
  ```json
  {
    "message": "Transaction completed, settlement queued",
    "tx_id": "订单ID"
  }
  ```
- **说明**: 
  - 将订单状态改为完成
  - 推送结算任务到Redis队列
  - 异步更新三代AI钱包余额

## 推荐系统

### 获取用户三代关系
- **接口**: `GET /api/v1/users/{user_address}/referral-chain`
- **功能**: 获取指定用户的三代推荐关系
- **返回**:
  ```json
  {
    "tu1": "第一代推荐人AI地址",
    "tu2": "第二代推荐人AI地址", 
    "tu3": "第三代推荐人AI地址"
  }
  ```

### 查询用户团队
- **接口**: `GET /api/v1/referrals/{address}`
- **功能**: 查询用户的下线网络
- **返回**:
  ```json
  {
    "referrals": ["下线1地址", "下线2地址", ...],
    "total_count": 5
  }
  ```

## 充值系统

### 手动充值（管理员）
- **接口**: `POST /api/v1/admin/deposits/manual`
- **功能**: 管理员手动给钱包充值
- **参数**:
  ```json
  {
    "user_address": "钱包地址（人类或AI）",
    "amount": 100,
    "reason": "充值原因"
  }
  ```
- **返回**: 充值结果

## 数据结构说明

### 用户表 (users)
- `address`: 人类钱包地址（主地址）
- `ai_address`: AI钱包地址（推荐码）
- `human_balance`: 人类钱包余额
- `ai_balance`: AI钱包余额
- `tu1`: 第一代推荐人AI地址
- `tu2`: 第二代推荐人AI地址
- `tu3`: 第三代推荐人AI地址

### 交易表 (transactions)
- `tu1_address`: 第一代推荐人地址
- `tu1_amount`: 第一代奖励金额
- `tu2_address`: 第二代推荐人地址
- `tu2_amount`: 第二代奖励金额
- `tu3_address`: 第三代推荐人地址
- `tu3_amount`: 第三代奖励金额
- `settlement_status`: 结算状态 (pending/completed/failed)

## 分润规则
- 第一代推荐人: 5% 交易金额
- 第二代推荐人: 3% 交易金额
- 第三代推荐人: 2% 交易金额
- 奖励发放到对应AI钱包余额

## 测试流程
1. 注册新用户 → 获取人类钱包地址和AI钱包地址
2. 用AI钱包地址作为推荐码注册下级用户
3. 下级用户购物 → 自动计算三代分润
4. 确认收货 → 异步更新AI钱包余额