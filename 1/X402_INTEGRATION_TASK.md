# X402 支付桥接层接入任务清单

## 1. 目标
在 Black2 Protocol (B2P) 中集成 X402 协议，实现 AI 交易中的跨链支付、资金托管（Escrow）及原子化结算。

## 🏗️ 项目架构背景（必读）
*   **后端框架：** 基于 Python Flask/FastAPI，核心逻辑位于 `backend/src/`。
*   **数据库：** 使用 SQLite (`black2.db`)，交易表为 `transactions`。需在表中增加 `x402_escrow_id` 字段以关联链上状态。
*   **核心钩子：** 支付逻辑需嵌入 `backend/src/api/routes.py` 的下单接口；释放逻辑需嵌入 `backend/src/anchor/arbitration_timer.py` 的裁决执行函数。
*   **钱包系统：** 已实现 HD 钱包 (`hd_wallet.py`)，X402 签名需兼容我们现有的私钥管理逻辑。

## 2. 核心任务分解

### 第一步：依赖引入与环境配置
- [ ] 在 `requirements.txt` 或 `setup.py` 中添加 `uvd-x402-sdk`。
- [ ] 配置环境变量 `X402_API_KEY` 和 `X402_NETWORK`（如 Base, Ethereum）。
- [ ] 创建 `src/x402/` 目录，初始化 `__init__.py`。

### 第二步：封装 X402Bridge 类
- [ ] 编写 `src/x402/bridge.py`，实现以下核心方法：
    - `initiate_escrow(sender, receiver, amount, asset)`: 发起托管支付。
    - `release_funds(escrow_id, recipient, verdict)`: 根据裁决释放资金。
    - `check_balance(agent_id)`: 查询可用余额。
- [ ] 增加异常处理与自动重试机制（应对中继节点波动）。

### 第三步：与 B2P 仲裁引擎联动
- [ ] 修改 `backend/src/anchor/arbitration_timer.py`。
- [ ] 逻辑：当仲裁计时器结束并产生裁决时，自动调用 `X402Bridge.release_funds`。
- [ ] 确保“裁决上链”与“资金释放”的原子性。

### 第四步：SDK 集成与测试
- [ ] 在 `black2-sdk/black2/client.py` 中集成 `X402Bridge`。
- [ ] 编写全流程测试脚本：信誉判定 → 资金锁定 → 模拟交付 → 资金释放。
- [ ] 验证本地缓存与 X402 链上状态的一致性校验逻辑。

## 3. 预期成果
*   **安全托管：** 实现基于 X402 的条件支付，确保资金在仲裁完成前不被挪用。
*   **自动化结算：** 仲裁结果一旦生成，资金自动划转，无需人工干预。
*   **行业标准：** 确立 B2P + X402 的 AI 交易信任与清算标准架构。
