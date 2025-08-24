#!/bin/bash
# AIO 分析器快速設定腳本
# ===========================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${WHITE}🚀 $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# 檢查必要工具
check_requirements() {
    print_step "檢查系統需求"
    
    # 檢查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python ${PYTHON_VERSION} 已安裝"
    else
        print_error "Python 3 未安裝，請先安裝 Python 3.8+"
        exit 1
    fi
    
    # 檢查 pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 已安裝"
    else
        print_error "pip3 未安裝"
        exit 1
    fi
    
    # 檢查 git
    if command -v git &> /dev/null; then
        print_success "Git 已安裝"
    else
        print_warning "Git 未安裝（可選）"
    fi
}

# 安裝 Python 依賴
install_dependencies() {
    print_step "安裝 Python 依賴套件"
    
    # 升級 pip
    echo "升級 pip..."
    python3 -m pip install --upgrade pip
    
    # 安裝基本依賴
    echo "安裝基本依賴..."
    pip3 install -q flask pandas numpy pyyaml python-dotenv aiohttp colorlog tqdm
    
    # 安裝 Google API 依賴（可選）
    echo "安裝 Google API 依賴..."
    pip3 install -q google-api-python-client google-auth-httplib2 google-auth-oauthlib || {
        print_warning "Google API 客戶端安裝失敗，將在稍後嘗試"
    }
    
    # 安裝 Google Ads API（可選）
    echo "安裝 Google Ads API..."
    pip3 install -q google-ads || {
        print_warning "Google Ads API 客戶端安裝失敗，將在稍後嘗試"
    }
    
    print_success "Python 依賴安裝完成"
}

# 創建配置目錄
setup_config_structure() {
    print_step "設定專案結構"
    
    # 確保配置目錄存在
    mkdir -p config
    mkdir -p local_preview/reports
    mkdir -p logs
    
    # 創建配置範例檔案（如果不存在）
    if [ ! -f "config/credentials.json.template" ]; then
        cat > config/credentials.json.template << 'EOF'
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
EOF
        print_success "創建 GSC 憑證範例"
    fi
    
    if [ ! -f "config/google-ads.yaml.template" ]; then
        cat > config/google-ads.yaml.template << 'EOF'
# Google Ads API 配置範例
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "1234567890"
use_proto_plus: True
EOF
        print_success "創建 Google Ads 配置範例"
    fi
    
    print_success "專案結構設定完成"
}

# 創建環境變數檔案
create_env_file() {
    print_step "創建環境變數檔案"
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# ===========================================
# AIO 分析器環境配置
# ===========================================

# Django 設定
SECRET_KEY=aio-analyzer-secret-key-$(openssl rand -hex 16)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 資料庫設定 (開發用 SQLite)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Google Search Console API
GSC_CREDENTIALS_FILE=$(pwd)/config/credentials.json
GSC_TOKEN_FILE=$(pwd)/config/token.json

# Google Ads API
GOOGLE_ADS_YAML_FILE=$(pwd)/config/google-ads.yaml

# SERP API 設定 (Serper)
SERP_API_PROVIDER=serper
SERP_API_KEY=your-serper-api-key-here
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
EOF
        print_success "環境變數檔案已創建"
    else
        print_warning "環境變數檔案已存在，跳過創建"
    fi
}

# 設置權限
set_permissions() {
    print_step "設置檔案權限"
    
    # 設置腳本執行權限
    chmod +x setup_apis.py 2>/dev/null || true
    chmod +x test_apis.py 2>/dev/null || true
    chmod +x start_preview.sh 2>/dev/null || true
    chmod +x quick_setup.sh 2>/dev/null || true
    
    # 設置配置檔案權限（安全考量）
    chmod 600 .env 2>/dev/null || true
    chmod 600 config/*.json 2>/dev/null || true
    chmod 600 config/*.yaml 2>/dev/null || true
    
    print_success "檔案權限設置完成"
}

# 測試安裝
test_installation() {
    print_step "測試安裝"
    
    # 測試 Python 導入
    python3 -c "
import flask
import pandas
import numpy
import yaml
import json
import aiohttp
print('✅ 所有基本套件導入成功')
" || {
        print_error "部分套件導入失敗"
        return 1
    }
    
    print_success "安裝測試通過"
}

# 顯示下一步
show_next_steps() {
    print_header "設定完成！"
    
    echo -e "${GREEN}🎉 AIO 分析器快速設定已完成！${NC}\n"
    
    echo -e "${CYAN}📋 下一步操作:${NC}"
    echo "1. 設定 API 憑證:"
    echo "   python3 setup_apis.py"
    echo ""
    echo "2. 測試 API 連接:"
    echo "   python3 test_apis.py"
    echo ""
    echo "3. 啟動本地預覽:"
    echo "   python3 local_preview/app_simple.py"
    echo ""
    echo "4. 或啟動完整版本:"
    echo "   cd backend && python3 manage.py runserver"
    
    echo -e "\n${PURPLE}📚 文檔資源:${NC}"
    echo "• API 設定指南: API_SETUP_GUIDE.md"
    echo "• 本地預覽說明: local_preview/README.md"
    echo "• 專案升級摘要: UPGRADE_SUMMARY.md"
    
    echo -e "\n${YELLOW}⚠️ 重要提醒:${NC}"
    echo "• 請先設定 API 憑證才能使用真實數據"
    echo "• 演示模式可以立即使用，無需 API 憑證"
    echo "• 完整功能需要 Google 和 Serper API"
    
    echo -e "\n${BLUE}🔗 有用連結:${NC}"
    echo "• Google Cloud Console: https://console.cloud.google.com/"
    echo "• Google Search Console: https://search.google.com/search-console/"
    echo "• Serper.dev: https://serper.dev/"
}

# 主程序
main() {
    print_header "AIO 分析器快速設定"
    
    echo -e "${WHITE}歡迎使用 AIO 潛力分析器快速設定腳本！${NC}"
    echo -e "${WHITE}此腳本將自動安裝依賴並初始化專案。${NC}\n"
    
    # 確認繼續
    read -p "按 Enter 繼續，或按 Ctrl+C 取消..."
    
    # 執行設定步驟
    check_requirements
    install_dependencies
    setup_config_structure
    create_env_file
    set_permissions
    test_installation
    
    # 顯示完成資訊
    show_next_steps
}

# 錯誤處理
trap 'echo -e "\n${RED}❌ 設定過程中發生錯誤${NC}"; exit 1' ERR

# 執行主程序
main "$@"
