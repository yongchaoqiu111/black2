# Black2 Clearing Protocol - 快速启动脚本 (Windows PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Black2 Clearing Protocol 启动脚本" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python版本
Write-Host "检查 Python 版本..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到 Python，请先安装 Python 3.9+" -ForegroundColor Red
    exit 1
}

# 检查Node.js版本
Write-Host "检查 Node.js 版本..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到 Node.js，请先安装 Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 后端设置
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  设置后端服务" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装 Python 依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ 后端依赖安装完成" -ForegroundColor Green
Write-Host ""

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "警告: 未找到 .env 文件" -ForegroundColor Yellow
    if (Test-Path "..\.env.example") {
        Write-Host "从 .env.example 复制配置..." -ForegroundColor Yellow
        Copy-Item "..\.env.example" ".env"
        Write-Host "请编辑 backend\.env 文件，填入 GitHub Token 等配置" -ForegroundColor Red
        Write-Host "按 Ctrl+C 取消，或按 Enter 继续（使用默认配置）..." -ForegroundColor Red
        Read-Host
    }
}

Set-Location ..

# 前端设置
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  设置前端应用" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

# 安装依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "安装 Node.js 依赖..." -ForegroundColor Yellow
    npm install
    Write-Host "✓ 前端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "✓ 前端依赖已存在" -ForegroundColor Green
}

Set-Location ..
Write-Host ""

# 创建日志目录
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# 启动服务
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  启动服务" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "后端服务将运行在: http://localhost:8000" -ForegroundColor Green
Write-Host "前端服务将运行在: http://localhost:5173" -ForegroundColor Green
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "提示: 按 Ctrl+C 停止所有服务" -ForegroundColor Yellow
Write-Host ""

# 启动后端（新窗口）
Write-Host "启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; python server.py"

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端（新窗口）
Write-Host "启动前端开发服务器..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  ✓ 所有服务已启动！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "已在两个新窗口中启动:" -ForegroundColor White
Write-Host "  - 后端服务 (backend)" -ForegroundColor White
Write-Host "  - 前端服务 (frontend)" -ForegroundColor White
Write-Host ""
Write-Host "访问地址:" -ForegroundColor White
Write-Host "  - 前端: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  - 后端API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "关闭这两个窗口即可停止服务" -ForegroundColor Yellow
Write-Host ""
