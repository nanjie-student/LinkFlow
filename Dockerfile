# 使用更轻量的 Python 3.12
FROM python:3.12-slim

# 设置 Flask 运行端口
EXPOSE 5000

# 防止生成 .pyc 文件，优化 Docker 容器
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 复制所有项目文件
COPY . /app

# 安装 Python 依赖
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# 设置 Kafka 服务器环境变量
ENV KAFKA_BROKER=kafka:9092

# 使用非 root 用户运行应用
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 运行 Flask 应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]