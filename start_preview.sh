#!/bin/bash
# AIO 分析器本地預覽啟動腳本
# ===============================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AIO 分析器本地預覽啟動器${NC}"
echo "=================================="

# 檢查 Python
echo -e "${BLUE}📋 檢查系統需求...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安裝，請先安裝 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} 已安裝${NC}"

# 進入本地預覽目錄
cd "$(dirname "$0")/local_preview"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 創建虛擬環境...${NC}"
    python3 -m venv venv
fi

# 激活虛擬環境
echo -e "${BLUE}🔧 激活虛擬環境...${NC}"
source venv/bin/activate

# 安裝依賴
echo -e "${BLUE}📚 安裝依賴套件...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 檢查環境變數
echo -e "${BLUE}⚙️ 檢查環境配置...${NC}"

# 從父目錄讀取環境變數（如果存在）
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ 已載入環境變數${NC}"
else
    echo -e "${YELLOW}⚠️ 未找到 .env 文件，將使用演示模式${NC}"
fi

# 創建必要目錄
mkdir -p reports

# 啟動應用
echo -e "${GREEN}🎉 啟動 AIO 分析器本地預覽...${NC}"
echo ""
echo -e "${BLUE}📱 請在瀏覽器中訪問: ${GREEN}http://localhost:5000${NC}"
echo -e "${BLUE}💡 使用 Ctrl+C 停止服務${NC}"
echo ""

# 啟動 Flask 應用
python app.py
