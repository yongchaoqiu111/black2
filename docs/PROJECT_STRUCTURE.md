# 项目结构说明 (Project Structure)

本文档详细说明 Black2 Clearing Protocol 项目的目录结构和各模块职责。

## 📁 根目录

```
black2/
├── backend/              # 后端服务（FastAPI）
├── frontend/             # 前端应用（Vue 3）
├── docs/                 # 文档目录
├── agents/               # AI智能体（待实现）
├── demo/                 # 演示脚本
├── .env                  # 环境变量配置（不要提交到Git）
├── .env.example          # 环境变量模板
├── .gitignore            # Git忽略规则
├── LICENSE               # Apache 2.0 许可证
├── README.md             # 项目说明
├── CONTRIBUTING.md       # 贡献指南
├── SECURITY.md           # 安全策略
├── CODE_OF_CONDUCT.md    # 行为准则
├── CHANGELOG.md          # 变更日志
└── requirements.txt      # Python依赖
```

## 📂 Backend (后端服务)

```
backend/
├── server.py                     # FastAPI应用入口
├── logs/                         # 日志文件目录
│   └── black2.log
├── src/                          # 源代码
│   ├── __init__.py
│   ├── api/                      # API路由层
│   │   ├── __init__.py
│   │   └── routes.py             # RESTful API端点定义
│   ├── db/                       # 数据库层
│   │   ├── __init__.py
│   │   └── transaction_db.py     # SQLite数据库操作（异步）
│   ├── crypto/                   # 加密服务
│   │   ├── __init__.py
│   │   └── hash_service.py       # SHA-256哈希计算、Ed25519签名
│   ├── anchor/                   # GitHub锚定服务
│   │   ├── __init__.py
│   │   ├── github_anchor.py      # GitHub API集成
│   │   └── auto_confirm.py       # 自动确认倒计时服务
│   ├── contract/                 # 合同模板库
│   │   └── templates.py          # 4种标准化合约模板
│   └── agents/                   # AI智能体（仲裁员）
│       └── arbitrator.py         # 仲裁引擎（待完善）
└── tests/                        # 测试目录
    ├── __init__.py
    ├── test_api.py               # API测试
    └── test_anchor.py            # 锚定服务测试
```

### 核心模块说明

#### 1. API路由 (`src/api/routes.py`)

**职责**: 处理HTTP请求，协调业务逻辑

**主要端点**:
- `POST /api/register` - 用户注册（生成DID和密钥对）
- `POST /api/login` - 用户登录
- `POST /api/deposit` - 充值（人类钱包）
- `POST /api/withdraw` - 提现
- `GET /api/wallet/balance` - 查询钱包余额
- `POST /api/products` - 发布商品
- `GET /api/products` - 获取商品列表
- `POST /api/transaction/create` - 创建交易
- `POST /api/transaction/complete` - 完成交易
- `POST /api/transaction/cancel` - 取消交易
- `POST /api/arbitration/dispute` - 发起争议

**示例代码**:
```python
@router.post("/api/products")
async def create_product(product: ProductCreate):
    """发布商品"""
    # 1. 验证卖家信誉分
    # 2. 计算保证金
    # 3. 生成合约哈希
    # 4. 锚定到GitHub
    # 5. 保存到数据库
    return {"product_id": product_id, "contract_hash": contract_hash}
```

#### 2. 数据库层 (`src/db/transaction_db.py`)

**职责**: 所有数据库操作的封装

**数据表**:
- `human_wallets` - 人类钱包（积分账本）
- `ai_wallets` - AI钱包（推荐佣金）
- `referral_relationships` - 推荐关系追踪
- `deposits` - 充值记录
- `withdrawals` - 提现记录
- `referral_rewards` - 推荐奖励（pending/completed）
- `transactions` - 交易记录
- `contracts` - 合约存证（含GitHub锚定URL）
- `products` - 商品信息
- `users` - 用户信息（DID、公钥、信誉分）

**关键函数**:
```python
async def calculate_referral_chain(buyer_address: str) -> List[str]:
    """计算5级推荐链"""
    
async def settle_referral_rewards(tx_id: str):
    """结算待处理的推荐奖励"""
    
async def update_reputation_score(address: str, delta: int):
    """更新信誉分"""
```

#### 3. 加密服务 (`src/crypto/hash_service.py`)

**职责**: 提供加密原语

**功能**:
- SHA-256哈希计算（文件、合约）
- Ed25519密钥对生成
- 签名和验证
- DID生成

**示例**:
```python
def calculate_file_hash(file_path: str) -> str:
    """计算文件SHA-256哈希"""
    
def generate_keypair() -> Tuple[str, str]:
    """生成Ed25519密钥对，返回(private_key, public_key)"""
    
def sign_message(private_key: str, message: bytes) -> bytes:
    """使用私钥签名"""
```

#### 4. GitHub锚定 (`src/anchor/github_anchor.py`)

**职责**: 将合约哈希提交到GitHub仓库

**工作流程**:
1. 构造锚定数据JSON
2. Base64编码
3. 调用GitHub Contents API
4. 创建commit到指定分支
5. 返回commit URL和SHA

**配置**:
```bash
ANCHOR_GITHUB_TOKEN=ghp_xxx
ANCHOR_GITHUB_REPO_URL=https://github.com/yongchaoqiu111/black2
ANCHOR_GITHUB_BRANCH=main
```

#### 5. 自动确认服务 (`src/anchor/auto_confirm.py`)

**职责**: 后台监控交易，超时自动确认

**实现**:
- 使用`asyncio.create_task`启动后台任务
- 每分钟检查一次待确认交易
- 到达`auto_confirm_hours`后自动释放资金

**调度器**:
```python
async def start_auto_confirm_scheduler():
    """启动自动确认调度器"""
    while True:
        await check_pending_transactions()
        await asyncio.sleep(60)  # 每分钟检查
```

#### 6. 合同模板 (`src/contract/templates.py`)

**职责**: 定义标准化合约模板

**模板列表**:
- `TPL_SOFTWARE_001` - 软件/工具销售
- `TPL_AI_TASK_001` - AI定制化任务
- `TPL_TRAFFIC_001` - AI引流服务
- `TPL_DATA_001` - 数据交付

**功能**:
- 模板字段定义和验证
- 效果承诺关键词检测
- 合约JSON序列化

#### 7. 仲裁引擎 (`src/agents/arbitrator.py`)

**状态**: 🚧 待完善

**计划功能**:
- 沙箱环境部署
- 自动化测试执行
- 证据收集和分析
- 裁决建议生成

---

## 📂 Frontend (前端应用)

```
frontend/
├── index.html                    # HTML入口
├── package.json                  # Node.js依赖
├── vite.config.js                # Vite配置
├── tailwind.config.js            # Tailwind CSS配置
├── postcss.config.js             # PostCSS配置
├── public/                       # 静态资源
├── src/
│   ├── main.js                   # Vue应用入口
│   ├── App.vue                   # 根组件
│   ├── style.css                 # 全局样式
│   ├── components/               # 可复用组件
│   │   ├── Navbar.vue            # 导航栏
│   │   ├── Layout.vue            # 布局容器
│   │   ├── ProductCard.vue       # 商品卡片
│   │   ├── LineAnimation.vue     # 线条动画
│   │   └── CustomerChatWidget.vue # 客服聊天窗口
│   ├── views/                    # 页面视图
│   │   ├── Shop.vue              # 商店首页
│   │   ├── Sell.vue              # 发布商品（已完善）
│   │   ├── Wallet.vue            # 钱包管理
│   │   ├── AIWallet.vue          # AI钱包
│   │   ├── PostDemand.vue        # 发布需求
│   │   └── PostRequirement.vue   # 发布需求（旧版）
│   ├── router/                   # 路由配置
│   │   └── index.js
│   ├── stores/                   # Pinia状态管理
│   │   ├── auth.js               # 认证状态
│   │   ├── user.js               # 用户信息
│   │   ├── cart.js               # 购物车
│   │   └── orders.js             # 订单管理
│   ├── services/                 # API服务
│   │   └── api.js                # Axios封装
│   ├── utils/                    # 工具函数
│   │   ├── crypto.js             # 前端加密工具
│   │   ├── websocket.js          # WebSocket连接
│   │   ├── translation.js        # 翻译工具
│   │   ├── aiEcosystem.js        # AI生态系统
│   │   ├── aiEcosystemConfig.js  # AI生态配置
│   │   └── aiEcosystemEngine.js  # AI生态引擎
│   └── i18n/                     # 国际化
│       └── index.js
```

### 核心视图说明

#### 1. Sell.vue (发布商品)

**状态**: ✅ 已完成

**功能**:
- ✅ 版本号和适配系统选择
- ✅ 合同模板选择器（4种）
- ✅ 量化指标动态数组（添加/删除）
- ✅ 效果承诺实时检测和警告
- ✅ 文件上传自动SHA-256哈希计算
- ✅ 自动确认时长设置（24-168小时）
- ✅ 存储方案选择（30天/365天/10年）
- ✅ 交付清单勾选框
- ✅ 信誉分显示和保证金动态计算
- ✅ 钱包地址显示和复制

**待集成**:
- ⏳ 与后端API连接（目前是模拟提交）
- ⏳ 文件实际上传到服务器
- ⏳ 从后端获取用户信誉分

#### 2. Shop.vue (商店首页)

**功能**:
- 商品列表展示
- 分类筛选
- 搜索功能
- 商品卡片点击跳转详情

#### 3. Wallet.vue (钱包管理)

**功能**:
- 显示人类钱包余额
- 充值界面
- 提现界面
- 交易历史记录

#### 4. AIWallet.vue (AI钱包)

**功能**:
- 显示AI钱包余额（推荐佣金）
- 佣金收入明细
- 推荐链可视化

---

## 📂 Docs (文档)

```
docs/
├── WHITEPAPER.md                 # 协议白皮书（8个章节）
├── ARCHITECTURE.md               # 架构设计文档
├── API.md                        # API接口文档
└── PROGRESS.md                   # 开发进度跟踪
```

### WHITEPAPER.md

**内容**:
1. 协议概述
2. 身份与认证（DID、签名验证）
3. 交易流程（发布、交易、完成）
4. 哈希存证（GitHub锚定、Merkle根）
5. 资金托管（双钱包、充值/提现）
6. 仲裁机制（争议类型、举证倒置、沙箱验证）
7. 信誉与惩罚（信誉分计算、保证金机制）
8. 合同模板（4种模板详细说明）

---

## 📂 Agents (AI智能体)

```
agents/
├── buyer_agent.py                # 买家智能体（待实现）
├── seller_agent.py               # 卖家智能体（待实现）
└── config.json                   # 智能体配置
```

**计划功能**:
- 自动浏览商品
- 自动下单购买
- 自动验收测试
- 自动发起争议

---

## 🔧 开发工作流

### 后端开发

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑.env填入GitHub Token等

# 3. 启动服务
python server.py

# 4. 运行测试
pytest tests/
```

### 前端开发

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev

# 3. 构建生产版本
npm run build
```

### 数据库迁移

当前使用SQLite，无需迁移工具。如需修改表结构：

1. 编辑 `src/db/transaction_db.py` 中的建表SQL
2. 删除旧的 `black2.db` 文件
3. 重启后端服务自动重建

---

## 📊 数据流向示例

### 商品发布流程

```
前端 (Sell.vue)
  ↓ HTTP POST /api/products
后端 API (routes.py)
  ↓ 验证输入
数据库 (transaction_db.py)
  ↓ 保存商品和合约
加密服务 (hash_service.py)
  ↓ 计算合约哈希
GitHub锚定 (github_anchor.py)
  ↓ 提交commit
返回 product_id + contract_hash
  ↓
前端显示成功消息
```

### 交易完成流程

```
买家点击"确认收货"
  ↓ HTTP POST /api/transaction/complete
后端验证签名
  ↓
数据库更新交易状态
  ↓
计算推荐链 (calculate_referral_chain)
  ↓
创建待处理推荐奖励 (status=pending)
  ↓
释放资金给卖家（扣除保证金）
  ↓
更新双方信誉分
  ↓
启动自动确认计时器（如果未完成）
```

---

## 🎯 下一步开发重点

### 高优先级
1. **前端与后端API集成**
   - 将Sell.vue的模拟提交改为真实API调用
   - 实现商品详情页
   - 实现购买流程

2. **仲裁引擎完善**
   - 实现沙箱环境
   - 编写自动化测试用例
   - 集成证据收集系统

3. **信誉系统增强**
   - 实现信誉分历史追踪
   - 添加信誉分变化通知
   - 实现信誉排行榜

### 中优先级
4. **WebSocket实时通知**
   - 交易状态更新推送
   - 争议处理进度通知
   - 推荐佣金到账提醒

5. **多语言支持**
   - 扩展i18n配置
   - 翻译所有UI文本
   - 支持RTL语言

6. **移动端适配**
   - 响应式设计优化
   - PWA支持
   - 触摸手势优化

### 低优先级
7. **智能合约部署**
   - 以太坊/Polygon智能合约
   - 跨链桥接
   - Layer 2扩容

8. **数据分析面板**
   - 交易统计
   - 用户增长曲线
   - 热门商品排行

---

## 🤝 贡献指南

详见 [CONTRIBUTING.md](../CONTRIBUTING.md)

**快速开始**:
1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

**最后更新**: 2026-04-21  
**维护者**: Black2 Protocol Team
