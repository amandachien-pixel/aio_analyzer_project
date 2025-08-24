#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serper API 簡單測試
==================

快速測試 Serper API 連接和 AI Overview 檢測功能。
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Serper API 測試器
class SerperTester:
    """Serper API 測試器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://google.serper.dev/search"
        
        # 測試查詢列表
        self.test_queries = [
            "what is artificial intelligence",
            "how to make pizza",
            "python programming tutorial", 
            "what is climate change",
            "how does machine learning work",
            "什麼是人工智慧",
            "如何學習程式設計"
        ]
    
    async def test_basic_connection(self):
        """測試基本連接"""
        print("🔍 測試 Serper API 基本連接...")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': self.api_key,
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'q': 'test query',
                    'type': 'search'
                }
                
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=data,
                    timeout=10
                ) as response:
                    
                    if response.status == 200:
                        print("✅ API 連接成功")
                        return True
                    elif response.status == 401:
                        print("❌ API 金鑰無效")
                        return False
                    elif response.status == 429:
                        print("❌ API 查詢額度已耗盡")
                        return False
                    else:
                        print(f"❌ API 請求失敗，狀態碼: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ 連接測試失敗: {e}")
            return False
    
    async def test_aio_detection(self):
        """測試 AI Overview 檢測"""
        print("\n🤖 測試 AI Overview 檢測...")
        
        aio_results = []
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n[{i}/{len(self.test_queries)}] 測試查詢: '{query}'")
            
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'X-API-KEY': self.api_key,
                        'Content-Type': 'application/json'
                    }
                    
                    data = {
                        'q': query,
                        'type': 'search',
                        'gl': 'tw',  # 台灣地區
                        'hl': 'zh-tw'  # 繁體中文
                    }
                    
                    async with session.post(
                        self.endpoint,
                        headers=headers,
                        json=data,
                        timeout=15
                    ) as response:
                        
                        if response.status == 200:
                            result_data = await response.json()
                            
                            # 檢測 AI Overview
                            has_aio = self._detect_aio(result_data)
                            
                            aio_results.append({
                                'query': query,
                                'has_aio': has_aio,
                                'organic_count': len(result_data.get('organic', [])),
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            status = "🟢 有 AIO" if has_aio else "🟡 無 AIO"
                            organic_count = len(result_data.get('organic', []))
                            print(f"  結果: {status} | 有機結果: {organic_count} 個")
                            
                        else:
                            print(f"  ❌ 請求失敗，狀態碼: {response.status}")
                            
                # 延遲避免超過速率限制
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ❌ 查詢失敗: {e}")
        
        return aio_results
    
    def _detect_aio(self, data: dict) -> bool:
        """檢測是否有 AI Overview"""
        
        # 檢查 Serper 的 aiOverview 欄位
        if 'aiOverview' in data:
            return True
        
        # 檢查 answerBox（可能包含 AI 生成內容）
        if 'answerBox' in data:
            answer_box = data['answerBox']
            snippet = answer_box.get('snippet', '').lower()
            title = answer_box.get('title', '').lower()
            
            # 簡單的 AI 內容檢測
            ai_indicators = ['ai', 'artificial intelligence', 'generated', 'overview']
            if any(indicator in title or indicator in snippet for indicator in ai_indicators):
                return True
        
        # 檢查 knowledgeGraph
        if 'knowledgeGraph' in data:
            kg = data['knowledgeGraph']
            description = kg.get('description', '').lower()
            if 'ai' in description or 'overview' in description:
                return True
        
        return False
    
    def print_summary(self, results: list):
        """印出測試摘要"""
        print("\n" + "="*60)
        print("📊 測試摘要")
        print("="*60)
        
        total_queries = len(results)
        aio_count = sum(1 for r in results if r['has_aio'])
        aio_percentage = (aio_count / total_queries * 100) if total_queries > 0 else 0
        
        print(f"總查詢數: {total_queries}")
        print(f"觸發 AIO: {aio_count}")
        print(f"觸發率: {aio_percentage:.1f}%")
        
        print("\n📋 詳細結果:")
        for result in results:
            status = "✓" if result['has_aio'] else "○"
            print(f"  {status} {result['query']}")
        
        print(f"\n💡 這些結果可以幫助您了解哪些類型的查詢更容易觸發 AI Overview。")
        print(f"⚠️ 結果可能因地區、語言和時間而異。")

async def main():
    """主函數"""
    print("🚀 Serper API 測試工具")
    print("="*40)
    
    # 讀取 API 金鑰
    api_key = os.getenv('SERP_API_KEY')
    
    if not api_key or api_key == 'your-serper-api-key-here':
        print("❌ 請設定 SERP_API_KEY 環境變數")
        print("\n設定方法:")
        print("1. 編輯 .env 檔案")
        print("2. 或執行: export SERP_API_KEY=your-api-key")
        return
    
    print(f"🔑 使用 API 金鑰: {api_key[:10]}...")
    
    # 創建測試器
    tester = SerperTester(api_key)
    
    # 執行測試
    if await tester.test_basic_connection():
        results = await tester.test_aio_detection()
        tester.print_summary(results)
        
        # 儲存結果（可選）
        save_results = input("\n💾 是否儲存測試結果到 JSON 檔案？(y/N): ").lower()
        if save_results == 'y':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"serper_test_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 結果已儲存到: {filename}")
    else:
        print("\n❌ 基本連接測試失敗，請檢查 API 金鑰設定。")

if __name__ == "__main__":
    # 載入環境變數（如果有 .env 檔案）
    env_file = "../.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # 執行測試
    asyncio.run(main())
