#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Ads API 處理模組
======================

處理與 Google Ads API 相關的所有操作，
包括關鍵字擴展、搜尋量數據和競爭程度分析。
"""

import os
import pandas as pd
import asyncio
from typing import Dict, Any, List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from .logger import LoggingMixin


class AdsHandler(LoggingMixin):
    """Google Ads API 處理器"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        初始化 Ads 處理器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.config = config
        if logger:
            self._logger = logger
        
        # Ads 配置
        self.ads_config = config.get('ads', {})
        self.yaml_file = self.ads_config.get('yaml_file')
        self.language_code = self.ads_config.get('language_code', 'gid/1001')  # 繁體中文
        self.geo_target_code = self.ads_config.get('geo_target_code', 'gid/1013274')  # 台灣
        self.keyword_limit = self.ads_config.get('keyword_limit', 20)
        
        # 驗證配置
        self._validate_config()
        
        # Google Ads 客戶端
        self._client = None
    
    def _validate_config(self):
        """驗證 Ads 配置"""
        if not self.yaml_file:
            raise ValueError("Google Ads yaml_file 未設置")
        
        if not os.path.exists(self.yaml_file):
            raise FileNotFoundError(f"Google Ads YAML 文件不存在: {self.yaml_file}")
        
        self.logger.info("Google Ads 配置驗證通過")
    
    def _get_client(self) -> GoogleAdsClient:
        """
        獲取 Google Ads API 客戶端
        
        Returns:
            Google Ads 客戶端實例
        """
        if not self._client:
            try:
                self._client = GoogleAdsClient.load_from_storage(self.yaml_file)
                self.logger.info("Google Ads API 客戶端已初始化")
            except Exception as e:
                self.logger.error(f"初始化 Google Ads 客戶端失敗: {e}")
                raise
        
        return self._client
    
    async def generate_keyword_ideas(self,
                                   seed_keywords: List[str],
                                   customer_id: str,
                                   language_code: str = None,
                                   geo_target_code: str = None) -> pd.DataFrame:
        """
        使用種子關鍵字生成關鍵字建議
        
        Args:
            seed_keywords: 種子關鍵字列表
            customer_id: Google Ads 客戶 ID
            language_code: 語言代碼
            geo_target_code: 地理目標代碼
            
        Returns:
            包含關鍵字建議的 DataFrame
        """
        if not seed_keywords:
            self.logger.warning("沒有種子關鍵字可供擴展")
            return pd.DataFrame()
        
        language_code = language_code or self.language_code
        geo_target_code = geo_target_code or self.geo_target_code
        
        self.logger.info(f"開始生成關鍵字建議 - 種子關鍵字數量: {len(seed_keywords)}")
        
        try:
            client = self._get_client()
            keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
            
            # 建構請求
            request = client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id.replace('-', '')  # 移除連字號
            
            # 設定語言和地理位置
            request.language = language_code
            request.geo_target_constants.append(geo_target_code)
            
            # 限制種子關鍵字數量（API 限制）
            limited_seeds = seed_keywords[:self.keyword_limit]
            request.keyword_seed.keywords.extend(limited_seeds)
            
            self.logger.debug(f"使用 {len(limited_seeds)} 個種子關鍵字進行擴展")
            
            # 在異步環境中執行同步 API 調用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: keyword_plan_idea_service.generate_keyword_ideas(request=request)
            )
            
            # 處理回應
            keyword_ideas = []
            for idea in response:
                metrics = idea.keyword_idea_metrics
                
                keyword_data = {
                    'keyword_idea': idea.text,
                    'search_volume': metrics.avg_monthly_searches if metrics else 0,
                    'competition_level': metrics.competition.name if metrics else 'UNKNOWN',
                    'competition_index': getattr(metrics, 'competition_index', 0) if metrics else 0,
                    'low_top_of_page_bid_micros': getattr(metrics, 'low_top_of_page_bid_micros', 0) if metrics else 0,
                    'high_top_of_page_bid_micros': getattr(metrics, 'high_top_of_page_bid_micros', 0) if metrics else 0
                }
                
                keyword_ideas.append(keyword_data)
            
            df = pd.DataFrame(keyword_ideas)
            
            if not df.empty:
                # 轉換出價從微分單位到實際貨幣單位（假設為美元）
                if 'low_top_of_page_bid_micros' in df.columns:
                    df['low_top_of_page_bid_usd'] = df['low_top_of_page_bid_micros'] / 1_000_000
                if 'high_top_of_page_bid_micros' in df.columns:
                    df['high_top_of_page_bid_usd'] = df['high_top_of_page_bid_micros'] / 1_000_000
                
                # 排序：按搜尋量降序
                df = df.sort_values('search_volume', ascending=False).reset_index(drop=True)
                
                self.logger.info(f"成功生成 {len(df)} 個關鍵字建議")
                self._log_keyword_stats(df)
            else:
                self.logger.warning("沒有生成任何關鍵字建議")
            
            return df
            
        except GoogleAdsException as ex:
            self.logger.error(f'Google Ads API 請求失敗: "{ex.error.code().name}"')
            for error in ex.failure.errors:
                self.logger.error(f'  錯誤詳情: "{error.message}"')
            return pd.DataFrame()
        
        except Exception as e:
            self.logger.error(f"生成關鍵字建議時發生錯誤: {e}")
            return pd.DataFrame()
    
    def _log_keyword_stats(self, df: pd.DataFrame):
        """記錄關鍵字統計信息"""
        if df.empty:
            return
        
        total_keywords = len(df)
        avg_search_volume = df['search_volume'].mean()
        max_search_volume = df['search_volume'].max()
        
        # 競爭程度分布
        competition_counts = df['competition_level'].value_counts()
        
        self.logger.info(f"關鍵字統計 - 總數: {total_keywords}, "
                        f"平均搜尋量: {avg_search_volume:.0f}, "
                        f"最高搜尋量: {max_search_volume}")
        
        self.logger.info(f"競爭程度分布: {dict(competition_counts)}")
        
        # 高搜尋量關鍵字
        high_volume = df[df['search_volume'] >= 1000]
        if not high_volume.empty:
            self.logger.info(f"高搜尋量關鍵字（≥1000）: {len(high_volume)} 個")
    
    async def get_keyword_metrics(self,
                                keywords: List[str],
                                customer_id: str,
                                language_code: str = None,
                                geo_target_code: str = None) -> pd.DataFrame:
        """
        獲取指定關鍵字的詳細指標
        
        Args:
            keywords: 關鍵字列表
            customer_id: Google Ads 客戶 ID
            language_code: 語言代碼
            geo_target_code: 地理目標代碼
            
        Returns:
            包含關鍵字指標的 DataFrame
        """
        if not keywords:
            self.logger.warning("沒有關鍵字可查詢指標")
            return pd.DataFrame()
        
        language_code = language_code or self.language_code
        geo_target_code = geo_target_code or self.geo_target_code
        
        self.logger.info(f"開始獲取關鍵字指標 - 關鍵字數量: {len(keywords)}")
        
        try:
            client = self._get_client()
            keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
            
            # 建構請求
            request = client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id.replace('-', '')
            
            # 設定語言和地理位置
            request.language = language_code
            request.geo_target_constants.append(geo_target_code)
            
            # 使用關鍵字作為種子
            request.keyword_seed.keywords.extend(keywords[:self.keyword_limit])
            
            # 在異步環境中執行同步 API 調用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: keyword_plan_idea_service.generate_keyword_ideas(request=request)
            )
            
            # 處理回應
            metrics_data = []
            for idea in response:
                if idea.text in keywords:  # 只返回請求的關鍵字
                    metrics = idea.keyword_idea_metrics
                    
                    metric_data = {
                        'keyword': idea.text,
                        'search_volume': metrics.avg_monthly_searches if metrics else 0,
                        'competition_level': metrics.competition.name if metrics else 'UNKNOWN',
                        'competition_index': getattr(metrics, 'competition_index', 0) if metrics else 0
                    }
                    
                    metrics_data.append(metric_data)
            
            df = pd.DataFrame(metrics_data)
            self.logger.info(f"成功獲取 {len(df)} 個關鍵字的指標")
            
            return df
            
        except Exception as e:
            self.logger.error(f"獲取關鍵字指標時發生錯誤: {e}")
            return pd.DataFrame()
    
    async def validate_customer_access(self, customer_id: str) -> bool:
        """
        驗證對指定客戶帳戶的訪問權限
        
        Args:
            customer_id: Google Ads 客戶 ID
            
        Returns:
            是否有訪問權限
        """
        try:
            client = self._get_client()
            customer_service = client.get_service("CustomerService")
            
            # 清理客戶 ID
            clean_customer_id = customer_id.replace('-', '')
            
            # 在異步環境中執行同步 API 調用
            loop = asyncio.get_event_loop()
            customer = await loop.run_in_executor(
                None,
                lambda: customer_service.get_customer(
                    resource_name=f"customers/{clean_customer_id}"
                )
            )
            
            self.logger.info(f"成功訪問客戶帳戶: {customer.descriptive_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"無法訪問客戶帳戶 {customer_id}: {e}")
            return False
    
    def close(self):
        """清理資源"""
        self._client = None
        self.logger.debug("Google Ads 處理器已關閉")
