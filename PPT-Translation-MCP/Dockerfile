# 使用 Python 3.12 官方轻量级镜像
FROM python:3.12-slim

# 安装 uv 包管理器
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app

# 将项目文件复制到容器内
COPY . /app/

# 安装项目依赖（使用 uv 可以极大加快安装速度）
RUN uv sync --frozen --no-cache

# 暴露可能用到的 SSE 端口（默认 8000）
EXPOSE 8000

# 默认环境变量
ENV PRS_AI_MCP_BASE_URL="https://prsai.cc"
ENV PORT=8000
ENV HOST="0.0.0.0"

# 容器启动命令，使用 uv 运行项目
ENTRYPOINT ["uv", "run", "prs-ai-staging-mcp"]
