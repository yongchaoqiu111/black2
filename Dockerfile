# 多阶段构建 - 后端
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY backend/ .

# ============================================
# 多阶段构建 - 前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 安装依赖
COPY frontend/package*.json ./
RUN npm ci

# 复制源代码并构建
COPY frontend/ .
RUN npm run build

# ============================================
# 生产环境镜像
FROM python:3.11-slim

LABEL maintainer="Black2 Protocol Team"
LABEL description="Black2 Clearing Protocol - AI-to-AI Trusted Trading Platform"

WORKDIR /app

# 安装Node.js（用于serve前端静态文件）
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制后端
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app/backend /app/backend

# 从builder阶段复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 创建日志目录
RUN mkdir -p /app/logs

# 复制启动脚本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# 启动命令
CMD ["python", "backend/server.py"]
