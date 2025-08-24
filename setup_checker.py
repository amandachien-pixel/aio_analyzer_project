#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器設定檢查工具
====================

自動檢查 API 設定狀態並提供設定建議。
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(file_path: str) -> bool:
    """檢查文件是否存在"""
    return os.path.exists(file_path)

def check_env_file() -> Tuple[bool, List[str]]:
    """檢查 .env 文件配置"""
    env_path = Path(__file__).parent / '.env'
    missing_vars = []
    
    if not env_path.exists():
        return False, [".env 文件不存在"]
    
    # 讀取 .env 文件
    required_vars = [
        'GSC_CREDENTIALS_FILE',
        'GOOGLE_ADS_YAML_FILE', 
        'SERP_API_KEY',
        'SITE_URL',
        'CUSTOMER_ID'
    ]
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(f"缺少環境變數: {var}")
            elif f"{var}=YOUR_" in content or f"{var}=your-" in content:
                missing_vars.append(f"環境變數 {var} 尚未設定實際值")
    
    except Exception as e:
        missing_vars.append(f"讀取 .env 文件失敗: {e}")
    
    return len(missing_vars) == 0, missing_vars

def check_gsc_credentials() -> Tuple[bool, List[str]]:
    """檢查 Google Search Console 憑證"""
    config_dir = Path(__file__).parent / 'config'
    cred_file = config_dir / 'credentials.json'
    issues = []
    
    if not cred_file.exists():
        issues.append("credentials.json 文件不存在")
        return False, issues
    
    try:
        with open(cred_file, 'r') as f:
            cred_data = json.load(f)
        
        # 檢查必要欄位
        if 'type' in cred_data and cred_data['type'] == 'service_account':
            required_fields = ['client_email', 'private_key', 'project_id']
            for field in required_fields:
                if field not in cred_data:
                    issues.append(f"credentials.json 缺少欄位: {field}")
        else:
            # OAuth 格式檢查
            if 'installed' in cred_data:
                required_fields = ['client_id', 'client_secret']
                installed = cred_data['installed']
                for field in required_fields:
                    if field not in installed or 'YOUR_' in str(installed[field]):
                        issues.append(f"credentials.json 的 {field} 尚未設定")
            else:
                issues.append("credentials.json 格式不正確")
    
    except json.JSONDecodeError:
        issues.append("credentials.json 格式錯誤")
    except Exception as e:
        issues.append(f"檢查 credentials.json 時發生錯誤: {e}")
    
    return len(issues) == 0, issues

def check_google_ads_config() -> Tuple[bool, List[str]]:
    """檢查 Google Ads API 配置"""
    config_dir = Path(__file__).parent / 'config'
    ads_file = config_dir / 'google-ads.yaml'
    issues = []
    
    if not ads_file.exists():
        issues.append("google-ads.yaml 文件不存在")
        return False, issues
    
    try:
        with open(ads_file, 'r') as f:
            ads_config = yaml.safe_load(f)
        
        required_fields = [
            'developer_token',
            'client_id', 
            'client_secret',
            'refresh_token'
        ]
        
        for field in required_fields:
            if field not in ads_config:
                issues.append(f"google-ads.yaml 缺少欄位: {field}")
            elif 'YOUR_' in str(ads_config[field]):
                issues.append(f"google-ads.yaml 的 {field} 尚未設定實際值")
    
    except yaml.YAMLError:
        issues.append("google-ads.yaml 格式錯誤")
    except Exception as e:
        issues.append(f"檢查 google-ads.yaml 時發生錯誤: {e}")
    
    return len(issues) == 0, issues

def check_serper_api() -> Tuple[bool, List[str]]:
    """檢查 Serper API 設定"""
    issues = []
    
    # 檢查環境變數
    api_key = os.getenv('SERP_API_KEY')
    
    if not api_key:
        issues.append("SERP_API_KEY 環境變數未設定")
    elif api_key == "YOUR_SERP_API_KEY" or api_key == "your-serper-api-key-here":
        issues.append("SERP_API_KEY 尚未設定實際值")
    elif len(api_key) < 10:
        issues.append("SERP_API_KEY 長度過短，可能不是有效的 API 金鑰")
    
    return len(issues) == 0, issues

def get_setup_progress() -> Dict[str, Dict]:
    """獲取整體設定進度"""
    checks = {
        'env_file': {
            'name': '環境變數配置 (.env)',
            'status': False,
            'issues': []
        },
        'gsc_credentials': {
            'name': 'Google Search Console 憑證',
            'status': False,
            'issues': []
        },
        'google_ads': {
            'name': 'Google Ads API 配置',
            'status': False,
            'issues': []
        },
        'serper_api': {
            'name': 'Serper API 金鑰',
            'status': False,
            'issues': []
        }
    }
    
    # 執行各項檢查
    checks['env_file']['status'], checks['env_file']['issues'] = check_env_file()
    checks['gsc_credentials']['status'], checks['gsc_credentials']['issues'] = check_gsc_credentials()
    checks['google_ads']['status'], checks['google_ads']['issues'] = check_google_ads_config()
    checks['serper_api']['status'], checks['serper_api']['issues'] = check_serper_api()
    
    return checks

def print_setup_report():
    """列印設定報告"""
    print("🔍 AIO 分析器設定檢查報告")
    print("=" * 50)
    
    checks = get_setup_progress()
    completed = 0
    total = len(checks)
    
    for check_id, check_info in checks.items():
        status_icon = "✅" if check_info['status'] else "❌"
        print(f"{status_icon} {check_info['name']}")
        
        if check_info['status']:
            completed += 1
            print("   狀態：已完成")
        else:
            print("   狀態：需要設定")
            for issue in check_info['issues']:
                print(f"   - {issue}")
        print()
    
    # 進度總結
    progress = (completed / total) * 100
    print("=" * 50)
    print(f"📊 設定進度: {completed}/{total} ({progress:.0f}%)")
    
    if completed == total:
        print("🎉 恭喜！所有 API 設定已完成！")
        print("✅ 您可以開始使用 AIO 分析器了")
        print("\n🚀 下一步：")
        print("   python3 local_preview/app.py")
    else:
        print("⚠️  請完成上述未設定的項目")
        print("\n📖 完整設定指引：")
        print("   參考 COMPLETE_API_SETUP.md")
    
    return completed == total

def generate_setup_commands():
    """生成設定命令"""
    print("\n🛠️  快速設定命令：")
    print("-" * 30)
    
    # 檢查哪些文件缺失
    config_dir = Path(__file__).parent / 'config'
    
    if not (config_dir / 'credentials.json').exists():
        print("# 1. 設定 Google Search Console 憑證")
        print("# 從 Google Cloud Console 下載服務帳戶 JSON 文件後：")
        print("cp ~/Downloads/your-service-account-key.json config/credentials.json")
        print()
    
    if not (config_dir / 'google-ads.yaml').exists():
        print("# 2. 設定 Google Ads API 配置")
        print("cp config/google-ads.yaml.template config/google-ads.yaml")
        print("# 然後編輯 config/google-ads.yaml 填入您的 API 憑證")
        print()
    
    if not Path(__file__).parent / '.env':
        print("# 3. 設定環境變數")
        print("cp config/env.example .env")
        print("# 然後編輯 .env 填入您的 API 金鑰和設定")
        print()
    
    print("# 4. 測試設定")
    print("python3 setup_checker.py")

if __name__ == "__main__":
    # 載入環境變數（如果存在 .env 文件）
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            print("💡 建議安裝 python-dotenv: pip install python-dotenv")
    
    # 執行檢查
    is_complete = print_setup_report()
    
    if not is_complete:
        generate_setup_commands()
    
    print("\n" + "=" * 50)
    print("💡 提示：執行 python3 setup_checker.py 隨時檢查設定狀態")
