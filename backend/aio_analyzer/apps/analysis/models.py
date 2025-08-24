"""
分析數據模型
============

實現軟體開發規格書中定義的四大核心模組 (M1-M4) 的數據模型。
包括分析任務、關鍵字數據和 AIO 驗證結果。
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
import json

User = get_user_model()


class AnalysisProject(models.Model):
    """
    分析項目
    代表一個完整的 AIO 分析項目，包含所有相關的分析任務
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_projects')
    
    # 基本資訊
    name = models.CharField(max_length=200, verbose_name='項目名稱')
    description = models.TextField(blank=True, verbose_name='項目描述')
    
    # 分析參數
    target_site_url = models.URLField(verbose_name='目標網站 URL')
    start_date = models.DateField(verbose_name='開始日期')
    end_date = models.DateField(verbose_name='結束日期')
    regex_pattern = models.CharField(
        max_length=500,
        default=r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b',
        verbose_name='篩選正則表達式'
    )
    
    # 狀態追蹤
    STATUS_CHOICES = [
        ('created', '已創建'),
        ('running', '執行中'),
        ('completed', '已完成'),
        ('failed', '失敗'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    # 進度追蹤
    total_steps = models.IntegerField(default=4)  # M1-M4 四個模組
    completed_steps = models.IntegerField(default=0)
    current_step = models.CharField(max_length=50, blank=True)
    
    # 結果統計
    total_keywords = models.IntegerField(default=0)
    aio_keywords = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)
    
    # 錯誤資訊
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('分析項目')
        verbose_name_plural = _('分析項目')
        db_table = 'analysis_project'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def duration(self):
        """計算執行時間"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def aio_percentage(self):
        """計算 AIO 觸發率"""
        if self.total_keywords > 0:
            return (self.aio_keywords / self.total_keywords) * 100
        return 0.0


class AnalysisTask(models.Model):
    """
    分析任務
    代表分析項目中的單個模組任務 (M1-M4)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(AnalysisProject, on_delete=models.CASCADE, related_name='tasks')
    
    # 任務資訊
    TASK_TYPES = [
        ('gsc_extraction', 'M1: GSC 數據擷取'),
        ('keyword_expansion', 'M2: 關鍵字擴展'),
        ('aio_validation', 'M3: AIO 驗證'),
        ('report_generation', 'M4: 報告生成'),
    ]
    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    
    # 任務狀態
    STATUS_CHOICES = [
        ('pending', '待執行'),
        ('running', '執行中'),
        ('completed', '已完成'),
        ('failed', '失敗'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 任務參數
    parameters = models.JSONField(default=dict)
    
    # 結果數據
    result_data = models.JSONField(default=dict, blank=True)
    result_count = models.IntegerField(default=0)
    
    # Celery 任務 ID
    celery_task_id = models.CharField(max_length=100, blank=True)
    
    # 進度追蹤
    progress_percentage = models.FloatField(default=0.0)
    current_operation = models.CharField(max_length=200, blank=True)
    
    # 錯誤資訊
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('分析任務')
        verbose_name_plural = _('分析任務')
        db_table = 'analysis_task'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.get_task_type_display()}"


class KeywordData(models.Model):
    """
    關鍵字數據
    儲存從 GSC 和 Google Ads API 獲取的關鍵字資訊
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(AnalysisProject, on_delete=models.CASCADE, related_name='keywords')
    
    # 關鍵字基本資訊
    keyword = models.CharField(max_length=500, verbose_name='關鍵字')
    
    # 數據來源
    SOURCE_TYPES = [
        ('gsc', 'Google Search Console'),
        ('ads_expansion', 'Google Ads 擴展'),
        ('manual', '手動輸入'),
    ]
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    # GSC 數據 (M1 模組)
    gsc_clicks = models.IntegerField(null=True, blank=True, verbose_name='GSC 點擊數')
    gsc_impressions = models.IntegerField(null=True, blank=True, verbose_name='GSC 曝光數')
    gsc_ctr = models.FloatField(null=True, blank=True, verbose_name='GSC 點閱率')
    gsc_position = models.FloatField(null=True, blank=True, verbose_name='GSC 平均排名')
    
    # Google Ads 數據 (M2 模組)
    ads_search_volume = models.IntegerField(null=True, blank=True, verbose_name='月搜尋量')
    ads_competition_level = models.CharField(
        max_length=20,
        choices=[('LOW', '低'), ('MEDIUM', '中'), ('HIGH', '高')],
        blank=True,
        verbose_name='競爭程度'
    )
    ads_competition_index = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='競爭指數'
    )
    ads_low_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最低出價'
    )
    ads_high_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最高出價'
    )
    
    # AIO 驗證數據 (M3 模組)
    aio_verified = models.BooleanField(null=True, verbose_name='已驗證 AIO')
    aio_triggers = models.BooleanField(null=True, verbose_name='觸發 AIO')
    aio_content = models.TextField(blank=True, verbose_name='AIO 內容摘要')
    aio_verified_at = models.DateTimeField(null=True, blank=True)
    
    # SERP 相關數據
    serp_total_results = models.BigIntegerField(null=True, blank=True)
    serp_response_time = models.FloatField(null=True, blank=True)
    
    # 元數據
    metadata = models.JSONField(default=dict, blank=True)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('關鍵字數據')
        verbose_name_plural = _('關鍵字數據')
        db_table = 'analysis_keyword_data'
        unique_together = ['project', 'keyword']
        indexes = [
            models.Index(fields=['project', 'aio_triggers']),
            models.Index(fields=['project', 'ads_search_volume']),
            models.Index(fields=['keyword']),
        ]
    
    def __str__(self):
        return f"{self.keyword} ({self.project.name})"


class SERPResult(models.Model):
    """
    SERP 搜尋結果
    儲存詳細的 SERP API 回應數據
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keyword_data = models.OneToOneField(
        KeywordData, 
        on_delete=models.CASCADE, 
        related_name='serp_result'
    )
    
    # SERP API 參數
    api_provider = models.CharField(max_length=50, default='serpapi')
    search_engine = models.CharField(max_length=20, default='google')
    location = models.CharField(max_length=100, default='Taiwan')
    language = models.CharField(max_length=10, default='zh-tw')
    
    # 搜尋結果
    total_results = models.BigIntegerField(null=True, blank=True)
    search_time = models.FloatField(null=True, blank=True)
    
    # AIO 檢測結果
    has_ai_overview = models.BooleanField(default=False)
    ai_overview_content = models.TextField(blank=True)
    ai_overview_source_links = models.JSONField(default=list, blank=True)
    
    # 有機搜尋結果
    organic_results = models.JSONField(default=list, blank=True)
    featured_snippet = models.JSONField(default=dict, blank=True)
    people_also_ask = models.JSONField(default=list, blank=True)
    
    # 完整 API 回應
    raw_response = models.JSONField(default=dict, blank=True)
    
    # API 請求資訊
    api_request_id = models.CharField(max_length=100, blank=True)
    api_credits_used = models.IntegerField(default=1)
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('SERP 結果')
        verbose_name_plural = _('SERP 結果')
        db_table = 'analysis_serp_result'
    
    def __str__(self):
        return f"SERP: {self.keyword_data.keyword}"


class AnalysisCache(models.Model):
    """
    分析快取
    快取常用的分析結果以提高效能
    """
    cache_key = models.CharField(max_length=255, unique=True)
    cache_data = models.JSONField()
    
    # 快取類型
    CACHE_TYPES = [
        ('keyword_expansion', '關鍵字擴展'),
        ('serp_result', 'SERP 結果'),
        ('gsc_data', 'GSC 數據'),
    ]
    cache_type = models.CharField(max_length=30, choices=CACHE_TYPES)
    
    # 過期設定
    expires_at = models.DateTimeField()
    
    # 使用統計
    hit_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('分析快取')
        verbose_name_plural = _('分析快取')
        db_table = 'analysis_cache'
        indexes = [
            models.Index(fields=['cache_type', 'expires_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache: {self.cache_key}"
    
    def is_expired(self):
        """檢查快取是否過期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
