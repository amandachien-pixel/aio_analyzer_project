"""
AIO 分析器 Celery 配置
=====================

配置 Celery 任務隊列系統，用於異步處理 SERP API 請求和其他耗時任務。
按照軟體開發規格書要求實現異步處理架構。
"""

import os
from celery import Celery
from django.conf import settings

# 設置 Django 設定模組
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aio_analyzer.settings')

# 創建 Celery 應用
app = Celery('aio_analyzer')

# 使用字符串指定配置，這樣 worker 子進程不需要序列化配置對象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動發現任務模組
app.autodiscover_tasks()

# 任務路由配置
app.conf.task_routes = {
    'aio_analyzer.apps.analysis.tasks.extract_gsc_data': {'queue': 'gsc'},
    'aio_analyzer.apps.analysis.tasks.expand_keywords': {'queue': 'ads'},
    'aio_analyzer.apps.analysis.tasks.validate_aio_triggers': {'queue': 'serp'},
    'aio_analyzer.apps.reports.tasks.generate_report': {'queue': 'reports'},
}

# 任務優先級設定
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1

# 結果過期時間（秒）
app.conf.result_expires = 3600 * 24  # 24 hours

# 任務時間限制
app.conf.task_time_limit = 30 * 60  # 30 minutes
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes

# 錯誤處理
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_late = True

# 調試任務（開發環境）
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat 週期性任務配置
app.conf.beat_schedule = {
    'cleanup-old-reports': {
        'task': 'aio_analyzer.apps.reports.tasks.cleanup_old_reports',
        'schedule': 86400.0,  # 每天執行一次
    },
    'cleanup-expired-tasks': {
        'task': 'aio_analyzer.apps.tasks.tasks.cleanup_expired_tasks',
        'schedule': 3600.0,  # 每小時執行一次
    },
}

app.conf.timezone = settings.TIME_ZONE
