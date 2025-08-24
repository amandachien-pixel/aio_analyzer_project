"""
分析任務
========

實現軟體開發規格書中 M1-M3 模組的 Celery 異步任務。
包括 GSC 數據擷取、關鍵字擴展和 AIO 驗證。
"""

from celery import shared_task
from celery.exceptions import Retry
from django.utils import timezone
from django.conf import settings
import logging
import asyncio
import sys
import os
from pathlib import Path

# 添加原始工具模組到路徑
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'src'))

from utils.gsc_handler import GSCHandler
from utils.ads_handler import AdsHandler
from utils.serp_handler import SERPHandler
from .models import AnalysisProject, AnalysisTask, KeywordData, SERPResult

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_gsc_data(self, project_id, task_id):
    """
    M1 模組：從 Google Search Console 擷取種子關鍵字
    
    Args:
        project_id: 分析項目 ID
        task_id: 分析任務 ID
    
    Returns:
        dict: 擷取結果統計
    """
    try:
        # 更新任務狀態
        task = AnalysisTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.celery_task_id = self.request.id
        task.current_operation = '正在連接 Google Search Console...'
        task.save()
        
        project = AnalysisProject.objects.get(id=project_id)
        project.current_step = 'M1: GSC 數據擷取'
        project.save()
        
        logger.info(f"開始 GSC 數據擷取任務 - 項目: {project.name}")
        
        # 準備配置
        config = {
            'gsc': {
                'credentials_file': settings.AIO_ANALYZER_SETTINGS['GSC_CREDENTIALS_FILE'],
                'token_file': str(Path(settings.AIO_ANALYZER_SETTINGS['GSC_CREDENTIALS_FILE']).parent / 'token.json'),
                'scopes': ['https://www.googleapis.com/auth/webmasters.readonly']
            }
        }
        
        # 初始化 GSC 處理器
        gsc_handler = GSCHandler(config, logger)
        
        # 執行異步 GSC 數據擷取
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            gsc_data = loop.run_until_complete(
                gsc_handler.get_search_analytics_data(
                    site_url=project.target_site_url,
                    start_date=project.start_date.strftime('%Y-%m-%d'),
                    end_date=project.end_date.strftime('%Y-%m-%d'),
                    regex_pattern=project.regex_pattern
                )
            )
        finally:
            loop.close()
        
        # 處理結果
        if gsc_data.empty:
            logger.warning(f"項目 {project.name} 未獲取到 GSC 數據")
            task.status = 'completed'
            task.result_data = {'message': '未找到符合條件的關鍵字'}
            task.result_count = 0
            task.completed_at = timezone.now()
            task.save()
            return {'status': 'completed', 'keywords_count': 0}
        
        # 更新進度
        task.current_operation = f'正在處理 {len(gsc_data)} 個關鍵字...'
        task.progress_percentage = 50.0
        task.save()
        
        # 儲存關鍵字數據
        keywords_created = 0
        for _, row in gsc_data.iterrows():
            keyword_data, created = KeywordData.objects.get_or_create(
                project=project,
                keyword=row['query'],
                defaults={
                    'source_type': 'gsc',
                    'gsc_clicks': row.get('clicks', 0),
                    'gsc_impressions': row.get('impressions', 0),
                    'gsc_ctr': row.get('ctr', 0.0),
                    'gsc_position': row.get('position', 0.0),
                }
            )
            if created:
                keywords_created += 1
        
        # 更新任務結果
        task.status = 'completed'
        task.result_data = {
            'total_keywords': len(gsc_data),
            'new_keywords': keywords_created,
            'gsc_stats': {
                'total_clicks': int(gsc_data['clicks'].sum()),
                'total_impressions': int(gsc_data['impressions'].sum()),
                'avg_ctr': float(gsc_data['ctr'].mean()),
                'avg_position': float(gsc_data['position'].mean())
            }
        }
        task.result_count = keywords_created
        task.progress_percentage = 100.0
        task.completed_at = timezone.now()
        task.save()
        
        # 更新項目統計
        project.completed_steps += 1
        project.total_keywords = KeywordData.objects.filter(project=project).count()
        project.save()
        
        logger.info(f"GSC 數據擷取完成 - 項目: {project.name}, 關鍵字: {keywords_created}")
        
        return {
            'status': 'completed',
            'keywords_count': keywords_created,
            'total_keywords': len(gsc_data)
        }
        
    except Exception as exc:
        logger.error(f"GSC 數據擷取任務失敗: {exc}", exc_info=True)
        
        # 更新任務錯誤狀態
        task.status = 'failed'
        task.error_message = str(exc)
        task.completed_at = timezone.now()
        task.save()
        
        # 重試邏輯
        if self.request.retries < self.max_retries:
            logger.info(f"重試 GSC 數據擷取任務 (嘗試 {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        
        raise exc


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def expand_keywords(self, project_id, task_id):
    """
    M2 模組：使用 Google Ads API 擴展關鍵字
    
    Args:
        project_id: 分析項目 ID
        task_id: 分析任務 ID
    
    Returns:
        dict: 擴展結果統計
    """
    try:
        # 更新任務狀態
        task = AnalysisTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.celery_task_id = self.request.id
        task.current_operation = '正在連接 Google Ads API...'
        task.save()
        
        project = AnalysisProject.objects.get(id=project_id)
        project.current_step = 'M2: 關鍵字擴展'
        project.save()
        
        logger.info(f"開始關鍵字擴展任務 - 項目: {project.name}")
        
        # 獲取種子關鍵字
        seed_keywords = list(KeywordData.objects.filter(
            project=project,
            source_type='gsc'
        ).values_list('keyword', flat=True))
        
        if not seed_keywords:
            logger.warning(f"項目 {project.name} 沒有種子關鍵字可供擴展")
            task.status = 'completed'
            task.result_data = {'message': '沒有種子關鍵字可供擴展'}
            task.result_count = 0
            task.completed_at = timezone.now()
            task.save()
            return {'status': 'completed', 'expanded_count': 0}
        
        # 準備配置
        config = {
            'ads': {
                'yaml_file': settings.AIO_ANALYZER_SETTINGS['GOOGLE_ADS_YAML_FILE'],
                'language_code': 'gid/1001',  # 繁體中文
                'geo_target_code': 'gid/1013274',  # 台灣
                'keyword_limit': 20
            }
        }
        
        # 初始化 Google Ads 處理器
        ads_handler = AdsHandler(config, logger)
        
        # 獲取用戶的 Google Ads 客戶 ID
        customer_id = project.user.profile.google_ads_customer_id
        if not customer_id:
            raise ValueError("用戶未設置 Google Ads 客戶 ID")
        
        # 執行異步關鍵字擴展
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            expanded_data = loop.run_until_complete(
                ads_handler.generate_keyword_ideas(
                    seed_keywords=seed_keywords[:20],  # 限制種子關鍵字數量
                    customer_id=customer_id
                )
            )
        finally:
            loop.close()
        
        if expanded_data.empty:
            logger.warning(f"項目 {project.name} 關鍵字擴展未產生結果")
            task.status = 'completed'
            task.result_data = {'message': '關鍵字擴展未產生結果'}
            task.result_count = 0
            task.completed_at = timezone.now()
            task.save()
            return {'status': 'completed', 'expanded_count': 0}
        
        # 更新進度
        task.current_operation = f'正在處理 {len(expanded_data)} 個擴展關鍵字...'
        task.progress_percentage = 50.0
        task.save()
        
        # 儲存擴展的關鍵字數據
        keywords_created = 0
        for _, row in expanded_data.iterrows():
            keyword_data, created = KeywordData.objects.get_or_create(
                project=project,
                keyword=row['keyword_idea'],
                defaults={
                    'source_type': 'ads_expansion',
                    'ads_search_volume': row.get('search_volume', 0),
                    'ads_competition_level': row.get('competition_level', ''),
                    'ads_competition_index': row.get('competition_index', 0),
                    'ads_low_bid': row.get('low_top_of_page_bid_usd', 0),
                    'ads_high_bid': row.get('high_top_of_page_bid_usd', 0),
                }
            )
            
            # 如果關鍵字已存在，更新 Ads 數據
            if not created:
                keyword_data.ads_search_volume = row.get('search_volume', 0)
                keyword_data.ads_competition_level = row.get('competition_level', '')
                keyword_data.ads_competition_index = row.get('competition_index', 0)
                keyword_data.ads_low_bid = row.get('low_top_of_page_bid_usd', 0)
                keyword_data.ads_high_bid = row.get('high_top_of_page_bid_usd', 0)
                keyword_data.save()
            else:
                keywords_created += 1
        
        # 更新任務結果
        task.status = 'completed'
        task.result_data = {
            'total_expanded': len(expanded_data),
            'new_keywords': keywords_created,
            'ads_stats': {
                'avg_search_volume': int(expanded_data['search_volume'].mean()),
                'max_search_volume': int(expanded_data['search_volume'].max()),
                'competition_distribution': expanded_data['competition_level'].value_counts().to_dict()
            }
        }
        task.result_count = keywords_created
        task.progress_percentage = 100.0
        task.completed_at = timezone.now()
        task.save()
        
        # 更新項目統計
        project.completed_steps += 1
        project.total_keywords = KeywordData.objects.filter(project=project).count()
        project.save()
        
        logger.info(f"關鍵字擴展完成 - 項目: {project.name}, 新關鍵字: {keywords_created}")
        
        return {
            'status': 'completed',
            'expanded_count': keywords_created,
            'total_expanded': len(expanded_data)
        }
        
    except Exception as exc:
        logger.error(f"關鍵字擴展任務失敗: {exc}", exc_info=True)
        
        # 更新任務錯誤狀態
        task.status = 'failed'
        task.error_message = str(exc)
        task.completed_at = timezone.now()
        task.save()
        
        # 重試邏輯
        if self.request.retries < self.max_retries:
            logger.info(f"重試關鍵字擴展任務 (嘗試 {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        
        raise exc


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def validate_aio_triggers(self, project_id, task_id):
    """
    M3 模組：驗證關鍵字是否觸發 AIO
    
    Args:
        project_id: 分析項目 ID
        task_id: 分析任務 ID
    
    Returns:
        dict: AIO 驗證結果統計
    """
    try:
        # 更新任務狀態
        task = AnalysisTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.celery_task_id = self.request.id
        task.current_operation = '正在初始化 SERP API...'
        task.save()
        
        project = AnalysisProject.objects.get(id=project_id)
        project.current_step = 'M3: AIO 驗證'
        project.save()
        
        logger.info(f"開始 AIO 驗證任務 - 項目: {project.name}")
        
        # 獲取需要驗證的關鍵字
        keywords_to_verify = KeywordData.objects.filter(
            project=project,
            aio_verified__isnull=True
        )
        
        if not keywords_to_verify.exists():
            logger.warning(f"項目 {project.name} 沒有關鍵字需要 AIO 驗證")
            task.status = 'completed'
            task.result_data = {'message': '沒有關鍵字需要 AIO 驗證'}
            task.result_count = 0
            task.completed_at = timezone.now()
            task.save()
            return {'status': 'completed', 'verified_count': 0}
        
        # 準備配置
        serp_api_key = project.user.profile.serp_api_key or settings.AIO_ANALYZER_SETTINGS['SERP_API_KEY']
        if not serp_api_key:
            raise ValueError("未設置 SERP API 金鑰")
        
        config = {
            'serp': {
                'api_key': serp_api_key,
                'endpoint': settings.AIO_ANALYZER_SETTINGS['SERP_API_ENDPOINT'],
                'country': 'tw',
                'language': 'zh-tw',
                'concurrent_requests': 3,  # 降低並發數以符合 API 限制
                'rate_limit': 0.5  # 每2秒一個請求
            },
            'performance': {
                'timeout': 30,
                'retry_attempts': 2,
                'retry_delay': 2
            }
        }
        
        # 初始化 SERP 處理器
        serp_handler = SERPHandler(config, logger)
        
        # 測試 API 連接
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 驗證 API 連接
            api_working = loop.run_until_complete(serp_handler.test_api_connection())
            if not api_working:
                raise ValueError("SERP API 連接失敗")
            
            # 準備關鍵字列表
            keywords_list = list(keywords_to_verify.values_list('keyword', flat=True))
            
            # 更新進度
            task.current_operation = f'正在驗證 {len(keywords_list)} 個關鍵字的 AIO 觸發狀態...'
            task.progress_percentage = 20.0
            task.save()
            
            # 執行批次 AIO 驗證
            validation_results = loop.run_until_complete(
                serp_handler.batch_validate_aio(keywords_list)
            )
            
        finally:
            loop.close()
        
        # 更新進度
        task.current_operation = '正在保存驗證結果...'
        task.progress_percentage = 80.0
        task.save()
        
        # 處理驗證結果
        aio_count = 0
        verified_count = 0
        
        for keyword_data in keywords_to_verify:
            keyword = keyword_data.keyword
            has_aio = validation_results.get(keyword, False)
            
            # 更新關鍵字數據
            keyword_data.aio_verified = True
            keyword_data.aio_triggers = has_aio
            keyword_data.aio_verified_at = timezone.now()
            keyword_data.save()
            
            verified_count += 1
            if has_aio:
                aio_count += 1
        
        # 更新任務結果
        task.status = 'completed'
        task.result_data = {
            'total_verified': verified_count,
            'aio_triggers': aio_count,
            'aio_percentage': (aio_count / verified_count * 100) if verified_count > 0 else 0,
            'api_calls_made': len(keywords_list)
        }
        task.result_count = verified_count
        task.progress_percentage = 100.0
        task.completed_at = timezone.now()
        task.save()
        
        # 更新項目統計
        project.completed_steps += 1
        project.aio_keywords = KeywordData.objects.filter(
            project=project,
            aio_triggers=True
        ).count()
        project.save()
        
        logger.info(f"AIO 驗證完成 - 項目: {project.name}, AIO 關鍵字: {aio_count}/{verified_count}")
        
        return {
            'status': 'completed',
            'verified_count': verified_count,
            'aio_count': aio_count,
            'aio_percentage': (aio_count / verified_count * 100) if verified_count > 0 else 0
        }
        
    except Exception as exc:
        logger.error(f"AIO 驗證任務失敗: {exc}", exc_info=True)
        
        # 更新任務錯誤狀態
        task.status = 'failed'
        task.error_message = str(exc)
        task.completed_at = timezone.now()
        task.save()
        
        # 重試邏輯（較少重試次數，因為 SERP API 調用成本較高）
        if self.request.retries < self.max_retries:
            logger.info(f"重試 AIO 驗證任務 (嘗試 {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc, countdown=120 * (self.request.retries + 1))
        
        raise exc


@shared_task(bind=True)
def run_complete_analysis(self, project_id):
    """
    執行完整的分析流程 (M1 -> M2 -> M3 -> M4)
    
    Args:
        project_id: 分析項目 ID
    
    Returns:
        dict: 完整分析結果
    """
    try:
        project = AnalysisProject.objects.get(id=project_id)
        project.status = 'running'
        project.started_at = timezone.now()
        project.save()
        
        logger.info(f"開始完整分析流程 - 項目: {project.name}")
        
        # 建立各個模組任務
        tasks = []
        
        # M1: GSC 數據擷取
        gsc_task = AnalysisTask.objects.create(
            project=project,
            task_type='gsc_extraction'
        )
        tasks.append(gsc_task)
        
        # M2: 關鍵字擴展
        expansion_task = AnalysisTask.objects.create(
            project=project,
            task_type='keyword_expansion'
        )
        tasks.append(expansion_task)
        
        # M3: AIO 驗證
        validation_task = AnalysisTask.objects.create(
            project=project,
            task_type='aio_validation'
        )
        tasks.append(validation_task)
        
        # M4: 報告生成
        report_task = AnalysisTask.objects.create(
            project=project,
            task_type='report_generation'
        )
        tasks.append(report_task)
        
        # 順序執行任務
        results = {}
        
        # M1: GSC 數據擷取
        gsc_result = extract_gsc_data.delay(str(project.id), str(gsc_task.id))
        gsc_result.get()  # 等待完成
        results['gsc'] = gsc_result.result
        
        # M2: 關鍵字擴展
        expansion_result = expand_keywords.delay(str(project.id), str(expansion_task.id))
        expansion_result.get()  # 等待完成
        results['expansion'] = expansion_result.result
        
        # M3: AIO 驗證
        validation_result = validate_aio_triggers.delay(str(project.id), str(validation_task.id))
        validation_result.get()  # 等待完成
        results['validation'] = validation_result.result
        
        # M4: 報告生成
        from ..reports.tasks import generate_comprehensive_report
        report_result = generate_comprehensive_report.delay(str(project.id), str(report_task.id))
        report_result.get()  # 等待完成
        results['report'] = report_result.result
        
        # 更新項目狀態
        project.status = 'completed'
        project.completed_at = timezone.now()
        project.completion_percentage = 100.0
        project.save()
        
        logger.info(f"完整分析流程完成 - 項目: {project.name}")
        
        return {
            'status': 'completed',
            'project_id': str(project.id),
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"完整分析流程失敗: {exc}", exc_info=True)
        
        # 更新項目錯誤狀態
        project.status = 'failed'
        project.error_message = str(exc)
        project.save()
        
        raise exc
