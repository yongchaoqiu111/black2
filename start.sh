#!/usr/bin/env bash
# Black2 Clearing Protocol - 快速启动脚本 (Linux/macOS)

set -e  # 遇到错误立即退出

echo "========================================="
echo "  Black2 Clearing Protocol 启动脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${YELLOW}检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

# 检查Node.js版本
echo -e "${YELLOW}检查 Node.js 版本...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js 16+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js 版本: $NODE_VERSION${NC}"
echo ""

# 后端设置
echo "========================================="
echo "  设置后端服务"
echo "========================================="
echo ""

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建 Python 虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装 Python 依赖...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件${NC}"
    if [ -f "../.env.example" ]; then
        echo -e "${YELLOW}从 .env.example 复制配置...${NC}"
        cp ../.env.example .env
        echo -e "${RED}请编辑 backend/.env 文件，填入 GitHub Token 等配置${NC}"
        echo -e "${RED}按 Ctrl+C 取消，或按 Enter 继续（使用默认配置）...${NC}"
        read -r
    fi
fi

cd ..

# 前端设置
echo "========================================="
echo "  设置前端应用"
echo "========================================="
echo ""

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安装 Node.js 依赖...${NC}"
    npm install
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 前端依赖已存在${NC}"
fi

cd ..
echo ""

# 启动服务
echo "========================================="
echo "  启动服务"
echo "========================================="
echo ""

echo -e "${GREEN}后端服务将运行在: http://localhost:8000${NC}"
echo -e "${GREEN}前端服务将运行在: http://localhost:5173${NC}"
echo -e "${GREEN}API文档: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止所有服务${NC}"
echo ""

# 启动后端（后台运行）
echo -e "${YELLOW}启动后端服务...${NC}"
cd backend
source venv/bin/activate
python server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo -e "${YELLOW}启动前端开发服务器...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✓ 所有服务已启动！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "后端 PID: $BACKEND_PID"
echo "前端 PID: $FRONTEND_PID"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: 直接在终端查看"
echo ""
echo "停止服务:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 等待用户中断
wait
