#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Search Console API 處理模組
=================================

處理與 Google Search Console API 相關的所有操作，
包括身份驗證、數據擷取和格式化。
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError

from .logger import LoggingMixin


class GSCHandler(LoggingMixin):
    """Google Search Console API 處理器"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        初始化 GSC 處理器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.config = config
        if logger:
            self._logger = logger
        
        # GSC 配置
        self.gsc_config = config.get('gsc', {})
        self.credentials_file = self.gsc_config.get('credentials_file')
        self.token_file = self.gsc_config.get('token_file')
        self.scopes = self.gsc_config.get('scopes', ['https://www.googleapis.com/auth/webmasters.readonly'])
        
        # 驗證配置
        self._validate_config()
        
        # GSC 服務
        self._service = None
    
    def _validate_config(self):
        """驗證 GSC 配置"""
        if not self.credentials_file:
            raise ValueError("GSC credentials_file 未設置")
        
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"GSC 憑證文件不存在: {self.credentials_file}")
        
        self.logger.info("GSC 配置驗證通過")
    
    def _get_credentials(self) -> Credentials:
        """
        處理 GSC API 的 OAuth 2.0 授權流程
        
        Returns:
            Google OAuth 2.0 憑證
        """
        creds = None
        
        # 嘗試從現有 token 文件載入憑證
        if self.token_file and os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
                self.logger.debug("從現有 token 文件載入憑證")
            except Exception as e:
                self.logger.warning(f"載入現有憑證失敗: {e}")
        
        # 檢查憑證是否有效
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("憑證已成功重新整理")
                except RefreshError as e:
                    self.logger.error(f"憑證重新整理失敗: {e}")
                    creds = None
            
            # 如果憑證無效，執行新的授權流程
            if not creds:
                self.logger.info("執行新的 OAuth 2.0 授權流程")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
                self.logger.info("OAuth 2.0 授權完成")
        
        # 儲存憑證以供下次使用
        if self.token_file:
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                self.logger.debug(f"憑證已儲存至: {self.token_file}")
            except Exception as e:
                self.logger.warning(f"儲存憑證失敗: {e}")
        
        return creds
    
    def _get_service(self):
        """獲取 GSC API 服務實例"""
        if not self._service:
            creds = self._get_credentials()
            self._service = build('webmasters', 'v3', credentials=creds)
            self.logger.info("GSC API 服務已初始化")
        return self._service
    
    async def get_search_analytics_data(self,
                                      site_url: str,
                                      start_date: str,
                                      end_date: str,
                                      regex_pattern: str = None,
                                      dimensions: List[str] = None,
                                      row_limit: int = 5000) -> pd.DataFrame:
        """
        從 GSC 獲取搜尋分析數據
        
        Args:
            site_url: 網站 URL (例如 'sc-domain:example.com')
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            regex_pattern: 篩選查詢的正則表達式
            dimensions: 數據維度列表
            row_limit: 返回行數限制
            
        Returns:
            包含搜尋分析數據的 DataFrame
        """
        self.logger.info(f"開始從 GSC 擷取數據: {site_url} ({start_date} 至 {end_date})")
        
        if dimensions is None:
            dimensions = ['query']
        
        try:
            service = self._get_service()
            
            # 建構請求
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit
            }
            
            # 添加篩選條件
            if regex_pattern:
                request_body['dimensionFilterGroups'] = [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'includingRegex',
                        'expression': regex_pattern
                    }]
                }]
                self.logger.debug(f"使用正則表達式篩選: {regex_pattern}")
            
            # 在異步環境中執行同步 API 調用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: service.searchanalytics().query(
                    siteUrl=site_url, 
                    body=request_body
                ).execute()
            )
            
            # 處理回應
            if 'rows' not in response:
                self.logger.warning("GSC API 回應中沒有數據行")
                return pd.DataFrame()
            
            # 轉換為 DataFrame
            data = []
            for row in response['rows']:
                row_data = {}
                
                # 處理維度數據
                for i, dimension in enumerate(dimensions):
                    row_data[dimension] = row['keys'][i] if i < len(row['keys']) else None
                
                # 處理指標數據
                row_data.update({
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0.0),
                    'position': row.get('position', 0.0)
                })
                
                data.append(row_data)
            
            df = pd.DataFrame(data)
            
            self.logger.info(f"成功擷取 {len(df)} 筆 GSC 數據")
            
            # 數據品質檢查
            if not df.empty:
                self._validate_data_quality(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"GSC 數據擷取失敗: {e}")
            return pd.DataFrame()
    
    def _validate_data_quality(self, df: pd.DataFrame):
        """驗證數據品質並記錄統計信息"""
        if df.empty:
            return
        
        # 基本統計
        total_rows = len(df)
        total_clicks = df['clicks'].sum() if 'clicks' in df.columns else 0
        total_impressions = df['impressions'].sum() if 'impressions' in df.columns else 0
        avg_ctr = df['ctr'].mean() if 'ctr' in df.columns else 0
        avg_position = df['position'].mean() if 'position' in df.columns else 0
        
        self.logger.info(f"數據統計 - 總行數: {total_rows}, 總點擊: {total_clicks}, "
                        f"總曝光: {total_impressions}, 平均 CTR: {avg_ctr:.3f}, "
                        f"平均排名: {avg_position:.1f}")
        
        # 檢查異常值
        if 'ctr' in df.columns:
            high_ctr = df[df['ctr'] > 0.5]
            if not high_ctr.empty:
                self.logger.warning(f"發現 {len(high_ctr)} 筆 CTR > 50% 的異常數據")
        
        if 'position' in df.columns:
            low_position = df[df['position'] > 100]
            if not low_position.empty:
                self.logger.info(f"發現 {len(low_position)} 筆排名 > 100 的數據")
    
    async def get_site_list(self) -> List[str]:
        """
        獲取帳戶中的所有網站列表
        
        Returns:
            網站 URL 列表
        """
        try:
            service = self._get_service()
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: service.sites().list().execute()
            )
            
            sites = [site['siteUrl'] for site in response.get('siteEntry', [])]
            self.logger.info(f"獲取到 {len(sites)} 個網站")
            
            return sites
            
        except Exception as e:
            self.logger.error(f"獲取網站列表失敗: {e}")
            return []
    
    def close(self):
        """清理資源"""
        self._service = None
        self.logger.debug("GSC 處理器已關閉")
