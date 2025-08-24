"""
任務應用配置
============

AIO 分析器任務管理應用，提供 Celery 任務的監控和管理功能。
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aio_analyzer.apps.tasks'
    verbose_name = '任務管理'
