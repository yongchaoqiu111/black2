# 4号任务：SDK 最终封装与全流程测试 (Integration SDK Test Task)

## 1. 目标
整合增强版桥接层和隐私模块，编写 `integration_test.py` 模拟“信誉查询-托管-仲裁-退款”的全流程闭环。

## 2. 核心工作
### 第一步：SDK 代码合并
- [ ] 将 `4/x402_bridge_enhanced.py` 的内容正式覆盖到 `black2-sdk/black2/x402_bridge.py`。
- [ ] 将 `3/privacy.py` 的内容移入 `black2-sdk/black2/privacy.py`。
- [ ] 更新 `black2-sdk/setup.py`，添加 `uvd-x402-sdk` 和 `pygit2` 等必要依赖。

### 第二步：编写集成测试脚本 (`integration_test.py`)
- [ ] **场景模拟**：
    1. **买家视角**：查询卖家信誉 -> 发起托管支付 (Mock Mode)。
    2. **卖家视角**：确认收到托管通知 -> 提交交付物哈希。
    3. **纠纷模拟**：买家发起申诉 -> 触发自动仲裁逻辑。
    4. **资金结算**：验证 X402 是否根据裁决结果执行了退款或放款。

### 第三步：完善错误处理
- [ ] 确保在所有关键步骤捕获 `X402Error`，并根据错误码（如 `REPUTATION_REJECTED`）给出友好的提示。

## 3. 交付标准
*   **一键运行：** 运行 `python integration_test.py` 能够完整演示 B2P + X402 的核心价值。
*   **代码规范：** 所有新增代码必须包含完整的 Docstring 和类型提示。
*   **发布准备：** 整理 `README.md`，说明如何安装和使用 Black2 SDK。
