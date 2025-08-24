@echo off
REM AIO 分析器本地預覽啟動腳本 (Windows)
REM ===========================================

echo 🚀 AIO 分析器本地預覽啟動器
echo ==================================

REM 檢查 Python
echo 📋 檢查系統需求...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安裝，請先安裝 Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 已安裝

REM 進入本地預覽目錄
cd /d "%~dp0\local_preview"

REM 檢查虛擬環境
if not exist "venv" (
    echo 📦 創建虛擬環境...
    python -m venv venv
)

REM 激活虛擬環境
echo 🔧 激活虛擬環境...
call venv\Scripts\activate.bat

REM 安裝依賴
echo 📚 安裝依賴套件...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM 檢查環境變數
echo ⚙️ 檢查環境配置...

REM 從父目錄讀取環境變數（如果存在）
if exist "..\\.env" (
    echo ✅ 已找到環境變數文件
) else (
    echo ⚠️ 未找到 .env 文件，將使用演示模式
)

REM 創建必要目錄
if not exist "reports" mkdir reports

REM 啟動應用
echo 🎉 啟動 AIO 分析器本地預覽...
echo.
echo 📱 請在瀏覽器中訪問: http://localhost:5000
echo 💡 使用 Ctrl+C 停止服務
echo.

REM 啟動 Flask 應用
python app.py

pause
