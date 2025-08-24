#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器 API 連接測試
=====================

測試所有 API 服務的連接狀態，驗證配置是否正確。
"""

import os
import sys
import json
import yaml
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta

# 顏色定義
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'

def print_colored(text: str, color: str) -> None:
    """印出有色彩的文字"""
    print(f"{color}{text}{Colors.NC}")

def print_header(title: str) -> None:
    """印出標題"""
    print_colored(f"\n{'='*60}", Colors.BLUE)
    print_colored(f"🧪 {title}", Colors.WHITE)
    print_colored(f"{'='*60}", Colors.BLUE)

def print_test(name: str) -> None:
    """印出測試名稱"""
    print_colored(f"\n🔍 測試 {name}...", Colors.CYAN)

def print_success(message: str) -> None:
    """印出成功訊息"""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_error(message: str) -> None:
    """印出錯誤訊息"""
    print_colored(f"❌ {message}", Colors.RED)

def print_warning(message: str) -> None:
    """印出警告訊息"""
    print_colored(f"⚠️ {message}", Colors.YELLOW)

class APITester:
    """API 連接測試器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / 'config'
        self.env_file = self.project_root / '.env'
        
        # 載入環境變數
        self.load_env_variables()
        
        # 測試結果
        self.test_results = {
            'gsc': False,
            'google_ads': False,
            'serper': False
        }
    
    def load_env_variables(self):
        """載入環境變數"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    async def run_all_tests(self):
        """執行所有 API 測試"""
        print_header("AIO 分析器 API 連接測試")
        
        print_colored("🚀 開始測試所有 API 連接...", Colors.WHITE)
        print_colored(f"📁 專案路徑: {self.project_root}", Colors.BLUE)
        
        # 測試配置檔案
        await self.test_config_files()
        
        # 測試各個 API
        await self.test_google_search_console()
        await self.test_google_ads_api()
        await self.test_serper_api()
        
        # 測試摘要
        self.print_test_summary()
    
    async def test_config_files(self):
        """測試配置檔案"""
        print_test("配置檔案")
        
        # 檢查 GSC 憑證
        gsc_credentials = self.config_dir / 'credentials.json'
        if gsc_credentials.exists():
            try:
                with open(gsc_credentials, 'r') as f:
                    creds_data = json.load(f)
                
                required_fields = ['type', 'project_id', 'private_key', 'client_email']
                if all(field in creds_data for field in required_fields):
                    print_success(f"GSC 憑證檔案: {gsc_credentials}")
                    print_colored(f"  服務帳戶: {creds_data['client_email']}", Colors.CYAN)
                else:
                    print_error("GSC 憑證檔案格式不完整")
            except Exception as e:
                print_error(f"GSC 憑證檔案讀取失敗: {e}")
        else:
            print_error(f"GSC 憑證檔案不存在: {gsc_credentials}")
        
        # 檢查 Google Ads 配置
        ads_config = self.config_dir / 'google-ads.yaml'
        if ads_config.exists():
            try:
                with open(ads_config, 'r') as f:
                    ads_data = yaml.safe_load(f)
                
                required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
                if all(field in ads_data for field in required_fields):
                    print_success(f"Google Ads 配置: {ads_config}")
                    print_colored(f"  客戶端 ID: {ads_data['client_id'][:20]}...", Colors.CYAN)
                else:
                    print_error("Google Ads 配置檔案格式不完整")
            except Exception as e:
                print_error(f"Google Ads 配置檔案讀取失敗: {e}")
        else:
            print_error(f"Google Ads 配置檔案不存在: {ads_config}")
        
        # 檢查環境變數
        if self.env_file.exists():
            print_success(f"環境變數檔案: {self.env_file}")
            serp_key = os.getenv('SERP_API_KEY', '')
            if serp_key and serp_key != 'your-serper-api-key-here':
                print_colored(f"  Serper API Key: {serp_key[:10]}...", Colors.CYAN)
            else:
                print_warning("  Serper API Key 未設定或使用默認值")
        else:
            print_error(f"環境變數檔案不存在: {self.env_file}")
    
    async def test_google_search_console(self):
        """測試 Google Search Console API"""
        print_test("Google Search Console API")
        
        try:
            # 檢查憑證檔案
            credentials_file = self.config_dir / 'credentials.json'
            if not credentials_file.exists():
                print_error("憑證檔案不存在，跳過 GSC API 測試")
                return
            
            # 嘗試導入和初始化 GSC 客戶端
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                
                # 載入憑證
                credentials = service_account.Credentials.from_service_account_file(
                    str(credentials_file),
                    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
                )
                
                # 建立服務
                service = build('searchconsole', 'v1', credentials=credentials)
                
                # 測試 API 調用（取得網站列表）
                sites_response = service.sites().list().execute()
                
                print_success("Google Search Console API 連接成功")
                
                # 顯示可用的網站
                sites = sites_response.get('siteEntry', [])
                if sites:
                    print_colored(f"  找到 {len(sites)} 個網站屬性:", Colors.CYAN)
                    for site in sites[:3]:  # 只顯示前3個
                        print_colored(f"    • {site['siteUrl']}", Colors.CYAN)
                else:
                    print_warning("  未找到網站屬性，請檢查服務帳戶權限")
                
                self.test_results['gsc'] = True
                
            except ImportError:
                print_error("Google API 客戶端未安裝: pip install google-api-python-client google-auth")
            except Exception as e:
                print_error(f"GSC API 測試失敗: {e}")
                
        except Exception as e:
            print_error(f"GSC API 測試時發生錯誤: {e}")
    
    async def test_google_ads_api(self):
        """測試 Google Ads API"""
        print_test("Google Ads API")
        
        try:
            # 檢查配置檔案
            ads_config_file = self.config_dir / 'google-ads.yaml'
            if not ads_config_file.exists():
                print_error("Google Ads 配置檔案不存在，跳過測試")
                return
            
            try:
                from google.ads.googleads.client import GoogleAdsClient
                
                # 載入配置
                client = GoogleAdsClient.load_from_storage(str(ads_config_file))
                
                # 測試簡單的 API 調用
                ga_service = client.get_service("GoogleAdsService")
                
                # 嘗試取得客戶資訊
                with open(ads_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                customer_id = config.get('login_customer_id', '').replace('-', '')
                if customer_id:
                    query = """
                        SELECT customer.id, customer.descriptive_name
                        FROM customer
                        LIMIT 1
                    """
                    response = ga_service.search(customer_id=customer_id, query=query)
                    
                    for row in response:
                        customer = row.customer
                        print_success("Google Ads API 連接成功")
                        print_colored(f"  客戶 ID: {customer.id}", Colors.CYAN)
                        print_colored(f"  客戶名稱: {customer.descriptive_name}", Colors.CYAN)
                        self.test_results['google_ads'] = True
                        break
                else:
                    print_warning("未設定 login_customer_id，無法測試 API 連接")
                    
            except ImportError:
                print_error("Google Ads API 客戶端未安裝: pip install google-ads")
            except Exception as e:
                print_error(f"Google Ads API 測試失敗: {e}")
                
        except Exception as e:
            print_error(f"Google Ads API 測試時發生錯誤: {e}")
    
    async def test_serper_api(self):
        """測試 Serper API"""
        print_test("Serper API")
        
        try:
            api_key = os.getenv('SERP_API_KEY', '')
            
            if not api_key or api_key == 'your-serper-api-key-here':
                print_error("Serper API 金鑰未設定")
                return
            
            # 測試 API 調用
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }
                
                # 測試搜尋查詢
                test_data = {
                    'q': 'what is AI overview',
                    'type': 'search',
                    'gl': 'tw',
                    'hl': 'zh-tw'
                }
                
                async with session.post(
                    'https://google.serper.dev/search',
                    headers=headers,
                    json=test_data,
                    timeout=15
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        print_success("Serper API 連接成功")
                        
                        # 分析回應內容
                        if 'organic' in data:
                            print_colored(f"  找到 {len(data['organic'])} 個搜尋結果", Colors.CYAN)
                        
                        if 'aiOverview' in data:
                            print_colored("  ✓ 檢測到 AI Overview", Colors.GREEN)
                        elif 'answerBox' in data:
                            print_colored("  ✓ 檢測到 Answer Box", Colors.YELLOW)
                        else:
                            print_colored("  ○ 此查詢未觸發 AI Overview", Colors.CYAN)
                        
                        # 檢查 API 使用量（如果有提供）
                        if 'credits' in response.headers:
                            print_colored(f"  剩餘查詢額度: {response.headers['credits']}", Colors.CYAN)
                        
                        self.test_results['serper'] = True
                        
                    elif response.status == 401:
                        print_error("Serper API 認證失敗，請檢查 API 金鑰")
                    elif response.status == 429:
                        print_error("Serper API 查詢額度已耗盡")
                    else:
                        print_error(f"Serper API 測試失敗，狀態碼: {response.status}")
                        
        except asyncio.TimeoutError:
            print_error("Serper API 請求超時")
        except Exception as e:
            print_error(f"Serper API 測試時發生錯誤: {e}")
    
    def print_test_summary(self):
        """印出測試摘要"""
        print_header("測試結果摘要")
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        print_colored(f"📊 測試通過: {passed_tests}/{total_tests}", Colors.WHITE)
        
        # 詳細結果
        for service, passed in self.test_results.items():
            status = "✅ 通過" if passed else "❌ 失敗"
            service_name = {
                'gsc': 'Google Search Console',
                'google_ads': 'Google Ads API',
                'serper': 'Serper API'
            }[service]
            
            print_colored(f"  {service_name}: {status}", Colors.CYAN)
        
        # 建議
        print_colored("\n💡 建議:", Colors.YELLOW)
        
        if not self.test_results['gsc']:
            print("• 確認 GSC 憑證檔案存在且格式正確")
            print("• 確認服務帳戶已添加到 Search Console 權限")
        
        if not self.test_results['google_ads']:
            print("• 確認 Google Ads API 申請已獲核准")
            print("• 確認 OAuth 授權已完成並獲得 refresh_token")
            print("• 確認客戶 ID 格式正確")
        
        if not self.test_results['serper']:
            print("• 確認 Serper API 金鑰正確")
            print("• 檢查 API 查詢額度是否充足")
        
        if passed_tests == total_tests:
            print_colored("\n🎉 所有 API 測試通過！您可以開始使用 AIO 分析器了。", Colors.GREEN)
            print_colored("\n🚀 啟動應用:", Colors.CYAN)
            print("  python3 local_preview/app.py")
            print("  或")
            print("  cd backend && python3 manage.py runserver")
        else:
            print_colored(f"\n⚠️ {total_tests - passed_tests} 個 API 測試失敗，請檢查配置。", Colors.YELLOW)
            print_colored("📚 參考設定指南: API_SETUP_GUIDE.md", Colors.CYAN)

async def main():
    """主函數"""
    try:
        tester = APITester()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print_colored("\n\n👋 測試已取消", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ 測試過程中發生錯誤: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
