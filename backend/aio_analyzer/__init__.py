# AIO 分析器 Django 項目

# 這確保了 Celery 應用總是在 Django 啟動時被導入
from .celery import app as celery_app

__all__ = ('celery_app',)