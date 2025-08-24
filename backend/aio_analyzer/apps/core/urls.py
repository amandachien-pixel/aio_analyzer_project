"""
核心應用 URL 路由
================

提供用戶管理、認證和系統配置相關的 API 端點。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'api-credentials', views.APICredentialViewSet)
router.register(r'system-config', views.SystemConfigurationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/google/', views.GoogleAuthView.as_view(), name='google-auth'),
    path('auth/verify/', views.VerifyTokenView.as_view(), name='verify-token'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
