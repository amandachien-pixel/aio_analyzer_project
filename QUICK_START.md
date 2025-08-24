# 🚀 AIO 分析器快速入門指南

歡迎使用 AIO 潛力分析器！本指南將幫助您在 5 分鐘內快速設定並開始使用。

## 📋 快速設定檢查清單

- [ ] **第一步**: 執行快速設定腳本
- [ ] **第二步**: 設定 API 憑證
- [ ] **第三步**: 測試 API 連接
- [ ] **第四步**: 啟動應用

## 🏃‍♂️ 方法一：超快速設定（推薦新手）

### 1️⃣ 一鍵安裝所有依賴

```bash
./quick_setup.sh
```

這個腳本會自動：
- ✅ 檢查系統需求
- ✅ 安裝 Python 依賴
- ✅ 創建配置結構
- ✅ 生成環境變數範例
- ✅ 設置檔案權限

### 2️⃣ 互動式 API 設定

```bash
python3 setup_apis.py
```

這個助手會引導您：
- 🔑 設定 Google Search Console API
- 🎯 設定 Google Ads API
- 🔍 設定 Serper API
- ⚙️ 生成完整的環境配置

### 3️⃣ 驗證 API 連接

```bash
python3 test_apis.py
```

### 4️⃣ 啟動應用

```bash
# 本地預覽版（簡單易用）
python3 local_preview/app_simple.py

# 完整企業版
cd backend && python3 manage.py runserver
```

---

## ⚡ 方法二：立即體驗（演示模式）

如果您想先體驗功能，可以直接啟動演示模式：

```bash
# 確保在項目根目錄
cd /Users/AmandaChien/aio_analyzer_project

# 啟動演示版本
python3 local_preview/app_simple.py
```

然後訪問：**http://localhost:5001**

> 💡 演示模式使用模擬數據，無需 API 憑證即可體驗完整流程。

---

## 🔧 方法三：手動設定（進階用戶）

### 步驟 1: 安裝依賴

```bash
pip3 install flask pandas numpy pyyaml python-dotenv aiohttp
pip3 install google-api-python-client google-auth google-ads
```

### 步驟 2: 配置 API 憑證

#### Google Search Console API
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建專案並啟用 Search Console API
3. 創建服務帳戶並下載 JSON 憑證
4. 將憑證儲存為 `config/credentials.json`

#### Google Ads API
1. 申請 [Google Ads API](https://developers.google.com/google-ads/api/) 存取權限
2. 創建 OAuth 憑證並獲取 refresh_token
3. 配置 `config/google-ads.yaml`

#### Serper API
1. 註冊 [Serper.dev](https://serper.dev/) 帳戶
2. 獲取 API 金鑰
3. 設定環境變數 `SERP_API_KEY`

### 步驟 3: 創建環境配置

```bash
cp backend/env.example .env
# 編輯 .env 填入您的 API 憑證
```

### 步驟 4: 測試與啟動

```bash
python3 test_apis.py
python3 local_preview/app_simple.py
```

---

## 🧪 API 測試工具

### 快速測試 Serper API

```bash
# 設定 API 金鑰
export SERP_API_KEY=your-api-key

# 執行簡單測試
python3 examples/test_serper_simple.py
```

### 完整 API 測試

```bash
# 測試所有 API
python3 test_apis.py
```

---

## 🌟 使用體驗

### 本地預覽版特色
- 🎯 **MCP 邏輯架構**: 模組化的分析流程
- 💻 **簡明易用 UI**: 現代化響應式介面
- 📊 **實時進度追蹤**: 清楚的步驟指示器
- 🎭 **雙模式支援**: 演示模式 + 真實數據模式

### 分析流程
1. **M1: GSC 數據擷取** - 從 Search Console 獲取種子關鍵字
2. **M2: 關鍵字擴展** - 使用 Google Ads API 擴展關鍵字
3. **M3: AIO 驗證** - 使用 Serper API 檢測 AI Overview
4. **M4: 報告生成** - 生成 CSV 格式的分析報告

---

## 🚨 常見問題

### Q: 收到 "403 Forbidden" 錯誤
**A**: 檢查服務帳戶是否已添加到 Search Console 權限中

### Q: Google Ads API 連接失敗
**A**: 確認開發者權杖已獲核准且 OAuth 授權已完成

### Q: Serper API 查詢失敗
**A**: 檢查 API 金鑰是否正確且查詢額度充足

### Q: 端口被佔用
**A**: 使用不同端口：`python3 app.py --port 5002`

---

## 📚 進階功能

### 企業版功能（Django 後端）
- 👥 **多用戶管理**: 完整的用戶系統
- 🗄️ **數據持久化**: PostgreSQL 數據庫
- ⚡ **異步處理**: Celery 任務隊列
- 📊 **API 文檔**: Swagger UI
- 🐳 **容器部署**: Docker + Docker Compose

### 啟動企業版
```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver
```

---

## 🔗 重要連結

| 服務 | 連結 | 說明 |
|------|------|------|
| **Google Cloud Console** | https://console.cloud.google.com/ | 設定 GSC 和 Ads API |
| **Google Search Console** | https://search.google.com/search-console/ | 管理網站權限 |
| **Google Ads API** | https://ads.google.com/nav/selectaccount | 申請開發者權杖 |
| **Serper.dev** | https://serper.dev/ | 註冊並獲取 API 金鑰 |

---

## 📞 支援與回饋

### 獲取幫助
- 📖 **詳細設定指南**: `API_SETUP_GUIDE.md`
- 🧪 **測試工具**: `python3 test_apis.py`
- 💡 **示例腳本**: `examples/` 目錄

### 故障排除步驟
1. 檢查 Python 版本（需要 3.8+）
2. 確認所有依賴已安裝
3. 驗證 API 憑證配置
4. 查看終端錯誤訊息

---

## 🎯 下一步建議

### 新手用戶
1. ✅ 先使用演示模式熟悉介面
2. ✅ 設定一個 API（如 Serper）測試真實數據
3. ✅ 逐步添加其他 API 獲得完整功能

### 進階用戶
1. ✅ 部署企業版獲得所有功能
2. ✅ 設定監控和警報
3. ✅ 客製化分析參數
4. ✅ 整合到現有工作流程

---

🎉 **準備好開始您的 AIO 分析之旅了嗎？**

選擇上面任一種方法開始設定，或直接啟動演示模式體驗功能！
