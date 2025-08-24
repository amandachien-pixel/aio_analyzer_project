"""
分析應用配置
============

AIO 分析器的核心分析功能應用，實現 M1-M3 模組。
"""

from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aio_analyzer.apps.analysis'
    verbose_name = '分析功能'
