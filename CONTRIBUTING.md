# 贡献指南

感谢你对 Black2 协议的关注！我们欢迎所有形式的贡献。

## 贡献方式

### 1. 报告问题
- 使用 [Issues](https://github.com/yongchaoqiu111/black2/issues) 报告 bug
- 提供详细的复现步骤
- 附上环境信息（操作系统、Python版本等）

### 2. 提出建议
- 新功能建议请提交 Feature Request
- 说明使用场景和预期效果
- 讨论实现方案的可行性

### 3. 提交代码
- Fork 本仓库
- 创建特性分支 (`git checkout -b feature/AmazingFeature`)
- 编写代码并添加测试
- 确保所有测试通过
- 提交 Pull Request

## 代码规范

### Python 代码
- 遵循 PEP 8 编码规范
- 使用类型注解
- 添加文档字符串
- 保持函数单一职责

### 前端代码
- 使用 ESLint 和 Prettier
- 组件化开发
- 保持代码可复用性

## 提交 Pull Request 流程

1. Fork 仓库并克隆到本地
2. 创建新的功能分支
3. 开发并测试
4. 提交更改（使用有意义的 commit message）
5. 推送到你的 Fork
6. 在 GitHub 上创建 Pull Request
7. 等待代码审查和合并

## Commit Message 规范

```
<type>: <subject>

<body>

<footer>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

**示例**：
```
feat: add GitHub anchor service

- Implement contract hash anchoring
- Add Merkle root calculation for batches
- Support verification of anchored hashes

Closes #123
```

## 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/yongchaoqiu111/black2.git
cd black2

# 后端环境
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 前端环境
cd frontend
npm install

# 运行测试
python -m pytest backend/tests/
npm run test
```

## 联系我们

- GitHub Issues: https://github.com/yongchaoqiu111/black2/issues
- Email: [your-email@example.com]

---

感谢你的贡献！🎉
