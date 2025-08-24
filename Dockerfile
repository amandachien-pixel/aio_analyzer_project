# AIO 分析器 Dockerfile
# ======================
# 多階段構建，支持開發和生產環境

# 基礎映像
FROM python:3.11-slim as base

# 設置環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    redis-tools \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 創建應用用戶
RUN useradd --create-home --shell /bin/bash aiouser

# 設置工作目錄
WORKDIR /app

# 複製 requirements 文件
COPY requirements-web.txt ./

# 安裝 Python 依賴
RUN pip install --upgrade pip && \
    pip install -r requirements-web.txt

# 開發階段
FROM base as development

# 安裝開發依賴
RUN pip install \
    django-debug-toolbar \
    pytest-django \
    factory-boy \
    black \
    flake8

# 複製源代碼
COPY . .

# 創建必要目錄
RUN mkdir -p logs media static staticfiles

# 設置權限
RUN chown -R aiouser:aiouser /app

# 切換到應用用戶
USER aiouser

# 暴露端口
EXPOSE 8000

# 開發環境啟動命令
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]

# 生產階段
FROM base as production

# 安裝生產依賴
RUN pip install gunicorn

# 複製源代碼
COPY . .

# 創建必要目錄
RUN mkdir -p logs media static staticfiles

# 收集靜態文件
RUN python backend/manage.py collectstatic --noinput

# 設置權限
RUN chown -R aiouser:aiouser /app

# 切換到應用用戶
USER aiouser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/core/health/ || exit 1

# 生產環境啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "aio_analyzer.wsgi:application"]

# Celery Worker 階段
FROM base as celery-worker

# 複製源代碼
COPY . .

# 創建必要目錄
RUN mkdir -p logs

# 設置權限
RUN chown -R aiouser:aiouser /app

# 切換到應用用戶
USER aiouser

# Celery Worker 啟動命令
CMD ["celery", "-A", "aio_analyzer", "worker", "--loglevel=info", "--concurrency=4"]

# Celery Beat 階段
FROM base as celery-beat

# 複製源代碼
COPY . .

# 創建必要目錄
RUN mkdir -p logs

# 設置權限
RUN chown -R aiouser:aiouser /app

# 切換到應用用戶
USER aiouser

# Celery Beat 啟動命令
CMD ["celery", "-A", "aio_analyzer", "beat", "--loglevel=info", "--scheduler=django_celery_beat.schedulers:DatabaseScheduler"]
