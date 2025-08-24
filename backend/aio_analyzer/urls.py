"""
AIO 分析器 URL 配置
==================

主 URL 路由配置，包含 API 端點和管理介面。
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    # 管理後台
    path('admin/', admin.site.urls),
    
    # API 文檔
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # OAuth 認證
    path('auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/', include('allauth.urls')),
    
    # API 路由
    path('api/v1/core/', include('aio_analyzer.apps.core.urls')),
    path('api/v1/analysis/', include('aio_analyzer.apps.analysis.urls')),
    path('api/v1/reports/', include('aio_analyzer.apps.reports.urls')),
    path('api/v1/tasks/', include('aio_analyzer.apps.tasks.urls')),
]

# 開發環境靜態文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 調試工具欄
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
