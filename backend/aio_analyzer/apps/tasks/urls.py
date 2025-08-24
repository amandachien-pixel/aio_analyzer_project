"""
任務應用 URL 路由
================

提供 Celery 任務監控和管理相關的 API 端點。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'executions', views.TaskExecutionViewSet)
router.register(r'queues', views.TaskQueueViewSet)
router.register(r'stats', views.TaskStatsViewSet)
router.register(r'alerts', views.TaskAlertViewSet)
router.register(r'workers', views.WorkerStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # 任務監控端點
    path('monitor/overview/', views.TaskMonitorOverviewView.as_view(), name='task-monitor-overview'),
    path('monitor/active/', views.ActiveTasksView.as_view(), name='active-tasks'),
    path('monitor/failed/', views.FailedTasksView.as_view(), name='failed-tasks'),
    path('monitor/queues/', views.QueueStatusView.as_view(), name='queue-status'),
    
    # 任務管理端點
    path('management/retry/<str:task_id>/', views.RetryTaskView.as_view(), name='retry-task'),
    path('management/revoke/<str:task_id>/', views.RevokeTaskView.as_view(), name='revoke-task'),
    path('management/purge-queue/<str:queue_name>/', views.PurgeQueueView.as_view(), name='purge-queue'),
    path('management/restart-workers/', views.RestartWorkersView.as_view(), name='restart-workers'),
    
    # 統計分析端點
    path('analytics/performance/', views.PerformanceAnalyticsView.as_view(), name='performance-analytics'),
    path('analytics/errors/', views.ErrorAnalyticsView.as_view(), name='error-analytics'),
    path('analytics/usage-trends/', views.UsageTrendsView.as_view(), name='usage-trends'),
    path('analytics/user-activity/', views.UserActivityView.as_view(), name='user-activity'),
    
    # 警報管理端點
    path('alerts/<uuid:alert_id>/acknowledge/', views.AcknowledgeAlertView.as_view(), name='acknowledge-alert'),
    path('alerts/<uuid:alert_id>/resolve/', views.ResolveAlertView.as_view(), name='resolve-alert'),
    path('alerts/<uuid:alert_id>/ignore/', views.IgnoreAlertView.as_view(), name='ignore-alert'),
    path('alerts/bulk-acknowledge/', views.BulkAcknowledgeAlertsView.as_view(), name='bulk-acknowledge-alerts'),
    
    # Worker 管理端點
    path('workers/<str:hostname>/details/', views.WorkerDetailsView.as_view(), name='worker-details'),
    path('workers/<str:hostname>/shutdown/', views.ShutdownWorkerView.as_view(), name='shutdown-worker'),
    path('workers/<str:hostname>/ping/', views.PingWorkerView.as_view(), name='ping-worker'),
    path('workers/health-check/', views.WorkersHealthCheckView.as_view(), name='workers-health-check'),
    
    # 配置管理端點
    path('config/task-routes/', views.TaskRoutesConfigView.as_view(), name='task-routes-config'),
    path('config/rate-limits/', views.RateLimitsConfigView.as_view(), name='rate-limits-config'),
    path('config/update/', views.UpdateTaskConfigView.as_view(), name='update-task-config'),
    
    # 工具端點
    path('tools/cleanup/', views.CleanupTaskDataView.as_view(), name='cleanup-task-data'),
    path('tools/export-logs/', views.ExportTaskLogsView.as_view(), name='export-task-logs'),
    path('tools/system-status/', views.SystemStatusView.as_view(), name='system-status'),
]
