"""
核心數據模型
============

定義用戶配置、API 憑證和系統設定等核心數據模型。
按照軟體開發規格書要求支持多用戶和 OAuth 認證。
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """
    擴展的用戶模型
    支持 Google OAuth 2.0 認證和個人化設定
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('電子郵件'), unique=True)
    first_name = models.CharField(_('名字'), max_length=150, blank=True)
    last_name = models.CharField(_('姓氏'), max_length=150, blank=True)
    
    # OAuth 相關欄位
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    # 用戶偏好設定
    preferred_language = models.CharField(
        max_length=10,
        choices=[('zh-tw', '繁體中文'), ('en', 'English')],
        default='zh-tw'
    )
    timezone = models.CharField(max_length=50, default='Asia/Taipei')
    
    # 帳戶狀態
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('用戶')
        verbose_name_plural = _('用戶')
        db_table = 'core_user'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """獲取完整姓名"""
        return f"{self.last_name}{self.first_name}".strip()


class UserProfile(models.Model):
    """
    用戶配置檔案
    儲存用戶的 API 設定和分析偏好
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Google API 設定
    gsc_site_urls = models.JSONField(
        default=list,
        help_text='授權的 Google Search Console 網站列表'
    )
    google_ads_customer_id = models.CharField(
        max_length=50,
        blank=True,
        validators=[RegexValidator(r'^[\d-]+$', '請輸入有效的客戶 ID 格式')]
    )
    
    # 分析偏好設定
    default_date_range = models.IntegerField(
        default=90,
        help_text='默認分析天數'
    )
    default_regex_pattern = models.CharField(
        max_length=500,
        default=r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b',
        help_text='默認關鍵字篩選正則表達式'
    )
    
    # SERP API 設定
    serp_api_provider = models.CharField(
        max_length=50,
        choices=[
            ('serpapi', 'SerpApi'),
            ('scaleserp', 'ScaleSerp'),
            ('other', '其他'),
        ],
        default='serpapi'
    )
    serp_api_key = models.CharField(max_length=200, blank=True)
    
    # 通知設定
    email_notifications = models.BooleanField(default=True)
    task_completion_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('用戶配置')
        verbose_name_plural = _('用戶配置')
        db_table = 'core_user_profile'
    
    def __str__(self):
        return f"{self.user.email} 的配置"


class APICredential(models.Model):
    """
    API 憑證管理
    安全地儲存各種 API 憑證和令牌
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_credentials')
    
    # 憑證類型
    CREDENTIAL_TYPES = [
        ('gsc_oauth', 'Google Search Console OAuth'),
        ('google_ads', 'Google Ads API'),
        ('serp_api', 'SERP API'),
    ]
    
    credential_type = models.CharField(max_length=50, choices=CREDENTIAL_TYPES)
    name = models.CharField(max_length=100, help_text='憑證名稱')
    
    # 憑證數據（加密儲存）
    credentials_data = models.JSONField(
        help_text='憑證數據（將自動加密）'
    )
    
    # 狀態追蹤
    is_active = models.BooleanField(default=True)
    is_valid = models.BooleanField(default=True)
    last_validated = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('API 憑證')
        verbose_name_plural = _('API 憑證')
        db_table = 'core_api_credential'
        unique_together = ['user', 'credential_type', 'name']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_credential_type_display()}"


class SystemConfiguration(models.Model):
    """
    系統配置
    儲存全局系統設定和參數
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    # 配置類型
    CONFIG_TYPES = [
        ('string', '字符串'),
        ('integer', '整數'),
        ('float', '浮點數'),
        ('boolean', '布林值'),
        ('json', 'JSON'),
    ]
    
    value_type = models.CharField(max_length=20, choices=CONFIG_TYPES, default='string')
    
    # 分類
    category = models.CharField(
        max_length=50,
        choices=[
            ('api', 'API 設定'),
            ('performance', '效能設定'),
            ('security', '安全設定'),
            ('feature', '功能設定'),
        ],
        default='api'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('系統配置')
        verbose_name_plural = _('系統配置')
        db_table = 'core_system_configuration'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    def get_typed_value(self):
        """根據類型返回正確的值"""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class AuditLog(models.Model):
    """
    審計日誌
    記錄重要的系統操作和用戶行為
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 操作資訊
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100, blank=True)
    
    # 詳細資訊
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # 請求資訊
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # 結果
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('審計日誌')
        verbose_name_plural = _('審計日誌')
        db_table = 'core_audit_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"
