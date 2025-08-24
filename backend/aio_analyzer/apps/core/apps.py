"""
核心應用配置
============

AIO 分析器核心應用，提供基礎功能和用戶管理。
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aio_analyzer.apps.core'
    verbose_name = '核心功能'
    
    def ready(self):
        """應用啟動時執行的初始化代碼"""
        import aio_analyzer.apps.core.signals
