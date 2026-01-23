# 使用 Python 3.9 作为基础镜像
# 强制触发云托管构建更新 - 2026-01-24
FROM python:3.9-slim

# 安装 FFmpeg 和其他依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 backend 目录下的依赖文件
COPY backend/requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制 backend 目录下的所有代码到容器的工作目录
COPY backend/ .

# 创建上传目录
RUN mkdir -p uploads/original uploads/processed uploads/thumbnails

# 暴露端口 (微信云托管默认监听 80)
EXPOSE 80

# 启动命令
CMD ["python", "run.py"]
