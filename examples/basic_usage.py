#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器基本使用範例
=====================

展示如何使用 AIO 潛力分析器進行基本的關鍵字分析。
"""

import asyncio
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from aio_analyzer import AIOAnalyzer


async def basic_analysis_example():
    """基本分析範例"""
    print("=== AIO 潛力分析器 - 基本使用範例 ===\n")
    
    try:
        # 初始化分析器
        print("🔧 初始化分析器...")
        analyzer = AIOAnalyzer()
        
        # 驗證配置
        if not analyzer.validate_configuration():
            print("❌ 配置驗證失敗，請檢查配置文件")
            return
        
        print("✅ 配置驗證通過\n")
        
        # 執行完整分析
        print("🚀 開始執行 AIO 潛力分析...")
        results = await analyzer.run_full_analysis(
            days_back=30,  # 分析過去 30 天
            regex_pattern=r'^(what|how|why|when|where|who|which)\b'  # 英文問句
        )
        
        # 顯示結果
        print("\n📊 分析結果摘要:")
        print("-" * 50)
        
        if results["status"] == "completed":
            print(f"✅ 分析狀態: 成功完成")
            print(f"📅 分析期間: {results['analysis_period']['start']} 至 {results['analysis_period']['end']}")
            print(f"🌱 種子關鍵字數量: {results['seed_keywords_count']}")
            print(f"🔍 擴展關鍵字數量: {results['expanded_keywords_count']}")
            print(f"🤖 觸發 AIO 關鍵字數量: {results['aio_triggers_count']}")
            print(f"📈 AIO 觸發率: {results['aio_percentage']}%")
            print(f"📄 報告位置: {results['report_path']}")
        else:
            print(f"❌ 分析失敗: {results.get('message', '未知錯誤')}")
        
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")


async def step_by_step_example():
    """分步驟執行範例"""
    print("\n=== 分步驟執行範例 ===\n")
    
    try:
        from datetime import datetime, timedelta
        
        analyzer = AIOAnalyzer()
        
        # 設定時間範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print("📊 步驟 1: 從 GSC 提取種子關鍵字...")
        gsc_data = await analyzer.extract_seed_keywords(
            start_date=start_date,
            end_date=end_date,
            regex_pattern=r'\b(什麼|如何|為什麼|怎麼)\b'  # 中文問句
        )
        
        if gsc_data.empty:
            print("⚠️ 未獲取到 GSC 數據，跳過後續步驟")
            return
        
        print(f"✅ 獲取到 {len(gsc_data)} 個種子關鍵字")
        
        print("\n🔍 步驟 2: 使用 Google Ads API 擴展關鍵字...")
        seed_keywords = gsc_data['query'].head(10).tolist()  # 只使用前10個
        expanded_data = await analyzer.expand_keywords(seed_keywords)
        
        if expanded_data.empty:
            print("⚠️ 關鍵字擴展失敗，跳過後續步驟")
            return
        
        print(f"✅ 擴展出 {len(expanded_data)} 個關鍵字")
        
        print("\n🤖 步驟 3: 驗證 AIO 觸發...")
        # 只驗證前5個關鍵字以節省時間
        sample_data = expanded_data.head(5).copy()
        validated_data = await analyzer.validate_aio_triggers(sample_data)
        
        aio_count = validated_data['triggers_aio'].sum() if 'triggers_aio' in validated_data.columns else 0
        print(f"✅ 驗證完成，{aio_count}/{len(validated_data)} 個關鍵字觸發 AIO")
        
        print("\n📋 步驟 4: 生成報告...")
        report_path = await analyzer.generate_comprehensive_report(validated_data, gsc_data)
        print(f"✅ 報告已生成: {report_path}")
        
    except Exception as e:
        print(f"❌ 分步驟執行錯誤: {e}")


async def custom_config_example():
    """自定義配置範例"""
    print("\n=== 自定義配置範例 ===\n")
    
    try:
        # 使用自定義配置
        analyzer = AIOAnalyzer()
        
        # 修改配置
        analyzer.config.set('serp.concurrent_requests', 5)  # 降低並發數
        analyzer.config.set('serp.rate_limit', 0.5)         # 降低請求頻率
        analyzer.config.set('output.format', 'excel')       # 使用 Excel 格式
        
        print("⚙️ 自定義配置已設定:")
        print(f"   並發請求數: {analyzer.config.get('serp.concurrent_requests')}")
        print(f"   請求頻率: {analyzer.config.get('serp.rate_limit')} 請求/秒")
        print(f"   輸出格式: {analyzer.config.get('output.format')}")
        
        # 測試 SERP API 連接
        print("\n🔗 測試 SERP API 連接...")
        if await analyzer.serp_handler.test_api_connection():
            print("✅ SERP API 連接正常")
        else:
            print("❌ SERP API 連接失敗")
        
    except Exception as e:
        print(f"❌ 自定義配置測試錯誤: {e}")


async def main():
    """主執行函數"""
    print("AIO 潛力分析器 - 使用範例")
    print("=" * 40)
    
    # 基本使用範例
    await basic_analysis_example()
    
    # 分步驟執行範例
    await step_by_step_example()
    
    # 自定義配置範例
    await custom_config_example()
    
    print("\n🎉 所有範例執行完成！")
    print("\n💡 提示:")
    print("   1. 確保已正確配置所有 API 憑證")
    print("   2. 根據您的需求調整分析參數")
    print("   3. 查看生成的報告以獲取詳細結果")


if __name__ == '__main__':
    asyncio.run(main())
