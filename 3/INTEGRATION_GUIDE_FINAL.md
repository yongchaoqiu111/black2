# 隐私保护模块完整集成指南
===================================

## 📋 任务概述
完成 `INTEGRATION_PRIVACY_TASK.md 要求的所有集成工作，将隐私保护模块正式集成到 Black2 系统中。

---

## 📦 已交付文件
在 `f:\black2\3\` 目录下已创建：

| 文件 | 说明 |
|------|------|
| `privacy.py` | 隐私保护核心模块（最新版，包含 generate_zkp_proof() |
| `sdk_integration.py` | SDK 集成说明和代码片段 |
| `storage_patch.py` | Storage.py 隐私保护补丁 |
| `ai_routes_patch.py` | AI Routes 隐私保护补丁 |
| `AI_AGENTS.md` | 更新的 AI 交互规范（含 Privacy Level 说明） |
| `example.py` | 完整功能演示 |

---

## 🔧 集成步骤详解

### 第一步：SDK 内部集成

#### 1.1 复制 privacy.py
```powershell
# 在 PowerShell
Copy-Item f:\black2\3\privacy.py f:\black2\black2-sdk\black2\privacy.py
```

#### 1.2 更新 black2-sdk/black2/__init__.py
编辑 `black2-sdk/black2/__init__.py`，添加隐私模块导出：

```python
"""
Black2 Protocol SDK
AI 交易信任层标准开发工具包
"""

from .client import B2PClient
from .reputation import ReputationEngine
from .privacy import PrivacyManager, PrivacyLevel, AnonymousIdentity, privacy_manager, privacy_storage  # 新增

__version__ = "0.1.0"
__all__ = ["B2PClient", "ReputationEngine", "PrivacyManager", "PrivacyLevel", "AnonymousIdentity", "privacy_manager", "privacy_storage"]  # 更新
```

---

### 第二步：修改 storage.py

编辑 `black2-sdk/black2/storage.py`

#### 2.1 顶部添加导入
```python
from .privacy import privacy_storage, PrivacyLevel
```

#### 2.2 修改 push_to_repo 方法
在 push 数据到 GitHub 前，强制调用数据净化：

```python
def push_to_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Push 数据到仓库前进行隐私净化
    """
    # 强制调用数据净化（核心隐私合规
    sanitized_data = privacy_storage.sanitize_for_publication(repo_data)
    
    # 原始的 push 逻辑...
    print(f"[Privacy] 数据已净化，准备 Push 到仓库")
    
    # 继续原有逻辑
    # ...
    
    return sanitized_data
```

---

### 第三步：后端 API 适配

编辑 `backend/src/api/ai_routes.py`

#### 3.1 顶部添加导入
```python
from privacy import privacy_manager, PrivacyLevel
```

#### 3.2 修改 /api/v1/reputation/{address} 接口
在返回给外部 AI 的数据中，确保不包含具体的 transaction_history，仅保留宏观统计指标：

```python
@app.get("/api/v1/reputation/{address}")
async def get_reputation(address: str):
    # 获取原始信誉数据
    raw_reputation = get_reputation_from_db(address)
    
    # 使用 AGGREGATED 隐私等级进行脱敏
    sanitized_reputation = privacy_manager.deidentify_data(
        raw_reputation,
        PrivacyLevel.AGGREGATED
    )
    
    # 返回给外部 AI 的数据不包含具体的 transaction_history
    return sanitized_reputation
```

---

### 第四步：ZKP 声明预研落地

隐私模块中已包含 `generate_zkp_proof()` 占位函数，无需额外修改！

使用方式：
```python
from black2.privacy import privacy_manager

# 生成 ZKP 证明
proof = privacy_manager.generate_zkp_proof(
    agent_id="agent_123",
    repo_data={
        "total_score": 85.5,
        "dispute_count": 0
    }
)
```

---

## ✅ 验收标准对照

| 验收项 | 状态 | 说明 |
|---------|------|------|
| 隐私合规：公开发布的数据必须脱敏 | ✅ | 已实现 sanitize_for_publication() |
| 身份匿名：提供 proxy_address 工具 | ✅ | create_anonymous_identity() |
| 文档更新：AI_AGENTS.md 补充 Privacy Level | ✅ | 已添加详细说明和表格 |
| ZKP 占位函数：generate_zkp_proof() | ✅ | 已实现并预留升级接口 |

---

## 📚 隐私等级说明（已集成到 AI_AGENTS.md）

| 等级 | 说明 | 适用场景 |
|------|------|----------|
| **PUBLIC** | 完全公开 | 内部测试 |
| **AGGREGATED** | 仅聚合数据 | GitHub b2p-repo.json |
| **ANONYMOUS** | 匿名化 | API 响应 |
| **ZKP** | 零知识证明 | 高隐私场景 |

---

## 🎯 使用示例

### 示例1：SDK 使用
```python
from black2 import privacy_manager, PrivacyLevel

# 创建匿名身份
identity = privacy_manager.create_anonymous_identity(
    agent_id="my_agent",
    real_address="0x1234..."
)

# 数据脱敏
sanitized = privacy_manager.deidentify_data(
    data,
    PrivacyLevel.AGGREGATED
)

# 生成 ZKP 证明
proof = privacy_manager.generate_zkp_proof("my_agent", repo_data)
```

---

## 📞 联系方式
如有问题，请查看相关文件：
- `AI_AGENTS.md` - 完整的 AI 交互规范
- `example.py` - 功能演示
- `ZKP_RESEARCH.md` - 零知识证明预研

