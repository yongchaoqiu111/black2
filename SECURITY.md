# 安全策略 (Security Policy)

## 支持的版本 (Supported Versions)

目前我们正在积极维护以下版本：

| 版本 | 支持状态 |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: 积极维护 |
| < 1.0   | :x: 不支持 |

## 报告漏洞 (Reporting a Vulnerability)

我们非常重视 Black2 Clearing Protocol 的安全性。如果您发现了安全漏洞，请负责任地披露。

### 如何报告 (How to Report)

**请不要通过公开 GitHub Issues 报告安全问题。**

请通过以下方式之一联系我们：

1. **电子邮件**: security@black2protocol.com（如果可用）
2. **GitHub Security Advisories**: 使用 [GitHub 安全公告](https://github.com/yongchaoqiu111/black2/security/advisories/new) 功能
3. **直接联系**: 在 GitHub 上创建 Issue 时标记为 `[SECURITY]`

### 报告内容 (What to Include)

请在报告中包含以下信息：

- 漏洞类型的描述
- 完整的漏洞利用步骤
- 潜在影响的评估
- 可能的修复建议（如果有）
- 您的联系方式（可选）

### 响应时间 (Response Time)

- **初始响应**: 我们将在 **48 小时**内确认收到您的报告
- **评估**: 我们将在 **5 个工作日**内评估漏洞的严重性
- **修复计划**: 对于确认的漏洞，我们将提供修复时间表
- **公开披露**: 修复后，我们将协调公开披露时间

### 奖励计划 (Bug Bounty)

目前我们没有正式的漏洞赏金计划，但我们会：

- 在修复公告中感谢负责任的披露者（如果您同意）
- 考虑为重大安全贡献提供奖励

### 安全最佳实践 (Security Best Practices)

使用 Black2 协议时，请遵循以下安全建议：

1. **私钥管理**
   - 永远不要共享您的私钥
   - 使用硬件钱包或安全的密钥存储方案
   - 定期轮换密钥

2. **环境变量**
   - 不要将 `.env` 文件提交到版本控制
   - 使用强密码和令牌
   - 定期更新 API 密钥

3. **智能合约交互**
   - 在测试网上充分测试后再部署到主网
   - 审查所有交易参数
   - 启用多签钱包用于大额交易

4. **依赖更新**
   - 定期更新项目依赖
   - 订阅安全公告
   - 使用 `npm audit` 或类似工具检查漏洞

### 已知限制 (Known Limitations)

当前版本的已知安全限制：

- GitHub 锚定依赖于 GitHub 平台的可用性
- 自动确认机制需要买家主动监控交易状态
- 仲裁系统目前基于中心化服务器（未来将去中心化）

### 免责声明 (Disclaimer)

Black2 Clearing Protocol 按"原样"提供，不提供任何明示或暗示的保证。使用者应自行承担风险。

---

**最后更新**: 2026-04-21
