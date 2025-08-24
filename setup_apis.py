#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器 API 設定助手
=====================

自動化 API 設定流程，驗證配置，並提供互動式設定體驗。
"""

import os
import sys
import json
import yaml
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional

# 顏色定義
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(text: str, color: str) -> None:
    """印出有色彩的文字"""
    print(f"{color}{text}{Colors.NC}")

def print_header(title: str) -> None:
    """印出標題"""
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored(f"🔧 {title}", Colors.WHITE)
    print_colored(f"{'='*60}", Colors.BLUE)

def print_step(step: str) -> None:
    """印出步驟"""
    print_colored(f"\n📋 {step}", Colors.CYAN)

def print_success(message: str) -> None:
    """印出成功訊息"""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_error(message: str) -> None:
    """印出錯誤訊息"""
    print_colored(f"❌ {message}", Colors.RED)

def print_warning(message: str) -> None:
    """印出警告訊息"""
    print_colored(f"⚠️ {message}", Colors.YELLOW)

class APISetupHelper:
    """API 設定助手"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / 'config'
        self.env_file = self.project_root / '.env'
        
        # 確保配置目錄存在
        self.config_dir.mkdir(exist_ok=True)
    
    async def run_full_setup(self):
        """執行完整設定流程"""
        print_header("AIO 分析器 API 設定助手")
        
        print_colored("🚀 歡迎使用 AIO 分析器！", Colors.WHITE)
        print_colored("本助手將引導您完成所有 API 的設定。", Colors.WHITE)
        
        # 檢查現有配置
        await self.check_existing_config()
        
        # 設定各個 API
        await self.setup_google_search_console()
        await self.setup_google_ads_api()
        await self.setup_serper_api()
        
        # 生成環境配置
        await self.generate_env_config()
        
        # 驗證設定
        await self.validate_all_apis()
        
        # 完成
        self.print_completion_summary()
    
    async def check_existing_config(self):
        """檢查現有配置"""
        print_step("檢查現有配置")
        
        # 檢查憑證檔案
        credentials_file = self.config_dir / 'credentials.json'
        if credentials_file.exists():
            print_success(f"找到 GSC 憑證檔案: {credentials_file}")
        else:
            print_warning(f"未找到 GSC 憑證檔案: {credentials_file}")
        
        # 檢查 Google Ads 配置
        ads_config_file = self.config_dir / 'google-ads.yaml'
        if ads_config_file.exists():
            print_success(f"找到 Google Ads 配置: {ads_config_file}")
        else:
            print_warning(f"未找到 Google Ads 配置: {ads_config_file}")
        
        # 檢查環境變數檔案
        if self.env_file.exists():
            print_success(f"找到環境變數檔案: {self.env_file}")
        else:
            print_warning(f"未找到環境變數檔案: {self.env_file}")
    
    async def setup_google_search_console(self):
        """設定 Google Search Console API"""
        print_step("設定 Google Search Console API")
        
        credentials_file = self.config_dir / 'credentials.json'
        
        if not credentials_file.exists():
            print_colored("📥 請完成以下步驟來設定 Google Search Console API:", Colors.YELLOW)
            print("1. 前往 Google Cloud Console (https://console.cloud.google.com/)")
            print("2. 創建新專案或選擇現有專案")
            print("3. 啟用 'Google Search Console API'")
            print("4. 創建服務帳戶並下載 JSON 憑證檔案")
            print("5. 將檔案重新命名為 'credentials.json'")
            print(f"6. 將檔案放置在: {credentials_file}")
            
            input("\n按 Enter 繼續（確認您已完成上述步驟）...")
            
            if credentials_file.exists():
                print_success("GSC 憑證檔案已找到！")
                # 驗證憑證檔案格式
                try:
                    with open(credentials_file, 'r') as f:
                        creds_data = json.load(f)
                    
                    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                    if all(field in creds_data for field in required_fields):
                        print_success("憑證檔案格式正確")
                        print_colored(f"服務帳戶電子郵件: {creds_data['client_email']}", Colors.CYAN)
                        print_warning("⚠️ 請確認已將此電子郵件添加到 Search Console 用戶權限中")
                    else:
                        print_error("憑證檔案格式不正確，請檢查 JSON 格式")
                        
                except json.JSONDecodeError:
                    print_error("憑證檔案不是有效的 JSON 格式")
                except Exception as e:
                    print_error(f"讀取憑證檔案時發生錯誤: {e}")
            else:
                print_error("未找到憑證檔案，請重新檢查檔案路徑")
        else:
            print_success("GSC 憑證檔案已存在")
    
    async def setup_google_ads_api(self):
        """設定 Google Ads API"""
        print_step("設定 Google Ads API")
        
        ads_config_file = self.config_dir / 'google-ads.yaml'
        
        if not ads_config_file.exists():
            print_colored("📥 請完成以下步驟來設定 Google Ads API:", Colors.YELLOW)
            print("1. 前往 Google Ads API 申請頁面")
            print("2. 申請開發者權杖（Developer Token）")
            print("3. 創建 OAuth 2.0 憑證")
            print("4. 獲取 refresh_token")
            
            # 互動式配置
            print_colored("\n📝 請輸入 Google Ads API 配置資訊:", Colors.CYAN)
            
            developer_token = input("開發者權杖 (Developer Token): ").strip()
            client_id = input("客戶端 ID (Client ID): ").strip()
            client_secret = input("客戶端密鑰 (Client Secret): ").strip()
            refresh_token = input("更新權杖 (Refresh Token): ").strip()
            login_customer_id = input("登入客戶 ID (Login Customer ID): ").strip()
            
            # 生成配置檔案
            ads_config = {
                'developer_token': developer_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'login_customer_id': login_customer_id,
                'use_proto_plus': True
            }
            
            try:
                with open(ads_config_file, 'w') as f:
                    yaml.dump(ads_config, f, default_flow_style=False)
                print_success(f"Google Ads 配置已儲存到: {ads_config_file}")
            except Exception as e:
                print_error(f"儲存配置檔案時發生錯誤: {e}")
        else:
            print_success("Google Ads 配置檔案已存在")
    
    async def setup_serper_api(self):
        """設定 Serper API"""
        print_step("設定 Serper API")
        
        print_colored("📥 請完成以下步驟來設定 Serper API:", Colors.YELLOW)
        print("1. 前往 Serper.dev (https://serper.dev/)")
        print("2. 註冊帳戶並確認電子郵件")
        print("3. 前往儀表板獲取 API 金鑰")
        print("4. 免費方案提供 2,500 次查詢/月")
        
        api_key = input("\n請輸入您的 Serper API 金鑰: ").strip()
        
        if api_key:
            # 測試 API 金鑰
            await self.test_serper_api(api_key)
            self.serper_api_key = api_key
        else:
            print_warning("未輸入 API 金鑰，將在環境配置中使用占位符")
            self.serper_api_key = "your-serper-api-key-here"
    
    async def test_serper_api(self, api_key: str) -> bool:
        """測試 Serper API 連接"""
        print_colored("🧪 測試 Serper API 連接...", Colors.CYAN)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }
                data = {'q': 'test query'}
                
                async with session.post(
                    'https://google.serper.dev/search',
                    headers=headers,
                    json=data,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        print_success("Serper API 連接成功！")
                        return True
                    else:
                        print_error(f"Serper API 測試失敗，狀態碼: {response.status}")
                        return False
                        
        except Exception as e:
            print_error(f"Serper API 測試時發生錯誤: {e}")
            return False
    
    async def generate_env_config(self):
        """生成環境配置檔案"""
        print_step("生成環境配置檔案")
        
        env_content = f"""# ===========================================
# AIO 分析器環境配置
# ===========================================

# Django 設定
SECRET_KEY=aio-analyzer-secret-key-{os.urandom(16).hex()}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 資料庫設定 (開發用 SQLite)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Google Search Console API
GSC_CREDENTIALS_FILE={self.config_dir / 'credentials.json'}
GSC_TOKEN_FILE={self.config_dir / 'token.json'}

# Google Ads API
GOOGLE_ADS_YAML_FILE={self.config_dir / 'google-ads.yaml'}

# SERP API 設定 (Serper)
SERP_API_PROVIDER=serper
SERP_API_KEY={getattr(self, 'serper_api_key', 'your-serper-api-key-here')}
SERP_API_ENDPOINT=https://google.serper.dev/search

# 效能設定
DEFAULT_RATE_LIMIT=10
MAX_CONCURRENT_REQUESTS=5
REPORTS_STORAGE_DAYS=30

# Redis 設定 (可選，用於生產環境)
REDIS_URL=redis://localhost:6379/0

# Celery 設定 (可選，用於生產環境)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            print_success(f"環境配置已儲存到: {self.env_file}")
        except Exception as e:
            print_error(f"儲存環境配置時發生錯誤: {e}")
    
    async def validate_all_apis(self):
        """驗證所有 API 設定"""
        print_step("驗證 API 設定")
        
        # 檢查檔案存在性
        files_to_check = [
            (self.config_dir / 'credentials.json', 'Google Search Console 憑證'),
            (self.config_dir / 'google-ads.yaml', 'Google Ads 配置'),
            (self.env_file, '環境變數檔案')
        ]
        
        all_files_exist = True
        for file_path, description in files_to_check:
            if file_path.exists():
                print_success(f"{description}: ✓")
            else:
                print_error(f"{description}: ✗")
                all_files_exist = False
        
        if all_files_exist:
            print_success("所有配置檔案都已就位！")
        else:
            print_warning("部分配置檔案缺失，請檢查上述項目")
        
        # 提供測試腳本
        print_colored("\n🧪 要測試 API 連接，請執行:", Colors.CYAN)
        print(f"cd {self.project_root}")
        print("python3 test_apis.py")
    
    def print_completion_summary(self):
        """印出完成摘要"""
        print_header("設定完成！")
        
        print_colored("🎉 恭喜！AIO 分析器 API 設定已完成", Colors.GREEN)
        
        print_colored("\n📋 下一步:", Colors.CYAN)
        print("1. 測試 API 連接: python3 test_apis.py")
        print("2. 啟動本地預覽: python3 local_preview/app.py")
        print("3. 或啟動完整版本: cd backend && python3 manage.py runserver")
        
        print_colored("\n📚 重要提醒:", Colors.YELLOW)
        print("• 確保已將服務帳戶電子郵件添加到 Search Console 權限")
        print("• 確保 Google Ads API 申請已獲核准")
        print("• 監控 Serper API 使用量避免超過限額")
        
        print_colored("\n🔗 有用的連結:", Colors.PURPLE)
        print("• Google Cloud Console: https://console.cloud.google.com/")
        print("• Google Search Console: https://search.google.com/search-console/")
        print("• Google Ads API: https://ads.google.com/nav/selectaccount")
        print("• Serper.dev: https://serper.dev/")
        
        print_colored(f"\n📁 配置檔案位置:", Colors.BLUE)
        print(f"• GSC 憑證: {self.config_dir / 'credentials.json'}")
        print(f"• Google Ads: {self.config_dir / 'google-ads.yaml'}")
        print(f"• 環境變數: {self.env_file}")

async def main():
    """主函數"""
    try:
        setup_helper = APISetupHelper()
        await setup_helper.run_full_setup()
    except KeyboardInterrupt:
        print_colored("\n\n👋 設定已取消", Colors.YELLOW)
    except Exception as e:
        print_error(f"\n設定過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
