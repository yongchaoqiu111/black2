# Black2 SDK 集成指南

本文档说明如何将增强版的 X402 SDK 组件集成到主项目 `black2-sdk` 中。

---

## 📦 待集成的文件

以下文件已准备就绪，需要复制到 `black2-sdk` 目录：

### 1. 核心文件

| 源文件 | 目标位置 | 说明 |
|--------|----------|------|
| `4/x402_bridge_enhanced.py` | `black2-sdk/black2/x402_bridge.py` | 增强版 X402 Bridge |
| `4/test_arbitrator.py` | `black2-sdk/tests/test_arbitrator.py` | 仲裁模拟器测试 |
| `4/examples/python_example.py` | `black2-sdk/examples/python_example.py` | Python 示例 |
| `4/examples/javascript_example.js` | `black2-sdk/examples/javascript_example.js` | JavaScript 示例 |

### 2. 需要更新的文件

| 文件 | 更新内容 |
|------|----------|
| `black2-sdk/black2/__init__.py` | 添加 X402Bridge 导出 |
| `black2-sdk/setup.py` | 添加 uvd-x402-sdk 依赖 |
| `black2-sdk/README.md` | 更新使用文档 |

---

## 🔧 集成步骤

### 步骤 1: 备份现有文件

```bash
cd black2-sdk

# 备份现有的 x402_bridge.py
cp black2/x402_bridge.py black2/x402_bridge.py.backup

# 备份 setup.py
cp setup.py setup.py.backup
```

### 步骤 2: 复制增强版 X402 Bridge

```bash
# 复制增强版 X402 Bridge
cp ../4/x402_bridge_enhanced.py black2/x402_bridge.py

# 或者使用 PowerShell (Windows)
Copy-Item ..\4\x402_bridge_enhanced.py black2\x402_bridge.py
```

### 步骤 3: 更新 __init__.py

编辑 `black2-sdk/black2/__init__.py`:

```python
"""
Black2 Protocol SDK
AI 交易信任层标准开发工具包
"""

from .client import B2PClient
from .reputation import ReputationEngine
from .x402_bridge import X402Bridge, X402Error, X402ErrorCode

__version__ = "0.1.0"
__all__ = [
    "B2PClient",
    "ReputationEngine",
    "X402Bridge",
    "X402Error",
    "X402ErrorCode",
]
```

### 步骤 4: 更新 setup.py

编辑 `black2-sdk/setup.py`,添加新的依赖:

```python
from setuptools import setup, find_packages

setup(
    name="black2-sdk",
    version="0.1.0",
    author="Black2 Team",
    description="SDK for Black2 Protocol (B2P) - AI Transaction Trust Layer",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pygit2",
        "ipfshttpclient",
        "web3",
        "uvd-x402-sdk>=0.1.0",  # X402 cross-chain payment SDK
        "pydantic>=2.0",        # Data validation and type hints
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    python_requires=">=3.8",
)
```

### 步骤 5: 复制测试文件

```bash
# 创建 tests 目录（如果不存在）
mkdir -p black2-sdk/tests

# 复制测试文件
cp ../4/test_arbitrator.py black2-sdk/tests/

# 创建 tests/__init__.py
touch black2-sdk/tests/__init__.py
```

### 步骤 6: 复制示例代码

```bash
# 创建 examples 目录
mkdir -p black2-sdk/examples

# 复制示例文件
cp ../4/examples/python_example.py black2-sdk/examples/
cp ../4/examples/javascript_example.js black2-sdk/examples/
```

### 步骤 7: 安装依赖并测试

```bash
cd black2-sdk

# 安装依赖
pip install -e .

# 运行测试
python -m pytest tests/

# 或者运行仲裁模拟器
python tests/test_arbitrator.py

# 运行 Python 示例
python examples/python_example.py
```

---

## ✅ 验证清单

集成完成后，请验证以下项目：

- [ ] `X402Bridge` 类可以正常导入
- [ ] Mock Mode 可以正常工作
- [ ] 错误码体系正确实现
- [ ] 仲裁模拟器可以运行所有场景
- [ ] 所有测试用例通过
- [ ] 文档中的示例代码可以运行

---

## 🐛 故障排除

### 问题 1: 导入错误 `ModuleNotFoundError: No module named 'uvd-x402-sdk'`

**解决方案**:
```bash
pip install uvd-x402-sdk
```

或者在 Mock Mode 下运行（不需要实际安装）:
```python
bridge = X402Bridge(mock_mode=True)
```

### 问题 2: 测试失败

**检查项**:
1. 确保所有依赖已安装：`pip install -e .[dev]`
2. 检查 Python 版本：`python --version` (需要 3.8+)
3. 查看详细错误信息：`pytest -v`

### 问题 3: 类型检查错误

如果使用 mypy 进行类型检查时出现错误:

```bash
# 安装类型存根
pip install types-requests types-pygit2

# 或者忽略特定错误
mypy --ignore-missing-imports black2/
```

---

## 📝 回滚方案

如果集成后出现问题，可以回滚到之前的版本：

```bash
cd black2-sdk

# 恢复 x402_bridge.py
cp black2/x402_bridge.py.backup black2/x402_bridge.py

# 恢复 setup.py
cp setup.py.backup setup.py

# 重新安装
pip install -e .
```

---

## 🚀 发布到 PyPI（可选）

集成完成后，可以将 SDK 发布到 PyPI:

```bash
# 安装构建工具
pip install build twine

# 构建分发包
python -m build

# 上传到 PyPI
twine upload dist/*

# 需要先在 PyPI 注册账号并设置 token
# export TWINE_USERNAME="__token__"
# export TWINE_PASSWORD="pypi-..."
```

---

## 📞 获取帮助

如果在集成过程中遇到问题：

1. 查看文档：`README.md`
2. 运行测试：`pytest tests/`
3. 提交 Issue: https://github.com/black2-ai/black2-sdk/issues
4. 联系团队：dev@black2.ai

---

**最后更新**: 2026-04-20  
**版本**: v1.0.0
