#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERP API 處理模組
================

處理與 SERP API 相關的所有操作，
用於驗證關鍵字是否觸發 Google AI Overview (AIO)。
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Tuple, Optional
from asyncio import Semaphore
import time
from dataclasses import dataclass

from .logger import LoggingMixin


@dataclass
class SERPResult:
    """SERP 搜尋結果數據類別"""
    keyword: str
    has_aio: bool
    aio_content: Optional[str] = None
    total_results: int = 0
    error: Optional[str] = None


class SERPHandler(LoggingMixin):
    """SERP API 處理器"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        初始化 SERP 處理器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.config = config
        if logger:
            self._logger = logger
        
        # SERP 配置
        self.serp_config = config.get('serp', {})
        self.api_provider = self.serp_config.get('provider', 'serper')
        self.api_key = self.serp_config.get('api_key')
        self.endpoint = self.serp_config.get('endpoint', 'https://google.serper.dev/search')
        self.country = self.serp_config.get('country', 'tw')
        self.language = self.serp_config.get('language', 'zh-tw')
        self.concurrent_requests = self.serp_config.get('concurrent_requests', 10)
        self.rate_limit = self.serp_config.get('rate_limit', 1.0)  # 每秒請求數
        
        # 效能配置
        self.performance_config = config.get('performance', {})
        self.timeout = self.performance_config.get('timeout', 30)
        self.retry_attempts = self.performance_config.get('retry_attempts', 3)
        self.retry_delay = self.performance_config.get('retry_delay', 1)
        
        # 驗證配置
        self._validate_config()
        
        # 並發控制
        self._semaphore = Semaphore(self.concurrent_requests)
        self._last_request_time = 0
    
    def _validate_config(self):
        """驗證 SERP 配置"""
        if not self.api_key or self.api_key == "YOUR_SERP_API_KEY":
            raise ValueError("SERP API key 未正確設置")
        
        self.logger.info("SERP API 配置驗證通過")
    
    async def _rate_limit_delay(self):
        """實現速率限制"""
        if self.rate_limit > 0:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            min_interval = 1.0 / self.rate_limit
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                await asyncio.sleep(sleep_time)
            
            self._last_request_time = time.time()
    
    async def _make_serp_request(self, 
                                session: aiohttp.ClientSession, 
                                keyword: str) -> SERPResult:
        """
        執行單個 SERP API 請求
        
        Args:
            session: aiohttp 會話
            keyword: 搜尋關鍵字
            
        Returns:
            SERP 搜尋結果
        """
        async with self._semaphore:
            await self._rate_limit_delay()
            
            # 根據 API 提供商設定不同的請求格式
            if self.api_provider == 'serper':
                headers = {
                    'X-API-KEY': self.api_key,
                    'Content-Type': 'application/json'
                }
                payload = {
                    'q': keyword,
                    'gl': self.country,
                    'hl': self.language
                }
                
                for attempt in range(self.retry_attempts):
                    try:
                        async with session.post(
                            self.endpoint,
                            json=payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=self.timeout)
                        ) as response:
                            
                            if response.status == 200:
                                data = await response.json()
                                return self._parse_serp_response(keyword, data)
                            elif response.status == 429:  # Rate limit exceeded
                                retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                                self.logger.warning(f"API 速率限制，等待 {retry_after} 秒後重試")
                                await asyncio.sleep(retry_after)
                            else:
                                self.logger.warning(f"Serper API 請求失敗 - 狀態碼: {response.status}, 關鍵字: {keyword}")
                    
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Serper API 請求超時 - 關鍵字: {keyword}, 嘗試: {attempt + 1}")
                    except Exception as e:
                        self.logger.warning(f"Serper API 請求錯誤 - 關鍵字: {keyword}, 錯誤: {e}")
                    
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # 指數退避
            
            else:  # SerpApi 或其他提供商
                params = {
                    'api_key': self.api_key,
                    'q': keyword,
                    'gl': self.country,
                    'hl': self.language,
                    'engine': 'google'
                }
                
                for attempt in range(self.retry_attempts):
                    try:
                        async with session.get(
                            self.endpoint, 
                            params=params, 
                            timeout=aiohttp.ClientTimeout(total=self.timeout)
                        ) as response:
                            
                            if response.status == 200:
                                data = await response.json()
                                return self._parse_serp_response(keyword, data)
                            elif response.status == 429:  # Rate limit exceeded
                                retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                                self.logger.warning(f"API 速率限制，等待 {retry_after} 秒後重試")
                                await asyncio.sleep(retry_after)
                            else:
                                self.logger.warning(f"SERP API 請求失敗 - 狀態碼: {response.status}, 關鍵字: {keyword}")
                    
                    except asyncio.TimeoutError:
                        self.logger.warning(f"SERP API 請求超時 - 關鍵字: {keyword}, 嘗試: {attempt + 1}")
                    except Exception as e:
                        self.logger.warning(f"SERP API 請求錯誤 - 關鍵字: {keyword}, 錯誤: {e}")
                    
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # 指數退避
            
            return SERPResult(
                keyword=keyword,
                has_aio=False,
                error=f"請求失敗，已重試 {self.retry_attempts} 次"
            )
    
    def _parse_serp_response(self, keyword: str, data: Dict) -> SERPResult:
        """
        解析 SERP API 回應
        
        Args:
            keyword: 搜尋關鍵字
            data: API 回應數據
            
        Returns:
            解析後的搜尋結果
        """
        try:
            # 檢查是否存在 AI Overview
            has_aio = False
            aio_content = None
            total_results = 0
            
            if self.api_provider == 'serper':
                # Serper API 格式檢測
                # 檢查 AI Overview
                if 'aiOverview' in data:
                    has_aio = True
                    aio_content = data['aiOverview'].get('snippet', '')
                elif 'answerBox' in data:
                    answer_box = data['answerBox']
                    # 檢查是否為 AI 生成的內容
                    if ('snippet' in answer_box and 
                        ('ai' in answer_box.get('title', '').lower() or 
                         'generated' in answer_box.get('snippet', '').lower())):
                        has_aio = True
                        aio_content = answer_box.get('snippet', '')
                
                # 檢查 Knowledge Graph 中的 AI 內容
                if not has_aio and 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    if 'aiGenerated' in kg or 'type' in kg and 'ai' in kg['type'].lower():
                        has_aio = True
                        aio_content = kg.get('description', '')
                
                # 檢查有機搜尋結果
                if not has_aio and 'organic' in data:
                    for result in data['organic'][:3]:  # 檢查前3個結果
                        if ('aiGenerated' in result or 
                            'generatedByAI' in result or
                            'ai generated' in result.get('snippet', '').lower()):
                            has_aio = True
                            break
                
                # 獲取總結果數
                total_results = data.get('searchInformation', {}).get('totalResults', 0)
                if isinstance(total_results, str):
                    total_results = int(total_results.replace(',', '')) if total_results.replace(',', '').isdigit() else 0
            
            else:
                # SerpApi 或其他提供商的格式檢測
                if 'ai_overview' in data:
                    # SerpApi 格式
                    has_aio = True
                    aio_content = data['ai_overview'].get('snippet', '')
                elif 'knowledge_graph' in data and data['knowledge_graph'].get('type') == 'ai_overview':
                    # 其他格式
                    has_aio = True
                    aio_content = data['knowledge_graph'].get('description', '')
                elif 'answer_box' in data and 'ai' in data['answer_box'].get('type', '').lower():
                    # Answer box 中的 AI 內容
                    has_aio = True
                    aio_content = data['answer_box'].get('answer', '')
                
                # 檢查有機搜尋結果中是否包含 AI 相關標記
                if not has_aio and 'organic_results' in data:
                    for result in data['organic_results'][:3]:  # 檢查前3個結果
                        if 'ai_generated' in result or 'generated_by_ai' in result:
                            has_aio = True
                            break
                
                total_results = data.get('search_information', {}).get('total_results', 0)
            
            return SERPResult(
                keyword=keyword,
                has_aio=has_aio,
                aio_content=aio_content[:500] if aio_content else None,  # 限制內容長度
                total_results=total_results
            )
            
        except Exception as e:
            self.logger.error(f"解析 SERP 回應時發生錯誤 - 關鍵字: {keyword}, 錯誤: {e}")
            return SERPResult(
                keyword=keyword,
                has_aio=False,
                error=f"解析錯誤: {str(e)}"
            )
    
    async def batch_validate_aio(self, keywords: List[str]) -> Dict[str, bool]:
        """
        批次驗證關鍵字是否觸發 AIO
        
        Args:
            keywords: 關鍵字列表
            
        Returns:
            關鍵字到 AIO 觸發狀態的映射字典
        """
        if not keywords:
            self.logger.warning("沒有關鍵字可供驗證")
            return {}
        
        self.logger.info(f"開始批次 AIO 驗證 - 關鍵字數量: {len(keywords)}")
        
        results = {}
        processed_count = 0
        aio_count = 0
        
        # 創建進度追蹤
        async def process_keyword(session, keyword):
            nonlocal processed_count, aio_count
            
            result = await self._make_serp_request(session, keyword)
            
            processed_count += 1
            if result.has_aio:
                aio_count += 1
            
            # 每處理10個關鍵字記錄一次進度
            if processed_count % 10 == 0:
                progress_pct = (processed_count / len(keywords)) * 100
                self.logger.info(f"AIO 驗證進度: {processed_count}/{len(keywords)} "
                               f"({progress_pct:.1f}%) - 觸發 AIO: {aio_count}")
            
            return keyword, result.has_aio
        
        try:
            # 設定 aiohttp 連接器以優化性能
            connector = aiohttp.TCPConnector(
                limit=self.concurrent_requests * 2,
                limit_per_host=self.concurrent_requests,
                keepalive_timeout=60
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # 創建所有任務
                tasks = [process_keyword(session, keyword) for keyword in keywords]
                
                # 使用 asyncio.gather 並發執行所有任務
                completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 處理結果
                for task_result in completed_tasks:
                    if isinstance(task_result, Exception):
                        self.logger.error(f"任務執行錯誤: {task_result}")
                    else:
                        keyword, has_aio = task_result
                        results[keyword] = has_aio
            
            # 最終統計
            total_processed = len(results)
            total_aio = sum(results.values())
            aio_percentage = (total_aio / total_processed * 100) if total_processed > 0 else 0
            
            self.logger.info(f"AIO 驗證完成 - 處理: {total_processed}, "
                           f"觸發 AIO: {total_aio} ({aio_percentage:.1f}%)")
            
            return results
            
        except Exception as e:
            self.logger.error(f"批次 AIO 驗證時發生錯誤: {e}")
            return results
    
    async def validate_single_keyword(self, keyword: str) -> SERPResult:
        """
        驗證單個關鍵字是否觸發 AIO
        
        Args:
            keyword: 關鍵字
            
        Returns:
            SERP 搜尋結果
        """
        self.logger.debug(f"驗證單個關鍵字: {keyword}")
        
        try:
            async with aiohttp.ClientSession() as session:
                result = await self._make_serp_request(session, keyword)
                
                if result.has_aio:
                    self.logger.info(f"關鍵字 '{keyword}' 觸發 AIO")
                else:
                    self.logger.debug(f"關鍵字 '{keyword}' 未觸發 AIO")
                
                return result
                
        except Exception as e:
            self.logger.error(f"驗證關鍵字 '{keyword}' 時發生錯誤: {e}")
            return SERPResult(
                keyword=keyword,
                has_aio=False,
                error=str(e)
            )
    
    async def test_api_connection(self) -> bool:
        """
        測試 SERP API 連接
        
        Returns:
            API 連接是否正常
        """
        test_keyword = "test"
        
        try:
            result = await self.validate_single_keyword(test_keyword)
            
            if result.error:
                self.logger.error(f"SERP API 連接測試失敗: {result.error}")
                return False
            else:
                self.logger.info("SERP API 連接測試成功")
                return True
                
        except Exception as e:
            self.logger.error(f"SERP API 連接測試異常: {e}")
            return False
