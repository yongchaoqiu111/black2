# Black2 Hash Calculator - AI Agent Guide

## 三种本地计算工具（无需服务器）

AI 可以根据自己的环境选择任意一种工具，**全部在本地运行，不上传文件**。

---

## 1. Python 脚本（推荐）

**适用环境**：有 Python 3.x 的 Linux/Mac/Windows

**使用方法**：
```bash
python calculate_hash.py /path/to/file.zip
```

**输出示例**：
```json
{
  "file": "/path/to/file.zip",
  "size": 1073741824,
  "size_human": "1.00 GB",
  "sha256": "a1b2c3d4e5f6...",
  "algorithm": "SHA-256",
  "time_cost": 12.45
}
```

**AI 调用示例**：
```python
import subprocess
import json

result = subprocess.run(
    ['python', 'calculate_hash.py', 'product.zip'],
    capture_output=True,
    text=True
)
hash_data = json.loads(result.stdout)
file_hash = hash_data['sha256']
```

---

## 2. Bash 脚本

**适用环境**：Linux/Mac（自带 bash + sha256sum/shasum）

**使用方法**：
```bash
bash calculate_hash.sh /path/to/file.zip
```

**输出示例**：
```json
{"file":"/path/to/file.zip","size":1073741824,"sha256":"a1b2c3...","algorithm":"SHA-256"}
```

**AI 调用示例**：
```python
import subprocess
import json

result = subprocess.run(
    ['bash', 'calculate_hash.sh', 'product.zip'],
    capture_output=True,
    text=True
)
hash_data = json.loads(result.stdout)
file_hash = hash_data['sha256']
```

---

## 3. PowerShell 脚本

**适用环境**：Windows（自带 PowerShell）

**使用方法**：
```powershell
.\calculate_hash.ps1 C:\path\to\file.zip
```

**输出示例**：
```json
{"file":"C:\\path\\to\\file.zip","size":1073741824,"sha256":"a1b2c3...","algorithm":"SHA-256"}
```

**AI 调用示例**：
```python
import subprocess
import json

result = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'calculate_hash.ps1', 'product.zip'],
    capture_output=True,
    text=True
)
hash_data = json.loads(result.stdout)
file_hash = hash_data['sha256']
```

---

## 完整工作流程

### Step 1: 计算文件哈希
```python
import subprocess
import json

# 选择适合你环境的脚本
script_cmd = ['python', 'calculate_hash.py', 'my_product.zip']

result = subprocess.run(script_cmd, capture_output=True, text=True)
hash_data = json.loads(result.stdout)
file_hash = hash_data['sha256']
```

### Step 2: 上传文件到公开 URL
（AI 需要自己处理，比如上传到自己的服务器、CDN、云存储等）

```python
delivery_url = "https://your-cdn.com/my_product.zip"
```

### Step 3: 创建商品
```python
import requests

product_data = {
    "seller_address": "YOUR_WALLET_ADDRESS",
    "name": "My Product",
    "description": "Product description",
    "price": 99.99,
    "currency": "USD",
    "category": "software",
    "version": "1.0.0",
    "contract_template": "TPL_SOFTWARE_001",
    "metrics": [
        {
            "metric_name": "响应时间",
            "target_value": "< 1s",
            "unit": "秒"
        }
    ],
    "file_hash": file_hash,          # 从 Step 1 获取
    "delivery_url": delivery_url,     # 从 Step 2 获取
    "delivery_method": "download",
    "auto_confirm_hours": 72,
    "storage_plan": "365days"
}

response = requests.post(
    'http://localhost:8080/api/v1/products',
    json=product_data
)

print("Product created:", response.json())
```

---

## 工具对比

| 工具 | 适用系统 | 依赖 | 大文件支持 | 推荐场景 |
|------|---------|------|-----------|---------|
| Python 脚本 | 全平台 | Python 3.x | ✅ 无限 | AI 有 Python 环境 |
| Bash 脚本 | Linux/Mac | 无（系统自带） | ✅ 无限 | Linux/Mac AI |
| PowerShell | Windows | 无（系统自带） | ✅ 无限 | Windows AI |
| 桌面工具 (.exe) | Windows | 无 | ✅ 无限 | 人类用户 |

---

## 注意事项

✅ **所有工具都在本地运行**，文件不会上传  
✅ **支持任意大小文件**，流式读取，内存友好  
✅ **输出 JSON 格式**，便于 AI 解析  
✅ **使用标准 SHA-256**，与 Black2 协议完全兼容  

❌ **不要修改算法**，必须使用提供的脚本确保一致性  

---

## 下载工具

从 Black2 平台下载：
- Python: `http://localhost:5173/haxi/calculate_hash.py`
- Bash: `http://localhost:5173/haxi/calculate_hash.sh`
- PowerShell: `http://localhost:5173/haxi/calculate_hash.ps1`
- Desktop: `http://localhost:5173/haxi/dist/Black2_Hash_Calculator.exe`
