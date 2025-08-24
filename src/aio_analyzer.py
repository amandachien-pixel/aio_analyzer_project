#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 潛力分析器 - 核心功能
========================

此工具用於分析關鍵字觸發 Google AI Overview (AIO) 的潛力，
透過整合 Google Search Console、Google Ads API 和 SERP API
來提供全面的 AIO 分析報告。

Author: AIO Analytics Team
Version: 1.0.0
"""

import os
import sys
import asyncio
import aiohttp
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config.settings import Config
from utils.gsc_handler import GSCHandler
from utils.ads_handler import AdsHandler
from utils.serp_handler import SERPHandler
from utils.report_generator import ReportGenerator
from utils.logger import setup_logger


class AIOAnalyzer:
    """AIO 潛力分析器主類別"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 AIO 分析器
        
        Args:
            config_path: 配置文件路徑，默認使用 config/settings.py
        """
        self.config = Config(config_path)
        self.logger = setup_logger(self.config.get('logging', {}))
        
        # 初始化各個處理器
        self.gsc_handler = GSCHandler(self.config, self.logger)
        self.ads_handler = AdsHandler(self.config, self.logger)
        self.serp_handler = SERPHandler(self.config, self.logger)
        self.report_generator = ReportGenerator(self.config, self.logger)
        
        self.logger.info("AIO 分析器初始化完成")
    
    def validate_configuration(self) -> bool:
        """
        驗證所有必要的配置是否正確設置
        
        Returns:
            bool: 配置是否有效
        """
        self.logger.info("開始驗證配置...")
        
        required_configs = [
            ('gsc.credentials_file', self.config.get('gsc', {}).get('credentials_file')),
            ('ads.yaml_file', self.config.get('ads', {}).get('yaml_file')),
            ('serp.api_key', self.config.get('serp', {}).get('api_key')),
            ('analysis.site_url', self.config.get('analysis', {}).get('site_url')),
            ('analysis.customer_id', self.config.get('analysis', {}).get('customer_id'))
        ]
        
        for config_name, config_value in required_configs:
            if not config_value or config_value == "YOUR_API_KEY":
                self.logger.error(f"配置項目 {config_name} 未正確設置")
                return False
                
        # 檢查文件是否存在
        file_configs = [
            ('GSC credentials', self.config.get('gsc', {}).get('credentials_file')),
            ('Google Ads YAML', self.config.get('ads', {}).get('yaml_file'))
        ]
        
        for file_name, file_path in file_configs:
            if file_path and not os.path.exists(file_path):
                self.logger.error(f"{file_name} 文件不存在: {file_path}")
                return False
        
        self.logger.info("配置驗證通過")
        return True
    
    async def extract_seed_keywords(self, 
                                   start_date: datetime, 
                                   end_date: datetime, 
                                   regex_pattern: str) -> pd.DataFrame:
        """
        從 Google Search Console 提取種子關鍵字
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            regex_pattern: 篩選關鍵字的正則表達式
            
        Returns:
            包含種子關鍵字的 DataFrame
        """
        self.logger.info("開始從 GSC 提取種子關鍵字...")
        
        try:
            gsc_data = await self.gsc_handler.get_search_analytics_data(
                site_url=self.config.get('analysis', {}).get('site_url'),
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                regex_pattern=regex_pattern
            )
            
            if gsc_data.empty:
                self.logger.warning("未從 GSC 獲取到任何數據")
                return pd.DataFrame()
            
            self.logger.info(f"成功提取 {len(gsc_data)} 個種子關鍵字")
            return gsc_data
            
        except Exception as e:
            self.logger.error(f"提取種子關鍵字時發生錯誤: {e}")
            return pd.DataFrame()
    
    async def expand_keywords(self, seed_keywords: List[str]) -> pd.DataFrame:
        """
        使用 Google Ads API 擴展關鍵字
        
        Args:
            seed_keywords: 種子關鍵字列表
            
        Returns:
            擴展後的關鍵字 DataFrame
        """
        self.logger.info("開始進行關鍵字擴展...")
        
        if not seed_keywords:
            self.logger.warning("沒有種子關鍵字可供擴展")
            return pd.DataFrame()
        
        try:
            expanded_data = await self.ads_handler.generate_keyword_ideas(
                seed_keywords=seed_keywords,
                customer_id=self.config.get('analysis', {}).get('customer_id')
            )
            
            if expanded_data.empty:
                self.logger.warning("關鍵字擴展未產生任何結果")
                return pd.DataFrame()
            
            self.logger.info(f"成功擴展出 {len(expanded_data)} 個關鍵字")
            return expanded_data
            
        except Exception as e:
            self.logger.error(f"關鍵字擴展時發生錯誤: {e}")
            return pd.DataFrame()
    
    async def validate_aio_triggers(self, keywords_df: pd.DataFrame) -> pd.DataFrame:
        """
        驗證關鍵字是否觸發 AIO
        
        Args:
            keywords_df: 包含關鍵字的 DataFrame
            
        Returns:
            包含 AIO 觸發驗證結果的 DataFrame
        """
        self.logger.info("開始進行 AIO 觸發驗證...")
        
        if keywords_df.empty:
            self.logger.warning("沒有關鍵字可供驗證")
            return keywords_df
        
        try:
            validated_data = await self.serp_handler.batch_validate_aio(
                keywords=keywords_df['keyword_idea'].tolist()
            )
            
            # 將驗證結果合併到原始 DataFrame
            keywords_df['triggers_aio'] = keywords_df['keyword_idea'].map(validated_data)
            
            aio_count = keywords_df['triggers_aio'].sum()
            total_count = len(keywords_df)
            
            self.logger.info(f"AIO 驗證完成: {aio_count}/{total_count} 個關鍵字觸發 AIO")
            return keywords_df
            
        except Exception as e:
            self.logger.error(f"AIO 驗證時發生錯誤: {e}")
            return keywords_df
    
    async def generate_comprehensive_report(self, 
                                          final_df: pd.DataFrame, 
                                          gsc_df: pd.DataFrame) -> str:
        """
        生成綜合分析報告
        
        Args:
            final_df: 最終分析結果 DataFrame
            gsc_df: 原始 GSC 數據 DataFrame
            
        Returns:
            報告文件路徑
        """
        self.logger.info("開始生成綜合報告...")
        
        try:
            report_path = await self.report_generator.generate_detailed_report(
                analysis_data=final_df,
                gsc_data=gsc_df,
                output_dir=self.config.get('output', {}).get('directory', 'output')
            )
            
            self.logger.info(f"報告已生成: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"生成報告時發生錯誤: {e}")
            return ""
    
    async def run_full_analysis(self, 
                               days_back: int = 90,
                               regex_pattern: str = r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b') -> Dict[str, any]:
        """
        執行完整的 AIO 潛力分析流程
        
        Args:
            days_back: 向前追溯的天數
            regex_pattern: 篩選關鍵字的正則表達式
            
        Returns:
            分析結果摘要
        """
        if not self.validate_configuration():
            raise ValueError("配置驗證失敗，請檢查配置文件")
        
        self.logger.info("=== 開始執行完整 AIO 潛力分析 ===")
        
        # 設定分析時間範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        self.logger.info(f"分析時間範圍: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        # 第一步：提取種子關鍵字
        gsc_data = await self.extract_seed_keywords(start_date, end_date, regex_pattern)
        if gsc_data.empty:
            return {"status": "failed", "message": "無法獲取種子關鍵字"}
        
        # 第二步：擴展關鍵字
        seed_keywords = gsc_data['query'].tolist()
        expanded_data = await self.expand_keywords(seed_keywords)
        if expanded_data.empty:
            return {"status": "failed", "message": "關鍵字擴展失敗"}
        
        # 第三步：驗證 AIO 觸發
        validated_data = await self.validate_aio_triggers(expanded_data)
        
        # 第四步：生成報告
        report_path = await self.generate_comprehensive_report(validated_data, gsc_data)
        
        # 計算分析結果摘要
        total_keywords = len(validated_data)
        aio_keywords = validated_data['triggers_aio'].sum() if 'triggers_aio' in validated_data.columns else 0
        aio_percentage = (aio_keywords / total_keywords * 100) if total_keywords > 0 else 0
        
        summary = {
            "status": "completed",
            "analysis_period": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d')
            },
            "seed_keywords_count": len(gsc_data),
            "expanded_keywords_count": total_keywords,
            "aio_triggers_count": aio_keywords,
            "aio_percentage": round(aio_percentage, 2),
            "report_path": report_path
        }
        
        self.logger.info("=== AIO 潛力分析完成 ===")
        self.logger.info(f"分析摘要: {summary}")
        
        return summary


async def main():
    """主執行函數"""
    try:
        # 初始化分析器
        analyzer = AIOAnalyzer()
        
        # 執行完整分析
        results = await analyzer.run_full_analysis(
            days_back=90,
            regex_pattern=r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b'
        )
        
        # 輸出結果
        print("\n" + "="*60)
        print("AIO 潛力分析結果摘要")
        print("="*60)
        
        if results["status"] == "completed":
            print(f"✅ 分析狀態: 成功完成")
            print(f"📅 分析期間: {results['analysis_period']['start']} 至 {results['analysis_period']['end']}")
            print(f"🌱 種子關鍵字數量: {results['seed_keywords_count']}")
            print(f"🔍 擴展關鍵字數量: {results['expanded_keywords_count']}")
            print(f"🤖 觸發 AIO 關鍵字數量: {results['aio_triggers_count']}")
            print(f"📊 AIO 觸發率: {results['aio_percentage']}%")
            print(f"📄 報告位置: {results['report_path']}")
        else:
            print(f"❌ 分析失敗: {results['message']}")
        
        print("="*60)
        
    except Exception as e:
        print(f"執行時發生錯誤: {e}")
        logging.error(f"主程序執行錯誤: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
