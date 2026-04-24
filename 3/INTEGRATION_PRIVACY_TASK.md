# 3号任务：隐私保护模块集成 (Privacy Integration)

## 1. 目标
将 `privacy.py` 中的脱敏逻辑和匿名身份生成器正式集成到 Black2 SDK 和后端发布流程中，确保符合 GDPR 及商业隐私要求。

## 2. 核心工作
### 第一步：SDK 内部集成
- [ ] 在 `black2-sdk/black2/__init__.py` 中导出 `PrivacyManager` 和 `AnonymousIdentity`。
- [ ] 修改 `black2-sdk/black2/storage.py`：在 Push 数据到 GitHub 前，强制调用 `privacy_storage.sanitize_for_publication()` 进行数据净化。

### 第二步：后端 API 适配
- [ ] 在 `backend/src/api/ai_routes.py` 的 `/api/v1/reputation/{address}` 接口中，引入 `PrivacyLevel.AGGREGATED` 逻辑。
- [ ] 确保返回给外部 AI 的数据不包含具体的 `transaction_history`，仅保留宏观统计指标。

### 第三步：ZKP 声明预研落地
- [ ] 根据 `ZKP_RESEARCH.md`，在 SDK 中增加一个 `generate_zkp_proof(agent_id)` 的占位函数。
- [ ] 该函数目前返回简化的 JSON 声明（如“信誉分 > 50”），为未来接入真正的 zk-SNARK 库预留接口。

## 3. 交付标准
*   **隐私合规：** 任何公开发布到 Git 或 IPFS 的信誉数据必须经过脱敏处理。
*   **身份匿名：** 提供一套生成一次性 `proxy_address` 的工具，用于 X402 支付时的身份隔离。
*   **文档更新：** 在 `AI_AGENTS.md` 中补充关于隐私等级（Privacy Level）的说明。
