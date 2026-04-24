# 1号任务：后端 API 路由集成 (Integration Routes Task)

## 1. 目标
在 `backend/src/api/routes.py` 中实现支持 X402 托管支付的交易创建接口，并确保数据正确存入 SQLite。

## 2. 核心工作
### 第一步：引入依赖
- [ ] 在 `routes.py` 顶部导入 `src.x402.bridge` 中的 `x402_bridge` 实例。
- [ ] 导入 `transaction_db` 用于更新交易记录。

### 第二步：改造下单接口 (`/api/v1/transactions/create`)
- [ ] **逻辑修改**：在创建本地订单后，立即调用 `await x402_bridge.initiate_escrow(...)`。
- [ ] **参数传递**：将买家的 `wallet_address` 作为 sender，卖家的 `wallet_address` 作为 receiver。
- [ ] **数据持久化**：获取返回的 `escrow_id` 和 `escrow_address`，调用数据库更新函数写入 `transactions` 表的对应字段。

### 第三步：增加查询接口
- [ ] 新增 `/api/v1/transactions/{id}/escrow_status` 接口，用于前端/AI 实时查询 X402 链上的资金锁定状态。

## 3. 交付标准
*   **原子性：** 确保本地订单创建与 X402 托管发起的逻辑一致性（如果托管失败，本地订单应回滚或标记为异常）。
*   **响应速度：** 利用异步特性，确保 API 响应时间在 500ms 以内。
*   **文档同步：** 更新 `API_DOC.md`，补充新接口的请求/响应示例。
