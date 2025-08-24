"""
任務數據模型
============

Celery 任務的監控、管理和統計功能。
提供任務執行狀態追蹤和效能分析。
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class TaskExecution(models.Model):
    """
    任務執行記錄
    追蹤 Celery 任務的詳細執行情況
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Celery 任務資訊
    celery_task_id = models.CharField(max_length=100, unique=True)
    task_name = models.CharField(max_length=200)
    
    # 關聯的分析任務
    analysis_task = models.ForeignKey(
        'analysis.AnalysisTask',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='executions'
    )
    
    # 執行用戶
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 任務狀態
    STATUS_CHOICES = [
        ('PENDING', '待執行'),
        ('STARTED', '已開始'),
        ('SUCCESS', '成功'),
        ('FAILURE', '失敗'),
        ('RETRY', '重試中'),
        ('REVOKED', '已撤銷'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 執行參數
    task_args = models.JSONField(default=list, blank=True)
    task_kwargs = models.JSONField(default=dict, blank=True)
    
    # 執行結果
    result = models.JSONField(default=dict, blank=True)
    traceback = models.TextField(blank=True)
    
    # 效能數據
    runtime_seconds = models.FloatField(null=True, blank=True)
    memory_usage_mb = models.FloatField(null=True, blank=True)
    cpu_usage_percent = models.FloatField(null=True, blank=True)
    
    # Worker 資訊
    worker_hostname = models.CharField(max_length=200, blank=True)
    worker_pid = models.IntegerField(null=True, blank=True)
    
    # 重試資訊
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('任務執行記錄')
        verbose_name_plural = _('任務執行記錄')
        db_table = 'tasks_execution'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['celery_task_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.task_name} - {self.status}"
    
    @property
    def duration(self):
        """計算任務執行時間"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class TaskQueue(models.Model):
    """
    任務隊列監控
    監控不同隊列的狀態和負載情況
    """
    queue_name = models.CharField(max_length=100, unique=True)
    
    # 隊列統計
    pending_tasks = models.IntegerField(default=0)
    active_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    failed_tasks = models.IntegerField(default=0)
    
    # 效能指標
    avg_processing_time = models.FloatField(default=0.0)
    throughput_per_hour = models.FloatField(default=0.0)
    
    # Worker 資訊
    active_workers = models.IntegerField(default=0)
    worker_hostnames = models.JSONField(default=list, blank=True)
    
    # 狀態
    is_active = models.BooleanField(default=True)
    
    # 時間戳記
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('任務隊列')
        verbose_name_plural = _('任務隊列')
        db_table = 'tasks_queue'
    
    def __str__(self):
        return f"Queue: {self.queue_name}"


class TaskStats(models.Model):
    """
    任務統計
    定期收集的任務執行統計數據
    """
    # 統計週期
    PERIOD_CHOICES = [
        ('hourly', '每小時'),
        ('daily', '每日'),
        ('weekly', '每週'),
        ('monthly', '每月'),
    ]
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # 任務統計
    total_tasks = models.IntegerField(default=0)
    successful_tasks = models.IntegerField(default=0)
    failed_tasks = models.IntegerField(default=0)
    retried_tasks = models.IntegerField(default=0)
    
    # 任務類型分布
    task_type_distribution = models.JSONField(default=dict, blank=True)
    
    # 效能統計
    avg_runtime = models.FloatField(default=0.0)
    max_runtime = models.FloatField(default=0.0)
    min_runtime = models.FloatField(default=0.0)
    
    # 用戶統計
    active_users = models.IntegerField(default=0)
    tasks_per_user = models.JSONField(default=dict, blank=True)
    
    # 錯誤統計
    error_types = models.JSONField(default=dict, blank=True)
    most_common_errors = models.JSONField(default=list, blank=True)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('任務統計')
        verbose_name_plural = _('任務統計')
        db_table = 'tasks_stats'
        unique_together = ['period', 'period_start']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.get_period_display()} ({self.period_start})"
    
    @property
    def success_rate(self):
        """計算成功率"""
        if self.total_tasks > 0:
            return (self.successful_tasks / self.total_tasks) * 100
        return 0.0


class TaskAlert(models.Model):
    """
    任務警報
    監控任務異常並發送警報
    """
    # 警報類型
    ALERT_TYPES = [
        ('high_failure_rate', '高失敗率'),
        ('long_queue_time', '隊列時間過長'),
        ('worker_down', 'Worker 離線'),
        ('memory_usage', '記憶體使用過高'),
        ('custom', '自定義'),
    ]
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    
    # 警報內容
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # 觸發條件
    trigger_conditions = models.JSONField(default=dict)
    
    # 嚴重程度
    SEVERITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '緊急'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    # 狀態
    STATUS_CHOICES = [
        ('active', '活躍'),
        ('acknowledged', '已確認'),
        ('resolved', '已解決'),
        ('ignored', '已忽略'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # 相關數據
    related_tasks = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # 處理資訊
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # 通知設定
    notification_sent = models.BooleanField(default=False)
    notification_channels = models.JSONField(default=list, blank=True)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('任務警報')
        verbose_name_plural = _('任務警報')
        db_table = 'tasks_alert'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['severity', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.get_severity_display()}"


class WorkerStatus(models.Model):
    """
    Worker 狀態監控
    追蹤 Celery Worker 的健康狀態
    """
    hostname = models.CharField(max_length=200, unique=True)
    
    # Worker 資訊
    worker_pid = models.IntegerField()
    software_info = models.JSONField(default=dict, blank=True)
    
    # 狀態資訊
    is_online = models.BooleanField(default=True)
    active_tasks = models.IntegerField(default=0)
    processed_tasks = models.IntegerField(default=0)
    
    # 資源使用
    cpu_usage = models.FloatField(default=0.0)
    memory_usage = models.FloatField(default=0.0)
    load_average = models.JSONField(default=list, blank=True)
    
    # 隊列資訊
    queues = models.JSONField(default=list, blank=True)
    
    # 健康檢查
    last_heartbeat = models.DateTimeField(auto_now=True)
    uptime_seconds = models.BigIntegerField(default=0)
    
    # 時間戳記
    first_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Worker 狀態')
        verbose_name_plural = _('Worker 狀態')
        db_table = 'tasks_worker_status'
    
    def __str__(self):
        return f"Worker: {self.hostname}"
    
    def is_healthy(self):
        """檢查 Worker 是否健康"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 檢查心跳時間
        if timezone.now() - self.last_heartbeat > timedelta(minutes=5):
            return False
        
        # 檢查資源使用
        if self.cpu_usage > 90 or self.memory_usage > 90:
            return False
        
        return self.is_online
