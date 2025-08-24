"""
分析應用 URL 路由
================

提供 AIO 分析功能相關的 API 端點，實現 M1-M3 模組功能。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.AnalysisProjectViewSet)
router.register(r'tasks', views.AnalysisTaskViewSet)
router.register(r'keywords', views.KeywordDataViewSet)
router.register(r'serp-results', views.SERPResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # 分析項目相關端點
    path('projects/<uuid:project_id>/start/', views.StartAnalysisView.as_view(), name='start-analysis'),
    path('projects/<uuid:project_id>/stop/', views.StopAnalysisView.as_view(), name='stop-analysis'),
    path('projects/<uuid:project_id>/status/', views.ProjectStatusView.as_view(), name='project-status'),
    path('projects/<uuid:project_id>/export/', views.ExportDataView.as_view(), name='export-data'),
    
    # 任務相關端點
    path('tasks/<uuid:task_id>/progress/', views.TaskProgressView.as_view(), name='task-progress'),
    path('tasks/<uuid:task_id>/retry/', views.RetryTaskView.as_view(), name='retry-task'),
    path('tasks/<uuid:task_id>/cancel/', views.CancelTaskView.as_view(), name='cancel-task'),
    
    # 關鍵字相關端點
    path('keywords/bulk-import/', views.BulkImportKeywordsView.as_view(), name='bulk-import-keywords'),
    path('keywords/bulk-validate/', views.BulkValidateAIOView.as_view(), name='bulk-validate-aio'),
    path('keywords/export/', views.ExportKeywordsView.as_view(), name='export-keywords'),
    
    # 統計和分析端點
    path('statistics/overview/', views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('statistics/trends/', views.TrendsAnalysisView.as_view(), name='trends-analysis'),
    path('statistics/keywords/', views.KeywordStatsView.as_view(), name='keyword-stats'),
    
    # 工具端點
    path('tools/validate-gsc-url/', views.ValidateGSCUrlView.as_view(), name='validate-gsc-url'),
    path('tools/test-api-connection/', views.TestAPIConnectionView.as_view(), name='test-api-connection'),
    path('tools/keyword-suggestions/', views.KeywordSuggestionsView.as_view(), name='keyword-suggestions'),
]
