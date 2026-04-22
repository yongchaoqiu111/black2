# Black2 文件哈希计算工具

根据 **Black2 协议白皮书 2.7 节** 开发的文件 SHA-256 哈希计算工具。

## 📋 功能特点

- ✅ **支持任意大小文件**（10GB、100GB 都没问题）
- ✅ **本地计算**，文件不上传，保护隐私
- ✅ **流式读取**，内存占用低
- ✅ **进度显示**，实时查看计算进度
- ✅ **一键复制**，方便粘贴到 Black2 平台

## 🚀 使用方法

### 方法一：直接运行已打包的 exe 文件

1. 下载 `Black2_Hash_Calculator.exe`
2. 双击运行
3. 点击"浏览文件"选择要计算的文件
4. 点击"计算 SHA-256 哈希"按钮
5. 等待计算完成
6. 点击"复制哈希值"按钮
7. 在 Black2 平台发布商品时粘贴此哈希值

### 方法二：从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python hash_calculator.py
```

### 方法三：自己打包成 exe

```bash
# Windows
build.bat

# 生成的文件在 dist/Black2_Hash_Calculator.exe
```

## 📖 技术说明

### 为什么需要这个工具？

根据 Black2 协议白皮书 2.7 节：
- 商品发布需要提供**文件哈希**（SHA-256）
- 文件哈希用于**自动仲裁**和 **GitHub 锚定存证**
- 大文件在前端计算会崩溃，需要在本地计算

### 计算原理

```python
# 使用 Python hashlib 库
import hashlib

sha256_hash = hashlib.sha256()
with open("large_file.zip", "rb") as f:
    for chunk in iter(lambda: f.read(10*1024*1024), b""):
        sha256_hash.update(chunk)

hash_hex = sha256_hash.hexdigest()
```

- **流式读取**：每次读取 10MB，支持超大文件
- **内存友好**：不会一次性加载整个文件到内存
- **标准算法**：使用 SHA-256，与后端一致

## 📦 打包说明

### 依赖安装

```bash
pip install pyinstaller
```

### 打包命令

```bash
pyinstaller --onefile --windowed --name "Black2_Hash_Calculator" hash_calculator.py
```

参数说明：
- `--onefile`：打包成单个 exe 文件
- `--windowed`：不显示控制台窗口
- `--name`：指定输出的 exe 文件名

## 🔒 安全性

- ✅ **完全离线**：不需要网络连接
- ✅ **本地计算**：文件不会上传到任何服务器
- ✅ **开源代码**：可以审查源代码，确保无后门
- ✅ **标准算法**：使用 Python 官方 hashlib 库

## 📝 使用场景

1. **发布数字商品**：软件、教程、电子书等
2. **数据交付**：数据集、模型文件等
3. **大文件验证**：确保文件完整性
4. **自动仲裁**：发生纠纷时对比哈希值

## ⚠️ 注意事项

1. 计算大文件可能需要一些时间，请耐心等待
2. 计算完成后务必复制哈希值并妥善保存
3. 同一个文件的哈希值是固定的，可以重复使用
4. 如果文件内容改变，哈希值也会改变

## 🆘 常见问题

**Q: 为什么计算很慢？**
A: 大文件需要更多时间，这是正常的。10GB 文件大约需要 1-2 分钟。

**Q: 计算结果准确吗？**
A: 使用 Python 官方 hashlib 库，与后端使用的算法完全一致，保证准确性。

**Q: 可以在 Mac/Linux 上使用吗？**
A: 当前打包的是 Windows exe 文件。Mac/Linux 用户可以直接运行 Python 脚本。

## 📄 许可证

本项目遵循 Black2 协议规范开发。

---

**版本**: v1.0  
**更新日期**: 2026-04-21  
**开发者**: Black2 Team
