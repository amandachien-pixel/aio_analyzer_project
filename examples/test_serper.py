#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serper API 連接測試腳本
======================

用於測試 Serper API 配置是否正確，並驗證 AIO 檢測功能。
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
import json

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.serp_handler import SERPHandler
from utils.logger import setup_logger

# 測試關鍵字
TEST_KEYWORDS = [
    "what is artificial intelligence",
    "how to cook rice",
    "什麼是人工智慧",
    "如何煮飯",
    "best restaurants in taiwan"
]


async def test_serper_connection():
    """測試 Serper API 基本連接"""
    print("🔗 測試 Serper API 基本連接...")
    
    # 從環境變數或直接設定 API 金鑰
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        print("❌ 錯誤: 請設定 SERP_API_KEY 環境變數")
        print("   範例: export SERP_API_KEY=your-serper-api-key")
        return False
    
    # 測試請求
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'q': 'test query',
        'gl': 'tw',
        'hl': 'zh-tw'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://google.serper.dev/search',
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Serper API 連接成功!")
                    print(f"   查詢: {payload['q']}")
                    print(f"   回應時間: {response.headers.get('X-Response-Time', 'N/A')}")
                    print(f"   結果數量: {len(data.get('organic', []))}")
                    return True
                else:
                    print(f"❌ API 請求失敗: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   錯誤詳情: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")
        return False


async def test_aio_detection():
    """測試 AIO 檢測功能"""
    print("\n🤖 測試 AIO 檢測功能...")
    
    # 準備配置
    config = {
        'serp': {
            'provider': 'serper',
            'api_key': os.getenv('SERP_API_KEY'),
            'endpoint': 'https://google.serper.dev/search',
            'country': 'tw',
            'language': 'zh-tw',
            'concurrent_requests': 3,
            'rate_limit': 1.0
        },
        'performance': {
            'timeout': 15,
            'retry_attempts': 2,
            'retry_delay': 1
        }
    }
    
    # 設定日誌
    logger = setup_logger({'level': 'INFO'})
    
    try:
        # 初始化 SERP 處理器
        serp_handler = SERPHandler(config, logger)
        
        print(f"   API 提供商: {serp_handler.api_provider}")
        print(f"   端點: {serp_handler.endpoint}")
        print(f"   地區: {serp_handler.country}")
        print(f"   語言: {serp_handler.language}")
        
        # 測試單個關鍵字
        print(f"\n🔍 測試關鍵字: '{TEST_KEYWORDS[0]}'")
        result = await serp_handler.validate_single_keyword(TEST_KEYWORDS[0])
        
        if result.error:
            print(f"❌ 錯誤: {result.error}")
            return False
        else:
            print(f"✅ 查詢成功!")
            print(f"   觸發 AIO: {'是' if result.has_aio else '否'}")
            print(f"   總結果數: {result.total_results:,}")
            if result.aio_content:
                print(f"   AIO 內容: {result.aio_content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AIO 檢測測試失敗: {e}")
        return False


async def test_batch_processing():
    """測試批次處理功能"""
    print("\n📦 測試批次處理功能...")
    
    # 配置
    config = {
        'serp': {
            'provider': 'serper',
            'api_key': os.getenv('SERP_API_KEY'),
            'endpoint': 'https://google.serper.dev/search',
            'country': 'tw',
            'language': 'zh-tw',
            'concurrent_requests': 2,  # 降低並發以避免速率限制
            'rate_limit': 0.5  # 每 2 秒一次請求
        },
        'performance': {
            'timeout': 20,
            'retry_attempts': 1,
            'retry_delay': 2
        }
    }
    
    logger = setup_logger({'level': 'INFO'})
    
    try:
        serp_handler = SERPHandler(config, logger)
        
        # 測試前 3 個關鍵字
        test_keywords = TEST_KEYWORDS[:3]
        print(f"   測試關鍵字: {test_keywords}")
        
        results = await serp_handler.batch_validate_aio(test_keywords)
        
        print(f"✅ 批次處理完成!")
        print(f"   處理關鍵字數: {len(results)}")
        
        aio_count = sum(1 for has_aio in results.values() if has_aio)
        print(f"   觸發 AIO: {aio_count}/{len(results)}")
        
        # 顯示詳細結果
        for keyword, has_aio in results.items():
            status = "✅ 觸發 AIO" if has_aio else "❌ 未觸發"
            print(f"   • {keyword}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 批次處理測試失敗: {e}")
        return False


def check_environment():
    """檢查環境配置"""
    print("⚙️ 檢查環境配置...")
    
    # 檢查 API 金鑰
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        print("❌ SERP_API_KEY 環境變數未設定")
        return False
    elif api_key == 'your-serper-api-key':
        print("❌ 請設定正確的 Serper API 金鑰")
        return False
    else:
        print(f"✅ API 金鑰已設定 (長度: {len(api_key)})")
    
    # 檢查網路連接
    try:
        import urllib.request
        urllib.request.urlopen('https://google.serper.dev', timeout=5)
        print("✅ 網路連接正常")
    except Exception:
        print("❌ 無法連接到 Serper 服務")
        return False
    
    return True


def print_usage_info():
    """顯示使用說明"""
    print("\n📋 Serper API 設定說明:")
    print("1. 前往 https://serper.dev/ 註冊帳戶")
    print("2. 在控制台獲取 API 金鑰")
    print("3. 設定環境變數:")
    print("   export SERP_API_KEY=your-serper-api-key")
    print("4. 或在 .env 文件中添加:")
    print("   SERP_API_KEY=your-serper-api-key")
    print("   SERP_API_PROVIDER=serper")
    print("   SERP_API_ENDPOINT=https://google.serper.dev/search")


async def main():
    """主測試函數"""
    print("=" * 60)
    print("🧪 Serper API 測試工具")
    print("=" * 60)
    
    # 檢查環境
    if not check_environment():
        print_usage_info()
        return
    
    # 執行測試
    tests = [
        ("基本連接測試", test_serper_connection),
        ("AIO 檢測測試", test_aio_detection),
        ("批次處理測試", test_batch_processing),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if await test_func():
                passed_tests += 1
                print(f"✅ {test_name} 通過")
            else:
                print(f"❌ {test_name} 失敗")
        except Exception as e:
            print(f"❌ {test_name} 異常: {e}")
    
    # 顯示總結
    print("\n" + "=" * 60)
    print(f"📊 測試總結: {passed_tests}/{total_tests} 通過")
    
    if passed_tests == total_tests:
        print("🎉 所有測試通過! Serper API 配置正確")
        print("   您現在可以使用 Serper 進行 AIO 分析了!")
    else:
        print("⚠️ 部分測試失敗，請檢查配置")
        print_usage_info()
    
    print("=" * 60)


if __name__ == '__main__':
    # 設定事件循環政策 (for Windows)
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 執行測試
    asyncio.run(main())
