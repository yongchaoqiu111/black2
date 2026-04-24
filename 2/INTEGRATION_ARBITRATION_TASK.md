# 2号任务：仲裁引擎与异步任务联动 (Integration Arbitration Task)

## 1. 目标
修改 `backend/src/anchor/arbitration_timer.py`，利用 `AsyncTaskProcessor` 在裁决后自动触发 X402 资金释放，并执行链上锚定。

## 2. 核心工作
### 第一步：初始化异步处理器
- [ ] 在 `server.py` 启动时，初始化 `AsyncTaskProcessor` 和 `X402BatchProcessor`。
- [ ] 确保这些后台服务随主程序一同启动和关闭。

### 第二步：改造裁决执行函数 (`execute_arbitration_verdict`)
- [ ] **逻辑解耦**：当仲裁计时器结束产生 verdict 时，不要直接执行数据库更新。
- [ ] **提交任务**：调用 `task_processor.submit_task(release_funds_and_anchor, tx_id, verdict)`。
- [ ] **批量优化**：对于非紧急的信誉更新，通过 `batch_processor.add_to_batch()` 累积到一定数量后再统一进行链上锚定，以节省 Gas。

### 第三步：实现资金释放回调
- [ ] 编写 `release_funds_and_anchor` 函数：
    1. 调用 `x402_bridge.release_funds` 释放资金。
    2. 根据释放结果更新本地 `transactions` 表状态。
    3. 调用 `github_anchor.push_commit` 记录仲裁结果。

## 3. 交付标准
*   **非阻塞：** 仲裁裁决的执行过程不得阻塞其他 API 请求。
*   **容错性：** 如果 X402 释放失败，任务应进入重试队列（参考 `async_task_processor.py` 的重试逻辑）。
*   **可观测性：** 在日志中清晰记录每一笔仲裁资金的流向和链上交易哈希。
