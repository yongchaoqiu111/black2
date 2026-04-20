# 变更日志 (Changelog)

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布] - Unreleased

### 待开发功能 (Planned)
- 仲裁引擎实现（沙箱验证、自动裁决）
- 信誉系统完善（信誉分计算、惩罚机制）
- 前端与后端API集成
- 智能合约部署（以太坊/Polygon）
- 多语言支持扩展
- 移动端应用

---

## [1.0.0] - 2026-04-21

### 新增 (Added)
- **核心协议实现**
  - Black2 Clearing Protocol v1.0 完整实现
  - Ed25519 签名验证系统
  - DID (去中心化身份) 生成和验证
  - SHA-256 哈希存证机制
  
- **交易流程**
  - 商品发布页面（Sell.vue）
    - 版本号和适配系统字段
    - 合同模板选择器（4种模板）
    - 量化指标动态数组
    - 效果承诺实时检测
    - 文件上传自动SHA-256哈希计算
    - 自动确认时长设置（24-168小时）
    - 存储方案选择（30天/365天/10年）
    - 交付清单勾选框
    - 信誉分显示和保证金计算
  - 购买流程基础框架
  - 积分托管系统（零Gas费链下转移）
  
- **双钱包架构**
  - 人类钱包（明文，用于日常交易）
  - AI钱包（加密隐藏，接收推荐佣金）
  - 充值/提现API端点
  - 钱包余额查询和管理
  
- **GitHub 锚定服务**
  - 合约哈希提交到GitHub仓库
  - Repository Contents API集成
  - Base64编码和Commit管理
  - 不可篡改的时间戳证明
  
- **推荐系统**
  - 5级推荐链追踪
  - 佣金分配算法 [5%, 3%, 2%, 1%, 0.5%]
  - 延迟结算机制（交易完成后发放）
  - 推荐关系数据库表
  
- **合同模板库**
  - 软件/工具销售合约 (TPL_SOFTWARE_001)
  - AI定制化任务合约 (TPL_AI_TASK_001)
  - AI引流服务合约 (TPL_TRAFFIC_001)
  - 数据交付合约 (TPL_DATA_001)
  - 标准化字段定义和验证
  
- **自动确认服务**
  - 倒计时监控后台任务
  - 可配置的确认时长
  - 自动放款机制
  
- **数据库设计**
  - human_wallets 表（人类钱包）
  - ai_wallets 表（AI钱包）
  - referral_relationships 表（推荐关系）
  - deposits 表（充值记录）
  - withdrawals 表（提现记录）
  - referral_rewards 表（推荐奖励）
  - transactions 表（交易记录）
  - contracts 表（合约存证）
  
- **API端点**
  - POST /api/register - 用户注册
  - POST /api/login - 用户登录
  - POST /api/deposit - 充值
  - POST /api/withdraw - 提现
  - GET /api/wallet/balance - 查询余额
  - POST /api/transaction/create - 创建交易
  - POST /api/transaction/complete - 完成交易
  - POST /api/transaction/cancel - 取消交易
  - GET /api/products - 获取商品列表
  - POST /api/products - 发布商品
  
- **文档**
  - README.md - 项目说明（中英双语）
  - CONTRIBUTING.md - 贡献指南
  - SECURITY.md - 安全策略
  - CODE_OF_CONDUCT.md - 行为准则
  - docs/WHITEPAPER.md - 协议白皮书（8个章节）
  - .env.example - 环境变量模板
  - LICENSE - Apache 2.0 许可证

### 技术栈 (Tech Stack)
- **后端**: FastAPI + Python 3.9+
- **前端**: Vue 3 + Vite + Tailwind CSS
- **数据库**: SQLite (aiosqlite)
- **加密**: Ed25519, SHA-256
- **锚定**: GitHub API v3
- **状态管理**: Pinia
- **路由**: Vue Router

### 架构亮点 (Architecture Highlights)
- 托管+积分模式（零Gas费）
- GitHub存证（不可篡改时间戳）
- 双钱包分离（人类/AI）
- 举证责任倒置（卖家承担举证）
- 自动化仲裁准备（沙箱验证框架）

### 已知限制 (Known Limitations)
- 仲裁引擎尚未完全实现（仅框架）
- 信誉分系统为基础版本
- 前端与后端API尚未完全集成
- 智能合约未部署（当前为链下实现）
- 沙箱验证功能待开发

---

## [0.1.0] - 2026-04-15

### 新增 (Added)
- 项目初始化
- 基础目录结构
- 核心模块划分
- 概念验证原型

---

## 版本说明 (Version Notes)

### 语义化版本规则
- **主版本号 (MAJOR)**: 不兼容的API修改
- **次版本号 (MINOR)**: 向后兼容的功能性新增
- **修订号 (PATCH)**: 向后兼容的问题修正

### 变更类型说明
- **Added**: 新增功能
- **Changed**: 现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug修复
- **Security**: 安全相关修复

---

**维护者**: Black2 Protocol Team  
**联系方式**: https://github.com/yongchaoqiu111/black2  
**最后更新**: 2026-04-21
