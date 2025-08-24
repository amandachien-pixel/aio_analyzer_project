#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 潛力分析器設置腳本
=====================

用於檢查環境並協助初始化配置的設置腳本。
"""

import os
import sys
from pathlib import Path
import subprocess


def check_python_version():
    """檢查 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要 Python 3.8 或更高版本")
        return False


def check_dependencies():
    """檢查依賴套件"""
    print("\n📦 檢查依賴套件...")
    
    required_packages = [
        'pandas',
        'aiohttp', 
        'google-api-python-client',
        'google-ads',
        'tqdm',
        'colorlog'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 缺少以下套件: {', '.join(missing_packages)}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    return True


def check_config_files():
    """檢查配置文件"""
    print("\n⚙️ 檢查配置文件...")
    
    config_files = [
        ('config/credentials.json', '❌ GSC 憑證文件', '請從 Google Cloud Console 下載 OAuth 2.0 憑證'),
        ('config/google-ads.yaml', '❌ Google Ads 配置文件', '請複製 template 文件並填入 API 資訊'),
        ('.env', '❌ 環境變數文件', '請複製 config/env.example 為 .env 並設定 API 金鑰')
    ]
    
    all_exist = True
    
    for file_path, error_msg, instruction in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"{error_msg}: {file_path}")
            print(f"   💡 {instruction}")
            all_exist = False
    
    return all_exist


def create_directories():
    """創建必要的目錄"""
    print("\n📁 創建必要目錄...")
    
    directories = [
        'output',
        'logs',
        'config',
        'docs',
        'examples',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}/")


def setup_templates():
    """設置配置模板"""
    print("\n📝 設置配置模板...")
    
    # 檢查模板文件並提示用戶
    templates = [
        ('config/credentials.json.template', 'config/credentials.json'),
        ('config/google-ads.yaml.template', 'config/google-ads.yaml'),
        ('config/env.example', '.env')
    ]
    
    for template_path, target_path in templates:
        if os.path.exists(template_path) and not os.path.exists(target_path):
            print(f"📋 發現模板: {template_path}")
            print(f"   請複製並重命名為: {target_path}")
            print(f"   命令: cp {template_path} {target_path}")


def test_imports():
    """測試核心模組導入"""
    print("\n🧪 測試模組導入...")
    
    try:
        sys.path.append('src')
        from utils.logger import setup_logger
        print("✅ utils.logger")
        
        from config.settings import Config
        print("✅ config.settings")
        
        print("✅ 所有核心模組導入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False


def main():
    """主設置函數"""
    print("=" * 60)
    print("🚀 AIO 潛力分析器 - 環境設置檢查")
    print("=" * 60)
    
    checks = [
        ("Python 版本", check_python_version),
        ("依賴套件", check_dependencies),
        ("配置文件", check_config_files),
        ("模組導入", test_imports)
    ]
    
    # 創建目錄
    create_directories()
    setup_templates()
    
    # 執行檢查
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 檢查時發生錯誤: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有檢查通過！您可以開始使用 AIO 分析器了")
        print("\n📖 下一步:")
        print("   1. 運行範例: python examples/basic_usage.py")
        print("   2. 執行分析: python src/aio_analyzer.py")
        print("   3. 查看文檔: 閱讀 README.md 和 docs/")
    else:
        print("⚠️  部分檢查未通過，請按照上述提示完成配置")
        print("\n📚 需要幫助？")
        print("   1. 查看安裝指南: docs/installation_guide.md")
        print("   2. 檢查常見問題: README.md")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
