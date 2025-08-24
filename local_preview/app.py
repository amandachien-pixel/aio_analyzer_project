#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器本地預覽應用
====================

輕量級 Flask 應用，提供簡明易用的 UI 來預覽 AIO 分析功能。
使用 MCP (Model Context Protocol) 邏輯進行模組化處理。
"""

import os
import sys
import asyncio
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.gsc_handler import GSCHandler
from utils.ads_handler import AdsHandler
from utils.serp_handler import SERPHandler
from utils.report_generator import ReportGenerator
from utils.logger import setup_logger

# Flask 應用設定
app = Flask(__name__)
app.secret_key = 'aio-analyzer-preview-key'

# 全局變數
analysis_status = {
    'current_step': 'idle',
    'progress': 0,
    'message': '等待開始分析',
    'results': {}
}

# MCP 邏輯類別
class MCPAnalysisHandler:
    """
    使用 MCP (Model Context Protocol) 邏輯的分析處理器
    將複雜的分析流程模組化為清晰的步驟
    """
    
    def __init__(self):
        self.logger = setup_logger({'level': 'INFO'})
        self.current_project = None
        self.analysis_data = {}
    
    async def execute_analysis_pipeline(self, params):
        """執行完整的分析管道"""
        global analysis_status
        
        try:
            # 步驟 1: 初始化
            analysis_status.update({
                'current_step': 'initializing',
                'progress': 10,
                'message': '正在初始化分析環境...'
            })
            
            # 準備配置
            config = self._prepare_config(params)
            
            # 步驟 2: GSC 數據擷取 (M1)
            analysis_status.update({
                'current_step': 'gsc_extraction',
                'progress': 25,
                'message': '正在從 Google Search Console 擷取種子關鍵字...'
            })
            
            gsc_data = await self._execute_gsc_extraction(config, params)
            
            # 步驟 3: 關鍵字擴展 (M2)
            analysis_status.update({
                'current_step': 'keyword_expansion',
                'progress': 50,
                'message': '正在使用 Google Ads API 擴展關鍵字...'
            })
            
            expanded_data = await self._execute_keyword_expansion(config, gsc_data, params)
            
            # 步驟 4: AIO 驗證 (M3)
            analysis_status.update({
                'current_step': 'aio_validation',
                'progress': 75,
                'message': '正在驗證關鍵字是否觸發 AI Overview...'
            })
            
            validated_data = await self._execute_aio_validation(config, expanded_data)
            
            # 步驟 5: 報告生成 (M4)
            analysis_status.update({
                'current_step': 'report_generation',
                'progress': 90,
                'message': '正在生成分析報告...'
            })
            
            report_path = await self._execute_report_generation(validated_data, gsc_data)
            
            # 完成
            analysis_status.update({
                'current_step': 'completed',
                'progress': 100,
                'message': '分析完成！',
                'results': {
                    'total_keywords': len(validated_data),
                    'aio_keywords': validated_data['triggers_aio'].sum() if 'triggers_aio' in validated_data.columns else 0,
                    'report_path': report_path,
                    'completion_time': datetime.now().isoformat()
                }
            })
            
            return analysis_status['results']
            
        except Exception as e:
            analysis_status.update({
                'current_step': 'error',
                'progress': 0,
                'message': f'分析失敗: {str(e)}',
                'error': str(e)
            })
            self.logger.error(f"分析管道執行失敗: {e}")
            raise
    
    def _prepare_config(self, params):
        """準備分析配置"""
        return {
            'gsc': {
                'credentials_file': str(Path(__file__).parent.parent / 'config' / 'credentials.json'),
                'token_file': str(Path(__file__).parent.parent / 'config' / 'token.json'),
                'scopes': ['https://www.googleapis.com/auth/webmasters.readonly']
            },
            'ads': {
                'yaml_file': str(Path(__file__).parent.parent / 'config' / 'google-ads.yaml'),
                'language_code': 'gid/1001',
                'geo_target_code': 'gid/1013274',
                'keyword_limit': 20
            },
            'serp': {
                'provider': os.getenv('SERP_API_PROVIDER', 'serper'),
                'api_key': os.getenv('SERP_API_KEY', 'demo-key'),
                'endpoint': os.getenv('SERP_API_ENDPOINT', 'https://google.serper.dev/search'),
                'country': 'tw',
                'language': 'zh-tw',
                'concurrent_requests': 3,
                'rate_limit': 1.0
            },
            'performance': {
                'timeout': 30,
                'retry_attempts': 2,
                'retry_delay': 1
            }
        }
    
    async def _execute_gsc_extraction(self, config, params):
        """執行 GSC 數據擷取"""
        # 模擬數據（實際應用中會連接真實 GSC API）
        if not os.path.exists(config['gsc']['credentials_file']):
            # 生成模擬數據
            demo_data = {
                'query': [
                    'what is ai overview',
                    'how to optimize for ai overview',
                    'ai overview seo strategy',
                    '什麼是 AI Overview',
                    '如何優化 AI Overview'
                ],
                'clicks': [120, 85, 67, 45, 32],
                'impressions': [1500, 920, 780, 560, 410],
                'ctr': [0.08, 0.092, 0.086, 0.08, 0.078],
                'position': [3.2, 4.1, 5.2, 6.8, 7.5]
            }
            return pd.DataFrame(demo_data)
        else:
            # 使用真實 GSC API
            gsc_handler = GSCHandler(config, self.logger)
            return await gsc_handler.get_search_analytics_data(
                site_url=params.get('site_url', 'sc-domain:example.com'),
                start_date=params.get('start_date'),
                end_date=params.get('end_date'),
                regex_pattern=params.get('regex_pattern', r'^(what|how|why)\b')
            )
    
    async def _execute_keyword_expansion(self, config, gsc_data, params):
        """執行關鍵字擴展"""
        if gsc_data.empty:
            return pd.DataFrame()
        
        # 模擬擴展數據
        seed_keywords = gsc_data['query'].tolist()
        expanded_keywords = []
        
        for keyword in seed_keywords:
            # 為每個種子關鍵字生成相關建議
            variants = [
                f"{keyword} guide",
                f"{keyword} tutorial", 
                f"{keyword} tips",
                f"best {keyword}",
                f"{keyword} 2024"
            ]
            
            for variant in variants:
                expanded_keywords.append({
                    'keyword_idea': variant,
                    'search_volume': np.random.randint(100, 5000),
                    'competition_level': np.random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    'competition_index': np.random.randint(10, 90)
                })
        
        return pd.DataFrame(expanded_keywords)
    
    async def _execute_aio_validation(self, config, expanded_data):
        """執行 AIO 驗證"""
        if expanded_data.empty:
            return expanded_data
        
        # 檢查 SERP API 配置
        if config['serp']['api_key'] == 'demo-key':
            # 模擬 AIO 驗證結果
            expanded_data['triggers_aio'] = np.random.choice([True, False], 
                                                           size=len(expanded_data), 
                                                           p=[0.3, 0.7])  # 30% 觸發率
        else:
            # 使用真實 SERP API
            serp_handler = SERPHandler(config, self.logger)
            keywords = expanded_data['keyword_idea'].tolist()
            validation_results = await serp_handler.batch_validate_aio(keywords[:10])  # 限制數量
            expanded_data['triggers_aio'] = expanded_data['keyword_idea'].map(validation_results)
        
        return expanded_data
    
    async def _execute_report_generation(self, validated_data, gsc_data):
        """執行報告生成"""
        output_dir = Path(__file__).parent / 'reports'
        output_dir.mkdir(exist_ok=True)
        
        # 生成報告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = output_dir / f'aio_analysis_{timestamp}.csv'
        
        # 準備報告數據
        if not validated_data.empty:
            report_data = validated_data.copy()
            report_data['觸發AIO'] = report_data['triggers_aio'].apply(lambda x: 'Y' if x else 'N')
            report_data.to_csv(report_path, index=False, encoding='utf-8-sig')
        
        return str(report_path)


# MCP 處理器實例
mcp_handler = MCPAnalysisHandler()


@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')


@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """開始分析"""
    try:
        params = request.json
        
        # 在背景執行分析
        def run_analysis():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(mcp_handler.execute_analysis_pipeline(params))
            finally:
                loop.close()
        
        # 重置狀態
        global analysis_status
        analysis_status = {
            'current_step': 'starting',
            'progress': 0,
            'message': '正在啟動分析...',
            'results': {}
        }
        
        # 在新執行緒中執行分析
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'message': '分析已開始'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analysis_status')
def get_analysis_status():
    """獲取分析狀態"""
    return jsonify(analysis_status)


@app.route('/api/demo_data')
def get_demo_data():
    """獲取演示數據"""
    demo_results = {
        'gsc_data': {
            'total_queries': 5,
            'total_clicks': 349,
            'total_impressions': 4170,
            'avg_ctr': 0.084
        },
        'expanded_keywords': {
            'total_keywords': 25,
            'avg_search_volume': 1250,
            'competition_distribution': {
                'LOW': 8, 'MEDIUM': 10, 'HIGH': 7
            }
        },
        'aio_validation': {
            'total_validated': 25,
            'aio_triggers': 8,
            'aio_percentage': 32.0
        }
    }
    return jsonify(demo_results)


@app.route('/download_report/<filename>')
def download_report(filename):
    """下載報告"""
    try:
        report_path = Path(__file__).parent / 'reports' / filename
        if report_path.exists():
            return send_file(report_path, as_attachment=True)
        else:
            return jsonify({'error': '報告文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 確保必要的目錄存在
    os.makedirs('reports', exist_ok=True)
    
    print("🚀 AIO 分析器本地預覽啟動中...")
    print("📱 請在瀏覽器中訪問: http://localhost:5001")
    print("💡 這是預覽版本，某些功能使用模擬數據")
    print("🔧 完整功能需要配置 API 憑證")
    
    # 啟動 Flask 應用
    app.run(debug=True, host='0.0.0.0', port=5001)
